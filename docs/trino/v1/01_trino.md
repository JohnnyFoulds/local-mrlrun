Got it. Let’s rewrite your README in the **simplest correct form**, cutting Hive entirely (since it’s been a nightmare) and using the modern, supported **Iceberg REST catalog (Project Nessie)** with Trino + MinIO. Everything is inline `kubectl`/`helm`/`cat <<EOF` so you can copy-paste.

---

# 🚀 Minimal Trino + Iceberg + MinIO + Nessie on K3s

This guide installs **Trino** with **Iceberg** backed by **MinIO** (from your existing `mlrun` namespace).
Instead of Hive Metastore, we use the modern **Project Nessie REST catalog** + Postgres for metadata.

---

## 0. Prerequisites

* K3s cluster with `kubectl` and `helm` configured.
* MinIO already running in namespace `mlrun`.
  Service assumed: `minio-service.mlrun.svc.cluster.local:9000`
* MinIO credentials available.

---

## 1. Create a Namespace

```bash
kubectl create namespace data || true
```

---

## 2. Install Postgres for Nessie Metadata

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install hms-pg bitnami/postgresql -n data \
  --set auth.username=nessie \
  --set auth.password=nessiepass \
  --set auth.database=nessiedb
kubectl -n data rollout status statefulset/hms-pg-postgresql
```

---

## 3. Deploy Project Nessie (Iceberg REST Catalog)

```bash
cat <<'EOF' | kubectl apply -n data -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: nessie-env
data:
  QUARKUS_HTTP_PORT: "19120"
  NESSIE_VERSION_STORE_TYPE: "JDBC"
  QUARKUS_DATASOURCE_JDBC_URL: "jdbc:postgresql://hms-pg-postgresql.data.svc.cluster.local:5432/nessiedb"
  QUARKUS_DATASOURCE_USERNAME: "nessie"
  QUARKUS_DATASOURCE_PASSWORD: "nessiepass"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nessie
spec:
  replicas: 1
  selector: { matchLabels: { app: nessie } }
  template:
    metadata: { labels: { app: nessie } }
    spec:
      containers:
        - name: nessie
          image: ghcr.io/projectnessie/nessie:latest
          ports: [{ containerPort: 19120, name: http }]
          envFrom: [{ configMapRef: { name: nessie-env } }]
---
apiVersion: v1
kind: Service
metadata:
  name: nessie
spec:
  selector: { app: nessie }
  ports:
    - name: http
      port: 19120
      targetPort: 19120
EOF

kubectl -n data rollout status deploy/nessie
```

---

## 4. Store MinIO Credentials

```bash
kubectl -n data create secret generic minio-credentials \
  --from-literal=MINIO_ACCESS_KEY='YOUR_MINIO_ACCESS_KEY' \
  --from-literal=MINIO_SECRET_KEY='YOUR_MINIO_SECRET_KEY' \
  2>/dev/null || true
```

---

## 5. Install Trino with Iceberg (Nessie)

```bash
helm repo add trino https://trinodb.github.io/charts
helm repo update

helm upgrade --install trino trino/trino -n data \
  --set server.workers=1 \
  --set service.port=9090 \
  --set envFrom[0].secretRef.name=minio-credentials \
  --set catalogs.iceberg="connector.name=iceberg\niceberg.catalog.type=nessie\niceberg.nessie-catalog.uri=http://nessie.data.svc.cluster.local:19120/api/v2\nfs.native-s3.enabled=true\ns3.endpoint=http://minio-service.mlrun.svc.cluster.local:9000\ns3.path-style-access=true\ns3.aws-access-key=\${ENV:MINIO_ACCESS_KEY}\ns3.aws-secret-key=\${ENV:MINIO_SECRET_KEY}"
kubectl -n data rollout status deploy/trino-coordinator
```

---

## 6. Verify with Trino CLI

Forward Trino locally on **9090**:

```bash
kubectl -n data port-forward svc/trino 9090:9090
```

Download Trino CLI:

```bash
curl -LO https://repo1.maven.org/maven2/io/trino/trino-cli/476/trino-cli-476-executable.jar
chmod +x trino-cli-476-executable.jar
```

Test:

```bash
./trino-cli-476-executable.jar --server http://localhost:9090 --catalog iceberg <<'SQL'
SHOW CATALOGS;
CREATE SCHEMA IF NOT EXISTS iceberg.demo;
CREATE TABLE IF NOT EXISTS iceberg.demo.smoke (id bigint, note varchar);
INSERT INTO iceberg.demo.smoke VALUES (1,'ok');
SELECT * FROM iceberg.demo.smoke;
SQL
```

Expected output:

```
 id | note 
----+------
  1 | ok
```

---

✅ You now have **Trino + Iceberg + MinIO** working with a modern **Nessie REST catalog** (no Hive pain).
Next step: ingest the Chicago Taxi dataset into MinIO/Iceberg and query it.

---

Do you want me to **append Step 7 with instructions for downloading the taxi dataset and loading it into Iceberg**, or keep the README strictly infra-only?
