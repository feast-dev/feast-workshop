from datetime import timedelta

import pandas as pd
from feast import (
    FeatureView,
    Field,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64

from data_sources import *
from entities import *

driver_daily_features_view = FeatureView(
    name="driver_daily_features",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[Field(name="daily_miles_driven", dtype=Float32),],
    online=True,
    source=driver_stats_push_source,
    tags={"production": "True"},
    owner="test2@gmail.com",
)

driver_hourly_stats_view = FeatureView(
    name="driver_hourly_stats",
    description="Hourly features",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="miles_driven", dtype=Float32),
    ],
    online=True,
    source=driver_stats,
    tags={"production": "True"},
    owner="test2@gmail.com",
)


# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[driver_hourly_stats_view, input_request,],
    schema=[
        Field(name="conv_rate_plus_val1", dtype=Float64),
        Field(name="conv_rate_plus_val2", dtype=Float64),
    ],
)
def transformed_conv_rate(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["conv_rate_plus_val1"] = inputs["conv_rate"] + inputs["val_to_add"]
    df["conv_rate_plus_val2"] = inputs["conv_rate"] + inputs["val_to_add_2"]
    return df
