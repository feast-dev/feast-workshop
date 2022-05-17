from datetime import timedelta

import pandas as pd
from feast import (
    FeatureView,
    Field,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, String

from data_sources import *
from entities import *

driver_hourly_stats_view = FeatureView(
    name="driver_hourly_stats",
    description="Hourly features",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
    ],
    online=True,
    source=driver_stats,
    tags={"production": "True"},
    owner="test2@gmail.com",
)

driver_daily_features_view = FeatureView(
    name="driver_daily_features",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="daily_miles_driven", dtype=Float32),
        Field(name="lat", dtype=Float32),
        Field(name="lon", dtype=Float32),
    ],
    online=True,
    source=driver_stats_push_source,
    tags={"production": "True"},
    owner="test2@gmail.com",
)


# Define an on demand feature view which can generate new features based on
# existing feature views and RequestSource features
@on_demand_feature_view(
    sources=[driver_hourly_stats_view, val_to_add_request],
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


@on_demand_feature_view(
    sources=[driver_daily_features_view],
    schema=[Field(name="avg_hourly_miles_driven", dtype=Float64),],
)
def avg_hourly_miles_driven(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["avg_hourly_miles_driven"] = inputs["daily_miles_driven"] / 24
    return df


@on_demand_feature_view(
    sources=[driver_daily_features_view],
    schema=[Field(name=f"geohash_{i}", dtype=String) for i in range(1, 7)],
)
def location_features_from_push(inputs: pd.DataFrame) -> pd.DataFrame:
    import pygeohash as gh

    df = pd.DataFrame()
    df["geohash"] = inputs.apply(lambda x: gh.encode(x.lat, x.lon), axis=1).astype(
        "string"
    )

    for i in range(1, 7):
        df[f"geohash_{i}"] = df["geohash"].str[:i].astype("string")
    return df
