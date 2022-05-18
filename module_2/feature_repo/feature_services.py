from feast import FeatureService

from features import *

feature_service = FeatureService(
    name="model_v1",
    features=[driver_hourly_stats_view[["conv_rate"]]],
    owner="martin.abeleda@gmail.com",
)

feature_service_2 = FeatureService(
    name="model_v2",
    features=[
        driver_hourly_stats_view[["conv_rate"]],
        transformed_conv_rate,
    ],
    owner="martin.abeleda@gmail.com",
)

feature_service_3 = FeatureService(
    name="model_v3",
    features=[
        driver_daily_features_view,
        location_features_from_push,
    ],
    owner="martin.abeleda@gmail.com",
)
