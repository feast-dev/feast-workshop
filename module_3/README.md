<h1>Module 3: Scheduled batch transformations (Snowflake)</h1>

This is a very similar module to module 1. The key difference is now we'll be using a data warehouse (Snowflake) in combination with dbt + Airflow to ensure that batch features are regularly generated. 

- **Data sources**: Snowflake
- **Online store**: Redis
- **Use case**: Predicting churn for drivers in real time.

<img src="architecture.png" width=750>

<h2>Table of Contents</h2>

- [Workshop](#workshop)
  - [Step 1: Install Feast](#step-1-install-feast)
  - [Step 2: Inspect the `feature_store.yaml`](#step-2-inspect-the-feature_storeyaml)
  - [Step 4: Spin up services](#step-4-spin-up-services)
    - [Step 4a: Kafka + Redis + Feast SQL Registry + Feast services](#step-4a-kafka--redis--feast-sql-registry--feast-services)
    - [Step 4b: Setting up Airflow + dbt](#step-4b-setting-up-airflow--dbt)
    - [Step 4c: Examine the Airflow DAG](#step-4c-examine-the-airflow-dag)
      - [Q: What if different feature views have different freshness requirements?](#q-what-if-different-feature-views-have-different-freshness-requirements)
    - [Step 4d: Enable the Airflow DAG](#step-4d-enable-the-airflow-dag)
    - [Step 4e (optional): Run a backfill](#step-4e-optional-run-a-backfill)
  - [Step 5: Streaming](#step-5-streaming)
- [Conclusion](#conclusion)
- [FAQ](#faq)
    - [How do you synchronize materialized features with pushed features from streaming?](#how-do-you-synchronize-materialized-features-with-pushed-features-from-streaming)
    - [Does Feast allow pushing features to the offline store?](#does-feast-allow-pushing-features-to-the-offline-store)
    - [Can feature / push servers refresh their registry in response to an event? e.g. after a PR merges and `feast apply` is run?](#can-feature--push-servers-refresh-their-registry-in-response-to-an-event-eg-after-a-pr-merges-and-feast-apply-is-run)

# Workshop
## Step 1: Install Feast

First, we install Feast with Spark and Postgres and Redis support:
```bash
pip install "feast[snowflake,postgres,redis]"
```

## Step 2: Inspect the `feature_store.yaml`

```yaml
project: feast_demo_local
provider: local
registry:
  registry_type: sql
  path: postgresql://postgres:mysecretpassword@127.0.0.1:55001/feast
online_store:
  type: redis
  connection_string: localhost:6379
offline_store:
  type: snowflake.offline
  account: ${SNOWFLAKE_DEPLOYMENT_URL}
  user: ${SNOWFLAKE_USER}
  password: ${SNOWFLAKE_PASSWORD}
  role: ${SNOWFLAKE_ROLE}
  warehouse: ${SNOWFLAKE_WAREHOUSE}
  database: TECTON_DEMO_DATA
  schema: FRAUD
entity_key_serialization_version: 2
```

Now we're using a test database in Snowflake. 

## Step 4: Spin up services

### Step 4a: Kafka + Redis + Feast SQL Registry + Feast services

We use Docker Compose to spin up the services we need.
- This is similar to the previous module, which feeds data from  `feature_repo/data/driver_stats.parquet`into a Kafka topic
- This also deploys an instance of Redis, Postgres for a registry, a Feast feature server + push server.

Start up the Docker daemon and then use Docker Compose to spin up the services as described above:
- You may need to run `sudo docker-compose up` if you run into a Docker permission denied error
```console
$ docker-compose up

Creating network "module_1_default" with the default driver
Creating zookeeper ... done
Creating redis     ... done
Creating broker               ... done
Creating feast_feature_server ... done
Creating feast_push_server    ... done
Creating kafka_events         ... done
Creating registry             ... done
Attaching to zookeeper, redis, broker, feast_push_server, feast_feature_server, kafka_events, registry
...
```

### Step 4b: Set up dbt
> **TODO(adchia):** Generate parquet file to upload for public Snowflake dataset for features
 
There's already a dbt model that generates batch transformations. You just need to init this:

> **Note:** You'll need to install dbt-snowflake as well! `brew tap dbt-labs/dbt` and `brew install dbt-snowflake`

To initialize dbt with your own credentials, do this
```bash
cd dbt/feast_demo; dbt init
```

### Step 4c: Setting up Airflow

We setup a standalone version of Airflow to set up the `PythonOperator` (Airflow now prefers @task for this) and `BashOperator` which will run incremental dbt models. We use dbt to define batch transformations from Snowflake, and once the incremental model is tested / ran, we run materialization.

```bash
cd airflow_demo; sh setup_airflow.sh
```

### Step 4d: Examine the Airflow DAG

The example dag is going to run on a daily basis and materialize *all* feature views based on the start and end interval. Note that there is a 1 hr overlap in the start time to account for potential late arriving data in the offline store. 

With dbt incremental models, the model itself in incremental mode selects overlapping windows of data to account for late arriving data. Feast materialization similarly has a late arriving threshold.

```python
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
        entity_key_serialization_version=2
      )
      store = FeatureStore(config=repo_config)
      store.materialize(data_interval_start.subtract(hours=1), data_interval_end)
    
    # Setup DAG
    dbt_test >> dbt_run >> materialize()
```

#### Q: What if different feature views have different freshness requirements?

There's no built in mechanism for this, but you could store this logic in the feature view tags (e.g. a `batch_schedule`).
 
Then, you can parse these feature view in your Airflow job. You could for example have one DAG that runs all the daily `batch_schedule` feature views, and another DAG that runs all feature views with an hourly `batch_schedule`.

### Step 4e: Enable the Airflow DAG
Now go to `localhost:8080`, use Airflow's auto-generated admin password to login, and toggle on the `materialize_dag`. It should run one task automatically.

### Step 4f (optional): Run a backfill
To run a backfill (i.e. process previous days of the above while letting Airflow manage state), you can do (from the `airflow_demo` directory):

> **Warning:** This works correctly with the Redis online store because it conditionally writes. This logic has not been implemented for other online stores yet, and so can result in incorrect behavior

```bash
export AIRFLOW_HOME=$(pwd)/airflow_home
airflow dags backfill \
    --start-date 2021-07-01 \
    --end-date 2021-07-15 \
    feature_dag
```

## Step 5: Streaming
- TODO(danny): re-add streaming

# Conclusion
By the end of this module, you will have learned how to build a full feature platform, with orchestrated batch transformations (using dbt + Airflow), orchestrated materialization (with Feast + Airflow), and streaming ingestion (with Spark + Feast).

Feast abstracts away the need to think about data modeling in the online store and helps you:
- maintain fresh features in the online store by
  - ingesting batch features into the online store (via `feast materialize` or `feast materialize-incremental`)
  - ingesting streaming features into the online store (e.g. through `feature_store.push` or a Push server endpoint (`/push`))
- serve features (e.g. through `feature_store.get_online_features` or through feature servers)

# FAQ

### How does this work in production?
Several things change:
- All credentials are secured as secrets
- dbt models are version controlled
- Production deployment of Airflow (e.g. syncing with a Git repository of DAGs, using k8s)
- Bundling dbt models with Airflow (e.g. via S3 like this [MWAA + dbt guide](https://docs.aws.amazon.com/mwaa/latest/userguide/samples-dbt.html))
- Airflow DAG parallelizes across feature views (instead of running a single `feature_store.materialize` across all feature views)
- Feast materialization is configured to be more scalable (e.g. using other Feast batch materialization engines [Bytewax](https://docs.feast.dev/reference/batch-materialization/bytewax), [Snowflake](https://docs.feast.dev/reference/batch-materialization/snowflake), [Lambda](https://rtd.feast.dev/en/master/index.html?highlight=LambdaMaterializationEngine#feast.infra.materialization.aws_lambda.lambda_engine.LambdaMaterializationEngine), [Spark](https://github.com/feast-dev/feast/blob/master/sdk/python/feast/infra/materialization/contrib/spark/spark_materialization_engine.py))
