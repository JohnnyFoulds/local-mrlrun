SELECT
    *
FROM
    "{{ catalog }}"."{{ schema }}"."{{ source_table }}"
WHERE
    CAST({{ filter_column }} AS DATE) BETWEEN
        (CAST('{{ filter_start_value }}' AS DATE) - INTERVAL '3' MONTH) AND
        (CAST('{{ filter_start_value }}' AS DATE) - INTERVAL '2' MONTH)