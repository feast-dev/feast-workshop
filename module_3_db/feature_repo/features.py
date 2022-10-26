from datetime import timedelta

from feast import (
    FeatureView,
    Field,
)
from feast.types import String, Float64

from data_sources import *
from entities import *

user_transaction_amount_metrics = FeatureView(
    name="user_transaction_amount_metrics",
    description="User transaction features",
    entities=[user],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="user_id", dtype=String),
        Field(name="amt_sum_1d_10m", dtype=Float64),
        Field(name="amt_mean_1d_10m", dtype=Float64),
    ],
    online=True,
    source=aggregate_transactions_source,
    tags={"production": "True"},
    owner="test2@gmail.com",
)
