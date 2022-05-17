from feast import FeatureService

from features import *

feature_service = FeatureService(
    name="model_v1",
    features=[driver_hourly_stats_view[["conv_rate"]]],
    owner="test3@gmail.com",
)

feature_service = FeatureService(
    name="model_v2",
    features=[
        driver_hourly_stats_view,
        driver_daily_features_view,
        transformed_conv_rate,
    ],
    owner="test3@gmail.com",
)

feature_service = FeatureService(
    name="model_v3",
    features=[
        driver_hourly_stats_view,
        driver_daily_features_view,
        transformed_conv_rate,
        avg_hourly_miles_driven,
        location_features,
    ],
    owner="test3@gmail.com",
)

