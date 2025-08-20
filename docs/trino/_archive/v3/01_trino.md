# README — Polaris (Iceberg REST) + Trino on K3s with External MinIO (no probes)

> Assumptions
> You ran: `set -a && source .env && set +a` with
>
> ```
> S3_ENDPOINT_URL=http://192.168.1.184:30080  # or http://dragon.lan:30080
> AWS_ACCESS_KEY_ID=dragon
> AWS_SECRET_ACCESS_KEY=pass@word
> ```

## 0) Reset namespace & old resources

```bash
kubectl create namespace data 2>/dev/null || true
```

---

## 1) MinIO credentials (from your env)

```bash
kubectl -n data create secret generic minio-credentials \
  --from-literal=MINIO_ACCESS_KEY="${AWS_ACCESS_KEY_ID}" \
  --from-literal=MINIO_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
```

---

## 2) Polaris (REST catalog) wired to **your** MinIO endpoint

*(no liveness/readiness probes at all)*

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
    metadata:
      labels: { app: polaris }
    spec:
      containers:
      - name: polaris
        image: apache/polaris:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8181
        env:
        # Minimal bootstrap and realm config ONLY
        - name: POLARIS_BOOTSTRAP_CREDENTIALS
          value: default-realm,root,secret
        - name: polaris.realm-context.realms
          value: default-realm
        - name: polaris.realm-context.default-realm
          value: default-realm
---
apiVersion: v1
kind: Service
metadata:
  name: polaris
spec:
  type: ClusterIP
  selector: { app: polaris }
  ports:
  - name: api
    port: 8181
    targetPort: 8181
EOF

kubectl -n data rollout status deploy/polaris
```

---

## 3) Create the `warehouse` bucket on your MinIO (idempotent)

```bash
# Clean any previous helper pod
kubectl -n data delete pod mc-setup 2>/dev/null || true

cat <<EOF | kubectl apply -n data -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: mc-setup
  namespace: data
spec:
  template:
    spec: # This is the PodSpec
      containers:
      - name: mc-setup
        image: alpine:3.20
        envFrom: # <-- CORRECT: envFrom is a child of the container
          - secretRef:
              name: minio-credentials
        command: ["/bin/sh", "-c"]
        args:
          - |
            set -e
            set -x # Prints each command before executing it (great for debugging)

            echo "INFO: Installing dependencies..."
            apk add curl

            echo "INFO: Downloading mc client..."
            curl -L -o /usr/local/bin/mc https://dl.min.io/client/mc/release/linux-amd64/mc
            chmod +x /usr/local/bin/mc
            mc --version

            echo "INFO: Setting up MinIO alias..."
            mc alias set minio "${S3_ENDPOINT_URL}" "${AWS_ACCESS_KEY_ID}" "${AWS_SECRET_ACCESS_KEY}" --api s3v4

            echo "INFO: Creating MinIO warehouse bucket if it doesn't exist..."
            mc mb -p minio/warehouse || true

            echo "INFO: Verifying bucket exists..."
            mc ls minio/warehouse

            echo "SUCCESS: MinIO setup complete."
      restartPolicy: Never
  backoffLimit: 1 # Optional: How many times to retry the job if it fails
EOF

# Wait until the pod is Ready (it sleeps briefly at the end so it can flip Ready)
kubectl -n data wait --for=condition=complete job/mc-setup --timeout=120s

# Show logs, then clean up
kubectl -n data logs -f job/mc-setup
kubectl -n data delete job mc-setup
```

---

## 4) Create a Polaris catalog `main` (points to `s3://warehouse`)

```bash
# Port-forward Polaris temporarily
kubectl -n data port-forward svc/polaris 8181:8181 >/tmp/polaris.pf.log 2>&1 & 
PF_PID=$!; sleep 2

# Get OAuth token
ACCESS_TOKEN=$(curl -s -X POST \
  'http://localhost:8181/api/catalog/v1/oauth/tokens' \
  -d 'grant_type=client_credentials&client_id=root&client_secret=secret&scope=PRINCIPAL_ROLE:ALL' \
  | jq -r '.access_token')
echo "ACCESS_TOKEN: ${ACCESS_TOKEN:0:16}..."

# Create the catalog with the corrected payload (no wildcard in allowedLocations)
# We expect an 'HTTP/1.1 201 Created' or 'HTTP/1.1 200 OK' response
curl -i -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  'http://localhost:8181/api/management/v1/catalogs' \
  -d @- <<EOF
{
  "name": "main",
  "type": "INTERNAL",
  "properties": {
    "default-base-location": "s3://warehouse/",
    "s3.endpoint": "${S3_ENDPOINT_URL}",
    "s3.path-style-access": "true",
    "s3.access-key-id": "${AWS_ACCESS_KEY_ID}",
    "s3.secret-access-key": "${AWS_SECRET_ACCESS_KEY}",
    "s3.region": "dummy-region"
  },
  "storageConfigInfo": {
    "roleArn": "arn:aws:iam::000000000000:role/minio-polaris-role",
    "storageType": "S3",
    "allowedLocations": ["s3://warehouse/"]
  }
}
EOF

# List catalogs to verify it was created
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  'http://localhost:8181/api/management/v1/catalogs' | jq

# Stop port-forward
kill $PF_PID
```

---

## 5) Install Trino (Helm), service on **9191**, Iceberg REST to Polaris

```bash
# 1. Add and update the Trino Helm repository
helm repo add trino https://trinodb.github.io/charts/ && helm repo update

# 2. Deploy Trino with a custom configuration values file piped via stdin
cat <<EOF | helm upgrade --install trino trino/trino -n data -f -
server:
  workers: 1
  exchangeManager:
    name: filesystem
    baseDir: /tmp/trino-exchange
service:
  type: ClusterIP
  port: 9191
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

    fs.native-s3.enabled=true
    s3.path-style-access=true
    s3.endpoint=${S3_ENDPOINT_URL}
    s3.region=dummy-region
    s3.aws-access-key=${AWS_ACCESS_KEY_ID}
    s3.aws-secret-key=${AWS_SECRET_ACCESS_KEY}

  tpch: |
    connector.name=tpch
EOF

kubectl -n data rollout status deploy/trino-coordinator
```

---

## 6) Smoke-test via Trino CLI (inside cluster)

An interactive test, for example run `SHOW CATALOGS`.

```bash
kubectl -n data run -it --rm trino-client --image=trinodb/trino:476 --restart=Never -- \
  trino --server http://trino.data.svc.cluster.local:9191 --catalog iceberg
```

Proper test:

> I am not going to battle now to get this working, just use interactive with these commands.

```bash
kubectl -n data run -it --rm trino-client --image=trinodb/trino:476 --restart=Never -- \
  trino --server http://trino.data.svc.cluster.local:9191 --catalog iceberg <<'SQL'
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

(Optional) Web UI:

```bash
kubectl -n data port-forward svc/trino-coordinator 9191:9191
# open http://localhost:9191
```

---

### Notes

* **No health checks**: Polaris pod will not flap due to probe endpoints.
* **No Hive/Hadoop**: pure Polaris REST + Trino Iceberg with your external MinIO.
* **Credentials**: expanded from your shell into both Polaris env and Trino catalog.
* **Networking**: Trino talks to Polaris via `polaris.data.svc.cluster.local:8181` and to MinIO at `${S3_ENDPOINT_URL}`.

If anything still trips, paste the **first 100 lines** of:

```
kubectl -n data logs deploy/polaris --tail=200
kubectl -n data logs deploy/trino-coordinator --tail=200
```

and I’ll adjust this README **surgically**.
