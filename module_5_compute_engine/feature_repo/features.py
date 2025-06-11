from datetime import timedelta

from feast import (
    BatchFeatureView,
)
import pyspark
from feast.types import String

from data_sources import *
from entities import *


def transform_feature(inputs: pyspark.sql.DataFrame):
    return inputs


bfv = BatchFeatureView(
    name="order_stats",
    description="Hourly features",
    entities=[customer],
    schema=[
        Field(name="O_TOTALPRICE", dtype=Float32),
        Field(name="O_ORDERSTATUS", dtype=String),
    ],
    udf=transform_feature,
    online=True,
    source=tpch_sf,
    tags={"production": "True"},
    owner="test2@gmail.com",
)
