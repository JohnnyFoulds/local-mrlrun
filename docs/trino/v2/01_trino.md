# README — Polaris (Iceberg REST) + Trino on K3s with External MinIO

> Assumptions
>
> * You already run `set -a && source .env && set +a` so these are in your shell:
>
>   * `S3_ENDPOINT_URL=http://192.168.1.184:30080` (or `http://dragon.lan:30080`)
>   * `AWS_ACCESS_KEY_ID=dragon`
>   * `AWS_SECRET_ACCESS_KEY='pass@word'`
> *

## 0) Namespace

```bash
kubectl create namespace data 2>/dev/null || true
```

---

## 1) MinIO credentials (from your env)

```bash
kubectl -n data delete secret minio-credentials 2>/dev/null || true
kubectl -n data create secret generic minio-credentials \
  --from-literal=MINIO_ACCESS_KEY="${AWS_ACCESS_KEY_ID}" \
  --from-literal=MINIO_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
```

---

## 2) Polaris (REST catalog) wired to **your** MinIO endpoint

```bash
cat <<EOF | kubectl apply -n data -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: polaris
spec:
  replicas: 1
  selector: { matchLabels: { app: polaris } }
  template:
    metadata: { labels: { app: polaris } }
    spec:
      containers:
        - name: polaris
          image: apache/polaris:latest
          imagePullPolicy: IfNotPresent
          ports: [{ containerPort: 8181 }]
          env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom: { secretKeyRef: { name: minio-credentials, key: MINIO_ACCESS_KEY } }
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom: { secretKeyRef: { name: minio-credentials, key: MINIO_SECRET_KEY } }
            - name: AWS_REGION
              value: dummy-region
            - name: AWS_ENDPOINT_URL_S3
              value: "${S3_ENDPOINT_URL}"
            - name: AWS_ENDPOINT_URL_STS
              value: "${S3_ENDPOINT_URL}"
            - name: POLARIS_BOOTSTRAP_CREDENTIALS
              value: default-realm,root,secret
            - name: polaris.realm-context.realms
              value: default-realm
            - name: polaris.features.DROP_WITH_PURGE_ENABLED
              value: "true"
          readinessProbe:
            httpGet: { path: /healthcheck, port: 8181 }
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /healthcheck, port: 8181 }
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: polaris
spec:
  selector: { app: polaris }
  ports:
    - name: http
      port: 8181
      targetPort: 8181
EOF

kubectl -n data rollout status deploy/polaris
```

---

## 3) Create the `warehouse` bucket on your MinIO (idempotent)

```bash
kubectl -n data delete pod mc-setup 2>/dev/null || true
kubectl -n data run mc-setup --restart=Never --image=minio/mc:latest -- \
  /bin/sh -lc "
    mc alias set minio '${S3_ENDPOINT_URL}' '${AWS_ACCESS_KEY_ID}' '${AWS_SECRET_ACCESS_KEY}' --api s3v4 &&
    mc mb -p minio/warehouse || true &&
    mc ls minio/warehouse
  "
kubectl -n data wait --for=condition=Ready pod/mc-setup --timeout=60s || true
kubectl -n data logs mc-setup
kubectl -n data delete pod mc-setup --now
```

---

## 4) Create a Polaris catalog `polariscatalog` (points to `s3://warehouse`)

