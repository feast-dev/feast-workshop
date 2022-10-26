import os
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from feast import RepoConfig, FeatureStore
from feast.infra.offline_stores.contrib.spark_offline_store.spark import (
    SparkOfflineStoreConfig,
)
from feast.repo_config import RegistryConfig
from feast.infra.online_stores.dynamodb import DynamoDBOnlineStoreConfig
import pendulum

with DAG(
    dag_id="feature_dag",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    description="A dbt + Feast DAG",
    schedule="@daily",
    catchup=False,
    tags=["feast"],
) as dag:
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
            cd ${AIRFLOW_HOME}; dbt test --models "aggregate_transaction_features"
            """,
        dag=dag,
    )

    # Generate new transformed feature values
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
            cd ${AIRFLOW_HOME}; dbt run --models "aggregate_transaction_features"
            """,
        dag=dag,
    )

    # Use Feast to make these feature values available in a low latency store
    @task()
    def materialize(data_interval_start=None, data_interval_end=None):
        repo_config = RepoConfig(
            registry=RegistryConfig(
                registry_type="sql",
                path="postgresql://postgres:mysecretpassword@[YOUR-RDS-ENDPOINT:PORT]/feast",
            ),
            project="feast_demo",
            provider="local",
            offline_store=SparkOfflineStoreConfig(
                spark_conf={
                    "spark.ui.enabled": "false",
                    "spark.eventLog.enabled": "false",
                    "spark.sql.catalogImplementation": "hive",
                    "spark.sql.parser.quotedRegexColumnNames": "true",
                    "spark.sql.session.timeZone": "UTC",
                }
            ),
            online_store=DynamoDBOnlineStoreConfig(region="us-west-1"),
            entity_key_serialization_version=2,
        )
        # Needed for Mac OS users because of a seg fault in requests for standalone Airflow (not needed in prod)
        os.environ["NO_PROXY"] = "*"
        os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
        store = FeatureStore(config=repo_config)
        # Add 1 hr overlap to account for late data
        # Note: normally, you'll probably have different feature views with different freshness requirements, instead
        # of materializing all feature views every day.
        store.materialize(data_interval_start.subtract(hours=1), data_interval_end)

    # Setup DAG
    dbt_test >> dbt_run >> materialize()
