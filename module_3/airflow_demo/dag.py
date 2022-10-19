import os
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from feast import RepoConfig, FeatureStore
from feast.infra.offline_stores.snowflake import SnowflakeOfflineStoreConfig
from feast.repo_config import RegistryConfig
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
import pendulum

with DAG(
    dag_id='feature_dag',
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    description='A dbt + Feast DAG',
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

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
            cd ${AIRFLOW_HOME}; dbt run --models "aggregate_transaction_features"
            """,
        dag=dag,
    )

    @task()
    def materialize(data_interval_start=None, data_interval_end=None):
        repo_config = RepoConfig(
            registry=RegistryConfig(
                registry_type="sql",
                path="postgresql://postgres:mysecretpassword@127.0.0.1:55001/feast",
            ),
            project="feast_demo_local",
            provider="local",
            offline_store=SnowflakeOfflineStoreConfig(
                account=os.getenv("SNOWFLAKE_DEPLOYMENT_URL"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                role=os.getenv("SNOWFLAKE_ROLE"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema_=os.getenv("SNOWFLAKE_SCHEMA")
            ),
            online_store=RedisOnlineStoreConfig(connection_string="localhost:6379"),
            entity_key_serialization_version=2,
        )
        # Needed for Mac OS users because of a seg fault in requests for standalone Airflow (not needed in prod)
        os.environ["NO_PROXY"] = "*"
        store = FeatureStore(config=repo_config)
        # Add 1 hr overlap to account for late data
        # Note: normally, you'll probably have different feature views with different freshness requirements, instead
        # of materializing all feature views every day.
        store.materialize(data_interval_start.subtract(hours=1), data_interval_end)

    dbt_test >> dbt_run >> materialize()

