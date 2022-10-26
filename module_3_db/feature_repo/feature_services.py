from feast import FeatureService

from features import *

feature_service_1 = FeatureService(
    name="model_v1",
    features=[user_transaction_amount_metrics],
    owner="test3@gmail.com",
)
