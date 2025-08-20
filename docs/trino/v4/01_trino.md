# Polaris (Iceberg REST) + Trino on K3s with External MinIO

> Assumptions
> You ran: `set -a && source .env && set +a` with
>
> ```
> S3_ENDPOINT_URL=http://192.168.1.184:30080
> AWS_ACCESS_KEY_ID=dragon
> AWS_SECRET_ACCESS_KEY=pass@word
> ```

## 0) Create the namespace

```bash
echo $S3_ENDPOINT_URL
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

kubectl create namespace data
```

---

## 1) MinIO credentials (from your env)
```bash
kubectl -n data create secret generic minio-credentials \
  --from-literal=MINIO_ACCESS_KEY="${AWS_ACCESS_KEY_ID}" \
  --from-literal=MINIO_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
```

---

## 2) Polaris (REST catalog)

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
        - name: AWS_ACCESS_KEY_ID
          value: "${AWS_ACCESS_KEY_ID}" 
        - name: AWS_SECRET_ACCESS_KEY
          value: "${AWS_SECRET_ACCESS_KEY}" 
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

# Show logs, then clean up
kubectl -n data logs -f job/mc-setup
kubectl -n data delete job mc-setup
```

---

### 3.1) Create a new job specifically to add the STS policy

Just use the `minio` default credentials, I don't have unlimited time to figure this out with another access key.

---

## 4) Create a Polaris catalog `main`
```bash
# Port-forward Polaris temporarily
kubectl -n data port-forward svc/polaris 8181:8181 >/tmp/polaris.pf.log 2>&1 & 
PF_PID=$!; sleep 3

# Get OAuth token
ACCESS_TOKEN=$(curl -s -X POST \
  'http://localhost:8181/api/catalog/v1/oauth/tokens' \
  -d 'grant_type=client_credentials&client_id=root&client_secret=secret&scope=PRINCIPAL_ROLE:ALL' \
  | jq -r '.access_token')
echo "ACCESS_TOKEN: ${ACCESS_TOKEN:0:16}..."

# Create the catalog using a clean JSON payload
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


# Create a catalog admin role
curl -X PUT http://localhost:8181/api/management/v1/catalogs/main/catalog-roles/catalog_admin/grants \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  --json '{"grant":{"type":"catalog", "privilege":"CATALOG_MANAGE_CONTENT"}}'

# Create a data engineer role
curl -X POST http://localhost:8181/api/management/v1/principal-roles \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  --json '{"principalRole":{"name":"data_engineer"}}'

# Connect the roles
curl -X PUT http://localhost:8181/api/management/v1/principal-roles/data_engineer/catalog-roles/main \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  --json '{"catalogRole":{"name":"catalog_admin"}}'

# Give root the data engineer role
curl -X PUT http://localhost:8181/api/management/v1/principals/root/principal-roles \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  --json '{"principalRole": {"name":"data_engineer"}}'

# Check that the role was correctly assigned to the root principal:
curl -X GET http://localhost:8181/api/management/v1/principals/root/principal-roles -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# Stop port-forward
kill $PF_PID
```

---

## 5) Install Trino (Helm) with All Corrections

```bash
# Add and update the Trino Helm repository
helm repo add trino https://trinodb.github.io/charts/ && helm repo update

# Deploy Trino with a custom configuration values file piped via stdin
cat <<EOF | helm upgrade --install trino trino/trino -n data -f -
server:
  workers: 1
service:
  type: LoadBalancer
  port: 9191
catalogs:
  iceberg: |
    connector.name=iceberg
    iceberg.catalog.type=rest
    iceberg.rest-catalog.uri=http://polaris.data.svc.cluster.local:8181/api/catalog/
    iceberg.rest-catalog.warehouse=main
    iceberg.rest-catalog.vended-credentials-enabled=false
    iceberg.rest-catalog.security=OAUTH2
    iceberg.rest-catalog.oauth2.credential=root:secret
    iceberg.rest-catalog.oauth2.scope=PRINCIPAL_ROLE:ALL

    # Explicitly enable the register_table procedure
    iceberg.register-table-procedure.enabled=true
    iceberg.add-files-procedure.enabled=true

    # required for Trino to read from/write to S3
    fs.native-s3.enabled=true
    s3.endpoint=${S3_ENDPOINT_URL}
    s3.aws-access-key=${AWS_ACCESS_KEY_ID}
    s3.aws-secret-key=${AWS_SECRET_ACCESS_KEY}
    s3.region=dummy-region

  tpch: |
    connector.name=tpch
EOF

kubectl -n data rollout status deploy/trino-coordinator
kubectl -n data get svc trino
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
SQL
```