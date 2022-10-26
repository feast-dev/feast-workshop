{{ 
  config(
    materialized='incremental',
    file_format='parquet',
    incremental_strategy='append'
  ) 
}}

SELECT * 
FROM 
  (
    SELECT 
      user_id,
      to_timestamp(timestamp) AS timestamp,
      SUM(amt) OVER (
        PARTITION BY user_id
        ORDER BY to_timestamp(timestamp)
        RANGE BETWEEN INTERVAL 1 day PRECEDING AND CURRENT ROW
      ) AS amt_sum_1d_10m,
      AVG(amt) OVER (
        PARTITION BY user_id
        ORDER BY to_timestamp(timestamp)
        RANGE BETWEEN INTERVAL 1 day PRECEDING AND CURRENT ROW
      ) AS amt_mean_1d_10m
    FROM demo_fraud_v2.transactions
    {% if is_incremental() %}
    WHERE
      partition_0 BETWEEN date_format({{ prev_day_partition() }}, "yyyy") AND date_format({{ next_day_partition() }}, "yyyy") AND
      partition_1 BETWEEN date_format({{ prev_day_partition() }}, "MM") AND date_format({{ next_day_partition() }}, "MM") AND
      partition_2 BETWEEN date_format({{ prev_day_partition() }}, "dd") AND date_format({{ next_day_partition() }}, "dd")
    {% else %}
    -- Hack to simulate we started on 2021-06-01
    WHERE
      partition_0 = "2022" AND
      partition_1 = "04" AND
      partition_2 = "20"
    {% endif %}
  )
{% if is_incremental() %} 
-- Need to only produce values in this window
WHERE timestamp > (SELECT MAX(timestamp) FROM {{ this }})
{% endif %}