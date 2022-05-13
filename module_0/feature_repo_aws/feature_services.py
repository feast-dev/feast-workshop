from feast import FeatureService

from features import *

feature_service = FeatureService(
    name="model_v1",
    features=[driver_hourly_stats_view[["conv_rate"]]],
    owner="test3@gmail.com",
)

feature_service = FeatureService(
    name="model_v2", features=[driver_hourly_stats_view], owner="test3@gmail.com",
)
