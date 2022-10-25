from feast import PushSource, SnowflakeSource
import yaml

# Feast also supports pulling data from data warehouses like BigQuery, Snowflake, Redshift and data lakes (e.g. via
# Redshift Spectrum, Trino, Spark)
transactions_source = SnowflakeSource(
    name="transactions_source",
    database=yaml.safe_load(open("feature_store.yaml"))["offline_store"]["database"],
    table="TRANSACTIONS",
    schema="FRAUD",
    timestamp_field="TIMESTAMP",
)

aggregate_transactions_batch = SnowflakeSource(
    name="transactions_7d_batch",
    database=yaml.safe_load(open("feature_store.yaml"))["offline_store"]["database"],
    table="AGGREGATE_TRANSACTION_FEATURES",
    schema="FRAUD",
    timestamp_field="TIMESTAMP",
    tags={"dbtModel": "models/example/aggregate_transaction_features.sql"},
)

aggregate_transactions_push = PushSource(
    name="transactions_7d", batch_source=aggregate_transactions_batch
)

credit_scores = SnowflakeSource(
    name="credit_scores_source",
    database=yaml.safe_load(open("feature_store.yaml"))["offline_store"]["database"],
    query="SELECT USER_ID, DATE, CREDIT_SCORE, TIMESTAMP FROM CREDIT_SCORES",
    schema="FRAUD",
    timestamp_field="TIMESTAMP",
)
