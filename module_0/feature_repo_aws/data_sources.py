from feast import FileSource

driver_stats = FileSource(
    name="driver_stats_source",
    path="s3://feast-workshop-siddh/driver_stats.parquet",  # TODO: Replace with your bucket
    s3_endpoint_override="http://s3.ap-northeast-1.amazonaws.com",  # Needed since s3fs defaults to us-east-1
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="siddhantmahalle@outlook.com",
)
