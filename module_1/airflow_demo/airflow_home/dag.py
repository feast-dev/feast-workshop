from airflow.decorators import dag, task
from datetime import datetime
from feast import RepoConfig, RegistryConfig, FeatureStore, RedisOnlineStoreConfig


@dag(
    schedule="@daily",
    catchup=False,
    tags=["feast"],
)
def materialize_dag():
    @task()
    def materialize():
        repo_config = RepoConfig(
            registry=RegistryConfig(
                registry_type="sql",
                path="postgresql://postgres:mysecretpassword@127.0.0.1:55001/feast",
            ),
            project="feast_demo_local",
            provider="local",
            offline_store="file",
            online_store=RedisOnlineStoreConfig(connection_string="localhost:6379"),
        )
        store = FeatureStore(config=repo_config)
        store.materialize_incremental(datetime.now())

    materialize()


materialize_dag()
