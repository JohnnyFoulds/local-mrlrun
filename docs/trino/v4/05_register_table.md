# Register Table : Chicago Taxi Trips

## Connect to the Trino CLI

```bash
kubectl -n data run -it --rm trino-client --image=trinodb/trino:476 --restart=Never -- \
  trino --server http://trino.data.svc.cluster.local:9191 --catalog iceberg
```

## Run the SQL Commands

```sql
-- Step 1: Create a schema (like a database) to hold your tables.
CREATE SCHEMA IF NOT EXISTS lakehouse
WITH (location = 's3://warehouse/lake/');

-- Step 2: Create the table
CREATE TABLE IF NOT EXISTS lakehouse.taxi_trips (
    unique_key              VARCHAR      NOT NULL,  -- STRING REQUIRED
    taxi_id                 VARCHAR      NOT NULL,  -- STRING REQUIRED
    trip_start_timestamp    TIMESTAMP(3),           -- BigQuery TIMESTAMP (see note)
    trip_end_timestamp      TIMESTAMP(3),
    trip_seconds            INTEGER,
    trip_miles              DOUBLE,                 -- FLOAT64 → DOUBLE
    pickup_census_tract     BIGINT,
    dropoff_census_tract    BIGINT,
    pickup_community_area   INTEGER,
    dropoff_community_area  INTEGER,
    fare                    DOUBLE,
    tips                    DOUBLE,
    tolls                   DOUBLE,
    extras                  DOUBLE,
    trip_total              DOUBLE,
    payment_type            VARCHAR,
    company                 VARCHAR,
    pickup_latitude         DOUBLE,
    pickup_longitude        DOUBLE,
    pickup_location         VARCHAR,
    dropoff_latitude        DOUBLE,
    dropoff_longitude       DOUBLE,
    dropoff_location        VARCHAR
);

-- Step 3: Verify that the table was created and the schema is correct.
DESCRIBE lakehouse.taxi_trips;

-- Step 4: Attach the existing parquet files (no rewrite)
ALTER TABLE lakehouse.taxi_trips
EXECUTE add_files(
    location => 's3://warehouse/lake/taxi_trips/',
    format   => 'PARQUET'
);

-- Step 5: Run your first queries!
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

-- see files
SELECT * FROM lakehouse."taxi_trips$files" LIMIT 20;
```
