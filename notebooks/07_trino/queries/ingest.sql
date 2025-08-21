WITH filtered_data AS (
    SELECT
        *
    FROM
        "{{ catalog }}"."{{ schema }}"."{{ source_table }}"
    WHERE
        -- Trino uses CAST(... AS DATE) and the standard subtraction operator for intervals
        CAST({{ filter_column }} AS DATE) BETWEEN
            (CAST('{{ filter_start_value }}' AS DATE) - INTERVAL '3' MONTH) AND
            (CAST('{{ filter_start_value }}' AS DATE) - INTERVAL '2' MONTH)
)

, mean_time AS (
    SELECT
        -- Trino's equivalent of INT64 is BIGINT
        CAST(AVG(trip_seconds) AS BIGINT) AS avg_trip_seconds
    FROM
        filtered_data
)

SELECT
    -- Function names for date/time extraction are slightly different
    CAST(day_of_week(trip_start_timestamp) AS DOUBLE) AS dayofweek, -- Note: Sunday=7 in Trino
    CAST(hour(trip_start_timestamp) AS DOUBLE) AS hourofday,
    
    -- Geospatial functions use a different syntax
    ST_Distance(
        to_spherical_geography(ST_Point(pickup_longitude, pickup_latitude)),
        to_spherical_geography(ST_Point(dropoff_longitude, dropoff_latitude))
    ) AS trip_distance,
    
    trip_miles,
    
    -- Trino's equivalent of FLOAT64 is DOUBLE
    CAST(
        CASE
            WHEN trip_seconds IS NULL THEN m.avg_trip_seconds
            WHEN trip_seconds <= 0 THEN m.avg_trip_seconds
            ELSE trip_seconds
        END AS DOUBLE
    ) AS trip_seconds,
    
    payment_type,
    company,
    
    -- Use double quotes for identifiers if needed, not backticks
    (fare + tips + tolls + extras) AS "{{ target_column }}"
FROM
    filtered_data AS t
-- Explicit CROSS JOIN is clearer than a comma
CROSS JOIN mean_time AS m
WHERE
    trip_miles > 0 AND fare > 0 AND fare < 1500
    -- The Jinja templating part does not need to change at all
    {% for field in ["fare", "trip_start_timestamp", "pickup_longitude",
                "pickup_latitude", "dropoff_longitude", "dropoff_latitude", "payment_type", "company"] %}
        AND "{{ field }}" IS NOT NULL
    {% endfor %}