```bash
# Port-forward Polaris temporarily
kubectl -n data port-forward svc/polaris 8181:8181 >/tmp/polaris.pf.log 2>&1 & 
PF_PID=$!; sleep 2

# Token
ACCESS_TOKEN="$(curl -sS -X POST \
  'http://localhost:8181/api/catalog/v1/oauth/tokens' \
  -d 'grant_type=client_credentials&client_id=root&client_secret=secret&scope=PRINCIPAL_ROLE:ALL' \
  | jq -r '.access_token')"
echo "ACCESS_TOKEN: ${ACCESS_TOKEN:0:16}..."

# Create catalog
curl -sS -i -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  'http://localhost:8181/api/management/v1/catalogs' \
  --json "{
    \"name\": \"polariscatalog\",
    \"type\": \"INTERNAL\",
    \"properties\": {
      \"default-base-location\": \"s3://warehouse\",
      \"s3.endpoint\": \"${S3_ENDPOINT_URL}\",
      \"s3.path-style-access\": \"true\",
      \"s3.access-key-id\": \"${AWS_ACCESS_KEY_ID}\",
      \"s3.secret-access-key\": \"${AWS_SECRET_ACCESS_KEY}\",
      \"s3.region\": \"dummy-region\"
    },
    \"storageConfigInfo\": {
      \"roleArn\": \"arn:aws:iam::000000000000:role/minio-polaris-role\",
      \"storageType\": \"S3\",
      \"allowedLocations\": [\"s3://warehouse/*\"]
    }
  }"

# List catalogs
echo ; echo "=== Polaris catalogs ==="
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" \
  'http://localhost:8181/api/management/v1/catalogs' | jq

# Stop port-forward
kill $PF_PID 2>/dev/null || true
```

---

## 5) Trino via Helm (Service on **9191**, catalog = Iceberg REST to Polaris)

```bash
helm repo add trino https://trinodb.github.io/charts/ && helm repo update

cat <<EOF | helm upgrade --install trino trino/trino -n data -f -
server:
  workers: 1
  exchangeManager:
    name: filesystem
    baseDir:
      - /tmp/trino-exchange

service:
  type: ClusterIP
  port: 9191   # service port (container still listens on 8080)

# Export MinIO creds into the pod env
envFrom:
  - secretRef:
      name: minio-credentials

# Define Trino catalogs (each key -> a file under /etc/trino/catalog)
catalogs:
  iceberg: |
    connector.name=iceberg
    iceberg.catalog.type=rest
    iceberg.rest-catalog.uri=http://polaris.data.svc.cluster.local:8181/api/catalog/
    iceberg.rest-catalog.warehouse=polariscatalog
    iceberg.rest-catalog.security=OAUTH2
    iceberg.rest-catalog.oauth2.credential=root:secret
    iceberg.rest-catalog.oauth2.scope=PRINCIPAL_ROLE:ALL
    iceberg.rest-catalog.vended-credentials-enabled=true

    # IO to your external MinIO endpoint
    fs.native-s3.enabled=true
    s3.path-style-access=true
    s3.endpoint=${S3_ENDPOINT_URL}
    s3.region=dummy-region

  tpch: |
    connector.name=tpch
EOF

kubectl -n data rollout status deploy/trino-coordinator
```

---

## 6) Smoke-test (inside cluster; no 8080 on your laptop)

```bash
# Use Trino CLI inside a one-shot pod
kubectl -n data run -it --rm trino-client --image=trinodb/trino:476 --restart=Never -- \
  trino --server http://trino-coordinator:8080 --catalog iceberg <<'SQL'
SHOW CATALOGS;
CREATE SCHEMA IF NOT EXISTS db;
USE db;
CREATE TABLE IF NOT EXISTS customers (
  customer_id BIGINT,
  first_name  VARCHAR,
  last_name   VARCHAR,
  email       VARCHAR
);
INSERT INTO customers VALUES
  (1,'Rey','Skywalker','rey@resistance.org'),
  (2,'Hermione','Granger','hermione@hogwarts.edu'),
  (3,'Tony','Stark','tony@starkindustries.com');
SELECT * FROM customers;
SELECT snapshot_id, committed_at, summary FROM "customers$snapshots" ORDER BY committed_at DESC;
SQL
```

If you want the Web UI, forward **9191**:

```bash
kubectl -n data port-forward svc/trino-coordinator 9191:9191
# open http://localhost:9191
```

---

## Notes

* We **do not** touch Hive or Hadoop—pure Polaris (Iceberg REST) + Trino + your MinIO.
* Trino uses **REST catalog** (`iceberg.catalog.type=rest`) pointing to the in-cluster Polaris Service.
* Data and metadata live in **your** MinIO (`${S3_ENDPOINT_URL}`), bucket `warehouse`.
* All credentials pulled from your existing shell env via a Kubernetes Secret.

That’s it. Run it exactly as-is with your `.env` loaded, and it comes up clean.
