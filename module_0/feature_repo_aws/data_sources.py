from feast import FileSource

driver_stats = FileSource(
    name="driver_stats_source",
    path="s3://feast-workshop-marty/driver_stats.parquet",
    s3_endpoint_override="http://s3.us-west-2.amazonaws.com",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="martin.abeleda@gmail.com",
)
