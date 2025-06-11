from feast import (
    Field,
    FileSource,
    PushSource,
    RequestSource,
    SnowflakeSource
)
from feast.types import Int64, Float32

# driver_stats = SparkSource(
#     name="driver_stats_source",
#     path="../data/driver_stats_lat_lon.parquet",
#     timestamp_field="event_timestamp",
#     created_timestamp_column="created",
#     description="A table describing the stats of a driver based on hourly logs",
#     owner="test2@gmail.com",
# )


tpch_sf = SnowflakeSource(
    database="SNOWFLAKE_SAMPLE_DATA",
    schema="TPCH_SF10",
    table="ORDERS",
    timestamp_field="O_ORDERDATE"
)