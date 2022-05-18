from datetime import timedelta

from feast import (
    FeatureView,
    Field,
)
from feast.types import Float32

from data_sources import *
from entities import *

driver_hourly_stats_view = FeatureView(
    name="driver_hourly_stats",
    description="Hourly features from Danny",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[Field(name="conv_rate", dtype=Float32),],
    online=True,
    source=driver_stats,
    tags={"production": "True"},
    owner="test@gmail.com",
)

driver_hourly_stats_view_2 = FeatureView(
    name="driver_hourly_stats",
    description="Hourly features from Danny",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[Field(name="conv_rate", dtype=Float32),],
    online=True,
    source=driver_stats,
    tags={"production": "True"},
    owner="test2@gmail.com",
)
