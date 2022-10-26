{% macro prev_day_partition() %}
  (SELECT MAX(timestamp)::date FROM {{ this }})
{% endmacro %}

{% macro next_day_partition() %}
  (SELECT date_add(MAX(timestamp)::date, 1) FROM {{ this }})
{% endmacro %}