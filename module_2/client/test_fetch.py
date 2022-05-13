from feast import FeatureStore

store = FeatureStore(repo_path=".")

import pandas as pd
from datetime import datetime


def run_demo():
    store = FeatureStore(repo_path=".")

    print("--- Historical features ---")
    entity_df = pd.DataFrame.from_dict(
        {
            "driver_id": [1001, 1002, 1003, 1004],
            "event_timestamp": [
                datetime(2021, 4, 12, 10, 59, 42),
                datetime(2021, 4, 12, 8, 12, 10),
                datetime(2021, 4, 12, 16, 40, 26),
                datetime(2021, 4, 12, 15, 1, 12),
            ],
            "val_to_add": [1, 2, 3, 4],
            "val_to_add_2": [10, 20, 30, 40],
        }
    )
    training_df = store.get_historical_features(
        entity_df=entity_df, features=store.get_feature_service("model_v2"),
    ).to_df()
    print(training_df.head())

    print("\n--- Online features ---")
    features = store.get_online_features(
        features=store.get_feature_service("model_v2"),
        entity_rows=[{"driver_id": 1001, "val_to_add": 1000, "val_to_add_2": 2000,}],
    ).to_dict()
    for key, value in sorted(features.items()):
        print(key, " : ", value)

    print("\n--- Simulate a stream event ingestion via the daily stats push source ---")
    event_df = pd.DataFrame.from_dict(
        {
            "driver_id": [1001],
            "event_timestamp": [datetime(2021, 5, 13, 10, 59, 42),],
            "created": [datetime(2021, 5, 13, 10, 59, 42),],
            "daily_miles_driven": [1234],
        }
    )
    print(event_df)
    store.push("driver_stats_push_source", event_df)

    print("\n--- Online features again with updated values from a stream push---")
    features = store.get_online_features(
        features=store.get_feature_service("model_v2"),
        entity_rows=[{"driver_id": 1001, "val_to_add": 1000, "val_to_add_2": 2000,}],
    ).to_dict()
    for key, value in sorted(features.items()):
        print(key, " : ", value)


if __name__ == "__main__":
    run_demo()
