def print_online_features(features):
    for key, value in sorted(features.items()):
        print(key, " : ", value)


from feast import FeatureStore

store = FeatureStore(repo_path=".")
features = store.get_online_features(
    features=[
        "transformed_conv_rate:conv_rate_plus_val1",
        "transformed_conv_rate:conv_rate_plus_val2",
    ],
    entity_rows=[{"driver_id": 1001, "val_to_add": 1000, "val_to_add_2": 2000}],
).to_dict()
print_online_features(features)
