from feast import PushSource
from feast.infra.offline_stores.contrib.spark_offline_store.spark_source import (
    SparkSource,
)

# Historical log of transactions stream
transactions_source = SparkSource(
    name="transactions_source",
    table="demo_fraud_v2.transactions",
    timestamp_field="timestamp",
)

# Precomputed aggregate transaction feature values (batch / stream)
aggregate_transactions_source = PushSource(
    name="transactions_1d",
    batch_source=SparkSource(
        name="transactions_1d_batch",
        table="demo_fraud_v2.aggregate_transaction_features",
        timestamp_field="timestamp",
        tags={"dbtModel": "models/example/aggregate_transaction_features.sql"},
    ),
)
