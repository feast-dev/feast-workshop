from feast import FileSource

driver_stats = FileSource(
    name="driver_stats_source",
    path="gs://feast-workshop-danny/driver_stats.parquet",  # TODO: Replace with your bucket
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="test2@gmail.com",
)
