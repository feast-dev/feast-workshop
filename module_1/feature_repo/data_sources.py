import os
from feast import (
    FileSource,
    PushSource,
)

# Feast also supports pulling data from data warehouses like BigQuery, Snowflake, Redshift and data lakes (e.g. via Redshift Spectrum, Trino, Spark)
driver_stats = FileSource(
    name="driver_stats_source",
    path=f"{os.getcwd()}/data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="test2@gmail.com",
)

# A push source is useful if you have upstream systems that transform features (e.g. stream processing jobs)
driver_stats_push_source = PushSource(
    name="driver_stats_push_source",
    batch_source=driver_stats,
)
