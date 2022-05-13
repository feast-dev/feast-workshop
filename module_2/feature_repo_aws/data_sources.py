from feast import (
    Field,
    FileSource,
    RequestSource,
)
from feast.types import Int64

driver_stats = FileSource(
    name="driver_stats_source",
    path="s3://feast-spark-workshop-test/driver_stats.parquet",  # TODO: Replace with your bucket
    s3_endpoint_override="http://s3.us-west-2.amazonaws.com",  # Needed since s3fs defaults to us-east-1
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="test2@gmail.com",
)


# Define a request data source which encodes features / information only
# available at request time (e.g. part of the user initiated HTTP request)
input_request = RequestSource(
    name="vals_to_add",
    schema=[
        Field(name="val_to_add", dtype=Int64),
        Field(name="val_to_add_2", dtype=Int64),
    ],
)
