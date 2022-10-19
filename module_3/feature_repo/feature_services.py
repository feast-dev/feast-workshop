from feast import FeatureService

from features import *

feature_service = FeatureService(
    name="model_v1",
    features=[credit_scores_view],
    owner="test3@gmail.com",
)

feature_service_2 = FeatureService(
    name="model_v2",
    features=[credit_scores_view, aggregate_transactions_view],
    owner="test3@gmail.com",
)
