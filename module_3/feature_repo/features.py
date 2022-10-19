from datetime import timedelta

from feast import (
    FeatureView,
    Field,
)
from feast.types import Float32, Int32, String

from data_sources import *
from entities import *

credit_scores_view = FeatureView(
    name="credit_scores_features",
    description="User credit scores",
    entities=[user],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="USER_ID", dtype=String),
        Field(name="CREDIT_SCORE", dtype=Int32),
    ],
    online=True,
    source=credit_scores,
    tags={"production": "True"},
    owner="test2@gmail.com",
)

aggregate_transactions_view = FeatureView(
    name="aggregate_transactions_features",
    description="User transaction features",
    entities=[user],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="USER_ID", dtype=String),
        Field(name="7D_AVG_AMT", dtype=Float32),
    ],
    online=True,
    source=aggregate_transactions_source,
    tags={"production": "True"},
    owner="test2@gmail.com",
)
