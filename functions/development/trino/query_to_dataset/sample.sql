SELECT
    *
FROM
    "iceberg"."lakehouse"."taxi_trips"
WHERE
    CAST(trip_start_timestamp AS DATE) BETWEEN
        (CAST('2023-05-01' AS DATE) - INTERVAL '3' MONTH) AND
        (CAST('2023-05-01' AS DATE) - INTERVAL '2' MONTH)