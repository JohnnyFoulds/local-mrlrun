# Register Table : Chicago Taxi Trips

## Connect to the Trino CLI

```bash
kubectl -n data run -it --rm trino-client --image=trinodb/trino:476 --restart=Never -- \
  trino --server http://trino.data.svc.cluster.local:9191 --catalog iceberg
```

## Run the SQL Commands

```sql
-- Step 1: Create a schema (like a database) to hold your tables.
CREATE SCHEMA IF NOT EXISTS lakehouse;

-- Step 2: Use the register_table procedure to create the metadata for your existing files.
-- This tells Iceberg to create a table named 'taxi_trips' in the 'lakehouse' schema,
-- located at your data path in MinIO.
CALL iceberg.system.register_table(
    schema_name => 'lakehouse',
    table_name => 'taxi_trips',
    table_location => 's3://warehouse/lake/taxi_trips/'
);

-- Step 3: Verify that the table was created and the schema was inferred correctly.
DESCRIBE lakehouse.taxi_trips;

-- Step 4: Run your first queries!
-- Count the total number of records across all files.
SELECT count(*) FROM lakehouse.taxi_trips;

-- See a sample of the data.
SELECT 
    unique_key,
    trip_start_timestamp,
    trip_end_timestamp,
    trip_miles,
    fare
FROM lakehouse.taxi_trips 
LIMIT 10;
```