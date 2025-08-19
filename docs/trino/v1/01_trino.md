# Trino + Iceberg on K3s (MinIO, **no Hive Derby**, **Postgres-backed HMS**)

This is the **simplest correct** setup to run SQL over **Iceberg tables** stored in **MinIO** from a **Trino** cluster on **K3s**, without using embedded Derby. Everything is copy-paste ready. You will:

* create a `data` namespace,
* install a tiny PostgreSQL for the Hive Metastore (HMS),
* run a **single-pod** Hive Metastore that talks to Postgres,
* install Trino and point its **Iceberg** catalog at HMS and MinIO,
* verify with a smoke test.

Assumptions:

* You already have **MinIO** running in namespace `mlrun` (from MLRun), reachable cluster-internally.
* You know your MinIO **service DNS**, **port**, **access key**, and **secret key**.

---

## 0) Namespace

```bash
kubectl create namespace data
```

---

## 1) PostgreSQL for Hive Metastore (tiny, single-pod)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install hms-pg bitnami/postgresql -n data \
  --set auth.username=hive \
  --set auth.password=hivepass \
  --set auth.database=metastore
```

Wait for it to be ready:

```bash
kubectl -n data rollout status statefulset/hms-pg-postgresql
```

Postgres DNS you’ll use below:

```
jdbc:postgresql://hms-pg-postgresql.data.svc.cluster.local:5432/metastore
```

---

## 2) Hive Metastore (single pod, backed by Postgres)

Create a ConfigMap with a minimal **hive-site.xml** and a Deployment+Service that starts the metastore on **9083**.

```bash
# Config for Hive Metastore (uses Postgres)
cat <<'EOF' | kubectl apply -n data -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hive-metastore
spec:
  replicas: 1
  selector: { matchLabels: { app: hive-metastore } }
  template:
    metadata: { labels: { app: hive-metastore } }
    spec:
      initContainers:
        - name: wait-for-postgres
          image: busybox:1.36
          command: ['sh','-c','until nc -z -w3 hms-pg-postgresql.data.svc.cluster.local 5432; do echo "waiting for postgres..."; sleep 2; done']
        - name: fetch-pg-driver
          image: curlimages/curl:8.8.0
          command: ['sh','-c']
          args:
            - |
              set -euo pipefail
              mkdir -p /aux-jars
              for URL in \
                "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar" \
                "https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar" \
                "https://jdbc.postgresql.org/download/postgresql-42.7.4.jar"
              do
                echo "Trying: $URL"
                if curl --fail --location --retry 5 --retry-delay 2 -o /aux-jars/postgresql.jar "$URL"; then break; fi
              done
              test -s /aux-jars/postgresql.jar || { echo "FATAL: could not fetch JDBC jar"; exit 2; }
          volumeMounts: [{ name: aux-jars, mountPath: /aux-jars }]
      containers:
        - name: metastore
          image: apache/hive:3.1.3
          imagePullPolicy: IfNotPresent
          env:
            - { name: HIVE_AUX_JARS_PATH, value: /aux-jars/postgresql.jar }
            - { name: HADOOP_CLASSPATH,   value: /aux-jars/postgresql.jar }
            - { name: HIVE_CONF_DIR,      value: /opt/hive/conf }
          command: ["/bin/bash","-lc"]
          args:
            - |
              set -e
              /opt/hive/bin/schematool \
                -dbType postgres \
                -driver org.postgresql.Driver \
                -userName hive \
                -passWord hivepass \
                -url jdbc:postgresql://hms-pg-postgresql.data.svc.cluster.local:5432/metastore \
                -initSchema -verbose || true
              exec /opt/hive/bin/hive --service metastore -p 9083
          ports: [{ name: thrift, containerPort: 9083 }]
          volumeMounts:
            - { name: hive-config, mountPath: /opt/hive/conf/hive-site.xml, subPath: hive-site.xml }
            - { name: aux-jars,    mountPath: /aux-jars }
          readinessProbe:
            tcpSocket: { port: thrift }
            initialDelaySeconds: 25
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 12
          livenessProbe:
            tcpSocket: { port: thrift }
            initialDelaySeconds: 90
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 6
      volumes:
        - name: hive-config
          configMap: { name: hive-metastore-config }
        - name: aux-jars
          emptyDir: {}
