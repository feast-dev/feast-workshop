{{ config(materialized='incremental') }}

-- Note: Snowflake does not support time range windows
SELECT *
FROM
  (SELECT
      USER_ID,
      t.TIMESTAMP as TIMESTAMP,
      "7D_AVG_AMT"
   FROM TRANSACTIONS t 
   CROSS JOIN LATERAL 
    (
      SELECT 
        t.NAMEORIG as USER_ID,
        AVG(AMOUNT) as "7D_AVG_AMT"
      FROM TRANSACTIONS t2
      WHERE t2.NAMEORIG = t.NAMEORIG AND
        t2.TIMESTAMP >= t.TIMESTAMP - INTERVAL '6 DAY' AND
        t2.TIMESTAMP <= t.TIMESTAMP
    )
    {% if is_incremental() %}
    -- "-7 days" because we need at least 6 more days of data in order to compute the aggregation.
    WHERE TIMESTAMP > (SELECT DATEADD(day, -7, MAX(TIMESTAMP)::date) FROM {{ this }})
    {% endif %}
   )  
{% if is_incremental() %}
-- "-1 day" to account for late arriving data
WHERE TIMESTAMP > (SELECT DATEADD(day, -1, MAX(TIMESTAMP)::date) FROM {{ this }})
{% endif %})