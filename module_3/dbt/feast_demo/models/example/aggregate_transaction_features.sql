{{ config(materialized='incremental') }}

SELECT
    NAMEORIG as USER_ID,
    TIMESTAMP,
    AVG(AMOUNT) OVER (PARTITION BY NAMEORIG ORDER BY TIMESTAMP ROWS BETWEEN 6 preceding AND CURRENT ROW) as "7D_AVG_AMT"
FROM TRANSACTIONS
{% if is_incremental() %}
  WHERE TIMESTAMP > (SELECT DATEADD(day, -3, MAX(TIMESTAMP)::date) FROM {{ this }})
{% endif %}
