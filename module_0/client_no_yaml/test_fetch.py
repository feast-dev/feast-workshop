from feast import FeatureStore, RepoConfig
from feast.repo_config import RegistryConfig


repo_config = RepoConfig(
    registry=RegistryConfig(path="s3://feast-workshop-marty/registry.pb"),
    project="feast_demo_aws",
    provider="aws",
    offline_store="file",  # Could also be the OfflineStoreConfig e.g. FileOfflineStoreConfig
    online_store="null",  # Could also be the OnlineStoreConfig e.g. RedisOnlineStoreConfig
)
store = FeatureStore(config=repo_config)

import pandas as pd

# Get the latest feature values for unique entities
entity_df = pd.DataFrame.from_dict(
    {
        "driver_id": [
            1001,
            1002,
            1003,
            1004,
            1005,
        ],
    }
)
entity_df["event_timestamp"] = pd.to_datetime("now", utc=True)

training_df = store.get_historical_features(
    entity_df=entity_df,
    features=store.get_feature_service("model_v2"),
).to_df()

# Make batch predictions
# predictions = model.predict(training_df)
print(training_df)
