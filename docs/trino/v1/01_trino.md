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
# load environment variables
set -a && source .env && set +a

kubectl create namespace data 
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
  --from-literal=MINIO_ACCESS_KEY='dragon' \
  --from-literal=MINIO_SECRET_KEY='pass@word' \
  2>/dev/null || true
```

## 5. Install Trino with Iceberg (Nessie)

First, create a **ConfigMap** that defines the Iceberg catalog configuration pointing to Nessie and MinIO:

```bash
cat <<'EOF' | kubectl -n data apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: trino-catalog-iceberg
  labels:
    app.kubernetes.io/component: catalog
    app.kubernetes.io/instance: trino
data:
  iceberg.properties: |
    connector.name=iceberg
    iceberg.catalog.type=nessie
    iceberg.nessie-catalog.uri=http://nessie.data.svc.cluster.local:19120/api/v2

    # MinIO / S3
    fs.native-s3.enabled=true
    s3.endpoint=http://minio-service.mlrun.svc.cluster.local:9000
    s3.path-style-access=true
    s3.aws-access-key=${ENV:AWS_ACCESS_KEY_ID}
    s3.aws-secret-key=${ENV:AWS_SECRET_ACCESS_KEY}
EOF
```

Now install Trino via Helm, mounting the catalog ConfigMap and exposing it on **9090** (not 8080):

```bash
helm repo add trino https://trinodb.github.io/charts
helm repo update

cat <<'EOF' | helm upgrade --install trino trino/trino -n data -f -
server:
  workers: 1
  exchangeManager:
    name: filesystem
    baseDir:
      - /tmp/trino-exchange

service:
  port: 9090

# Mount MinIO creds so catalog can reference ${ENV:...}
envFrom:
  - secretRef:
      name: minio-credentials

# Define the Iceberg catalog (Nessie) correctly.
# NOTE: default-warehouse-dir is REQUIRED by Trino’s Nessie integration.
# See Trino+Nessie sample in official docs. :contentReference[oaicite:0]{index=0}
catalogs:
  iceberg: |
    connector.name=iceberg
    iceberg.catalog.type=nessie
    iceberg.nessie-catalog.uri=http://nessie.data.svc.cluster.local:19120/api/v2
    iceberg.nessie-catalog.ref=main
    iceberg.nessie-catalog.default-warehouse-dir=s3://iceberg-warehouse   # <-- choose/ensure this bucket exists

    # S3/MinIO
    fs.native-s3.enabled=true
    s3.endpoint=http://minio-service.mlrun.svc.cluster.local:9000
    s3.path-style-access=true
    s3.ssl.enabled=false
    s3.aws-access-key=${ENV:MINIO_ACCESS_KEY}
    s3.aws-secret-key=${ENV:MINIO_SECRET_KEY}
EOF

kubectl -n data rollout status deploy/trino-coordinator
```

---

## 6. Verify with Trino CLI

Forward Trino locally on **9090**:

```bash
kubectl -n data port-forward svc/trino 9090:9090
```

Download the Trino CLI:

```bash
curl -LO https://repo1.maven.org/maven2/io/trino/trino-cli/476/trino-cli-476-executable.jar
chmod +x trino-cli-476-executable.jar
```

Run a quick smoke test:

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

✅ At this point, Trino is correctly wired to Iceberg (via Nessie) and MinIO.
Next step (Step 7) will be to ingest the Chicago Taxi dataset.

---

Do you want me to go ahead and extend the README with **Step 7: Load Chicago Taxi dataset into Iceberg/MinIO**, so you can run queries immediately after this infra is up?
