import os
from airflow.decorators import dag, task
from datetime import datetime
from feast import RepoConfig, FeatureStore
from feast.repo_config import RegistryConfig
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
import pendulum


@dag(
    schedule="@daily",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    tags=["feast"],
)
def materialize_dag():
    @task()
    def materialize(data_interval_start=None, data_interval_end=None):
        repo_config = RepoConfig(
            registry=RegistryConfig(
                registry_type="sql",
                path="postgresql://postgres:mysecretpassword@127.0.0.1:55001/feast",
            ),
            project="feast_demo_local",
            provider="local",
            offline_store="file",
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

    materialize()


materialization_dag = materialize_dag()
