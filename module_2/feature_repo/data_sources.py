from feast import (
    Field,
    FileSource,
    PushSource,
    RequestSource,
)
from feast.types import Int64

driver_stats = FileSource(
    name="driver_stats_source",
    path="../data/driver_stats.parquet",  # Should be a remote path in reality for re-use
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="test2@gmail.com",
)

# A push source is useful if you have upstream systems that transform features (e.g. stream processing jobs)
driver_stats_push_source = PushSource(
    name="driver_stats_push_source", batch_source=driver_stats,
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