EOF
```

Verify it’s up:

```bash
kubectl -n data rollout status deploy/hive-metastore
```

Service DNS Trino will use:

```
thrift://hive-metastore.data.svc.cluster.local:9083
```

---

## 3) MinIO credentials (Secret → env vars for Trino)

```bash
kubectl -n data create secret generic minio-credentials \
  --from-literal=MINIO_ACCESS_KEY='YOUR_MINIO_ACCESS_KEY' \
  --from-literal=MINIO_SECRET_KEY='YOUR_MINIO_SECRET_KEY'
```

---

## 4) Trino (Helm) with **Iceberg** catalog → HMS + MinIO

Install Trino and inject:

* **filesystem exchange manager** (required),
* env vars from the Secret,
* an **Iceberg** catalog file that points to HMS and MinIO.

```bash
helm repo add trino https://trinodb.github.io/charts
helm repo update

helm install trino trino/trino -n data \
  --set server.workers=1 \
  --set server.exchangeManager.name=filesystem \
  --set server.exchangeManager.baseDir[0]=/tmp/trino-exchange \
  --set envFrom[0].secretRef.name=minio-credentials \
  --set catalogs.iceberg="connector.name=iceberg\niceberg.catalog.type=hive_metastore\nhive.metastore.uri=thrift://hive-metastore.data.svc.cluster.local:9083\nfs.native-s3.enabled=true\ns3.endpoint=http://minio-service.mlrun.svc.cluster.local:9000\ns3.path-style-access=true\ns3.aws-access-key=\${ENV:MINIO_ACCESS_KEY}\ns3.aws-secret-key=\${ENV:MINIO_SECRET_KEY}"
```

Wait for pods:

```bash
kubectl -n data get pods
kubectl -n data rollout status deploy/trino-coordinator
```

---

## 5) Smoke test (Trino CLI)

Port-forward Trino:

```bash
kubectl -n data port-forward svc/trino 8080:8080
```

Download CLI (one-liner; adjust version if needed):

```bash
curl -LO https://repo1.maven.org/maven2/io/trino/trino-cli/476/trino-cli-476-executable.jar
chmod +x trino-cli-476-executable.jar
```

Connect:

```bash
./trino-cli-476-executable.jar --server http://localhost:8080 --catalog iceberg
```

Run SQL:

```sql
-- Catalog should be visible
SHOW CATALOGS;

-- Create a schema in MinIO (this prepares for later data loads)
CREATE SCHEMA IF NOT EXISTS iceberg.demo
WITH (location = 's3a://lakehouse/demo/');

-- Minimal table to prove writes work end-to-end
CREATE TABLE iceberg.demo.smoke (id bigint, note varchar);
INSERT INTO iceberg.demo.smoke VALUES (1, 'ok');
SELECT * FROM iceberg.demo.smoke;
```

If you see `(1, ok)` returned, Trino ⇄ HMS ⇄ MinIO ⇄ Iceberg is wired correctly.

---

## Notes / Tweaks

* **MinIO service DNS:** replace `minio-service.mlrun.svc.cluster.local:9000` with your actual MinIO service/port.
* **Persistence:** This guide keeps HMS stateless (schema stored in Postgres) and Trino stateless. If you want durable local disks for Trino exchange, mount a PVC instead of `/tmp`.
* **Scaling:** Increase `server.workers` when needed; HMS can remain a single pod for most dev/POC loads.
* **Security:** For internal clusters, HTTP is acceptable. For TLS, terminate at an ingress and switch Trino to HTTPS accordingly.

You’re now ready for the **next step** (ingesting the taxi dataset into Iceberg tables on MinIO and querying them via Trino).
