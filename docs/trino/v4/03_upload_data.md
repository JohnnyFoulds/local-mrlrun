# Upload Data Taxi Data

Upload the data to the s3 store.

```bash
# load environment variables
set -a && source .env && set +a
```

## MinIO Client

### Install MinIO Client

```bash
sudo curl -L -o /usr/local/bin/mc https://dl.min.io/client/mc/release/linux-amd64/mc
sudo chmod +x /usr/local/bin/mc
mc --version
```

### Set MinIO Alias

```bash
mc alias set minio "${S3_ENDPOINT_URL}" "${AWS_ACCESS_KEY_ID}" "${AWS_SECRET_ACCESS_KEY}" --api s3v4
```

## Upload Data

```bash
SOURCE_PATH=/data/data/taxi_trips/
DESTINATION_PATH=minio/warehouse/lake/taxi_trips/

# upload the data
mc cp -r "${SOURCE_PATH}" "${DESTINATION_PATH}"

# list the contents
mc ls "${DESTINATION_PATH}"
```
