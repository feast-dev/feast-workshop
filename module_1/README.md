<h1>Module 1: Streaming ingestion & online feature retrieval with Kafka, Spark, Redis</h1>

In this module, we focus on building features for online serving, and keeping them fresh with a combination of batch feature materialization and stream feature ingestion. We'll be roughly working towards the following:

- **Data sources**: Kafka + File source
- **Online store**: Redis
- **Use case**: Predicting churn for drivers in real time.

<img src="architecture.png" width=750>

<h2>Table of Contents</h2>

- [Workshop](#workshop)
  - [Step 1: Install Feast](#step-1-install-feast)
  - [Step 2: Inspect the data](#step-2-inspect-the-data)
  - [Step 3: Inspect the `feature_store.yaml`](#step-3-inspect-the-feature_storeyaml)
  - [Step 4: Spin up Kafka + Redis + Feast SQL Registry + Feast services](#step-4-spin-up-kafka--redis--feast-sql-registry--feast-services)
  - [Step 5: Why register streaming features in Feast?](#step-5-why-register-streaming-features-in-feast)
    - [Understanding the PushSource](#understanding-the-pushsource)
  - [Step 6: Materialize batch features & ingest streaming features](#step-6-materialize-batch-features--ingest-streaming-features)
    - [A note on Feast feature servers + push servers](#a-note-on-feast-feature-servers--push-servers)
  - [Step 7: Scaling up and scheduling materialization](#step-7-scaling-up-and-scheduling-materialization)
    - [Background: configuring materialization](#background-configuring-materialization)
    - [Step 7: Scheduling materialization](#step-7-scheduling-materialization)
      - [Step 7a: Setting up Airflow](#step-7a-setting-up-airflow)
      - [Step 7b: Examine the Airflow DAG](#step-7b-examine-the-airflow-dag)
      - [Q: What if different feature views have different freshness requirements?](#q-what-if-different-feature-views-have-different-freshness-requirements)
      - [Step 7c: Enable the Airflow DAG](#step-7c-enable-the-airflow-dag)
    - [Step 7d (optional): Run a backfill](#step-7d-optional-run-a-backfill)
- [Conclusion](#conclusion)
- [FAQ](#faq)
    - [How do you synchronize materialized features with pushed features from streaming?](#how-do-you-synchronize-materialized-features-with-pushed-features-from-streaming)
    - [Does Feast allow pushing features to the offline store?](#does-feast-allow-pushing-features-to-the-offline-store)
    - [Can feature / push servers refresh their registry in response to an event? e.g. after a PR merges and `feast apply` is run?](#can-feature--push-servers-refresh-their-registry-in-response-to-an-event-eg-after-a-pr-merges-and-feast-apply-is-run)

# Workshop
## Step 1: Install Feast

First, we install Feast with Spark and Postgres and Redis support:
```bash
pip install "feast[spark,postgres,redis]"
```

## Step 2: Inspect the data
We've changed the original `driver_stats.parquet` to include some new fields and aggregations. You can follow along in [explore_data.ipynb](explore_data.ipynb):

```python
import pandas as pd
pd.read_parquet("feature_repo/data/driver_stats.parquet")
```

![](dataset.png)

The key thing to note is that there are now a `miles_driven` field and a `daily_miles_driven` (which is a pre-computed aggregation). 

## Step 3: Inspect the `feature_store.yaml`

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
  type: file
entity_key_serialization_version: 2
```

The key thing to note for now is the registry is now swapped for a SQL backed registry (Postgres) and the online store has been configured to be Redis. This is specifically for a single Redis node. If you want to use a Redis cluster, then you'd change this to something like:

```yaml
project: feast_demo_local
provider: local
registry:
  registry_type: sql
  path: postgresql://postgres:mysecretpassword@127.0.0.1:55001/feast
online_store:
  type: redis
  redis_type: redis_cluster
  connection_string: "redis1:6379,redis2:6379,ssl=true,password=my_password"
offline_store:
  type: file
entity_key_serialization_version: 2
```

Because we use `redis-py` under the hood, this means Feast also works well with hosted Redis instances like AWS Elasticache ([docs](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/ElastiCache-Getting-Started-Tutorials-Connecting.html)). 

## Step 4: Spin up Kafka + Redis + Feast SQL Registry + Feast services

We then use Docker Compose to spin up the services we need.
- This leverages a script (in `kafka_demo/`) that creates a topic, reads from `feature_repo/data/driver_stats.parquet`, generates newer timestamps, and emits them to the topic.
- This also deploys an instance of Redis.
- **Note:** one big difference between this and the previous module is its choice of using Postgres as the registry. See [Using Scalable Registry](https://docs.feast.dev/tutorials/using-scalable-registry) for details.
- This also deploys a Feast push server (on port 6567) + a Feast feature server (on port 6566). 
  - These servers embed a `feature_store.yaml` file that enables them to connect to a remote registry. The Dockerfile mostly delegates to calling the `feast serve` CLI command, which instantiates a Feast python server ([docs](https://docs.feast.dev/reference/feature-servers/python-feature-server)):
    ```yaml
    FROM python:3.8

    RUN pip install "feast[redis,postgres]"

    COPY feature_repo/feature_store.yaml feature_store.yaml

    # Needed to reach online store and registry within Docker network.
    RUN sed -i 's/localhost:6379/redis:6379/g' feature_store.yaml
    RUN sed -i 's/127.0.0.1:55001/registry:5432/g' feature_store.yaml
    ENV FEAST_USAGE=False

    CMD ["feast", "serve", "-h", "0.0.0.0"]
    ```

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
## Step 5: Why register streaming features in Feast?
Relying on streaming features in Feast enables data scientists to increase freshness of the features they rely on, decreasing training / serving skew. 

A data scientist may start out their feature engineering in their notebook by directly reading from the batch source (e.g. a table they join in a data warehouse). 

But then they hand this over to an engineer to productionize and realize that the model performance is different because pipeline delays lead to stale data being served. 

With Feast, at training data generation time, the data scientist can directly depend on a `FeatureView` with a `PushSource`, which ensures consistent access to fresh data at serving time, thus resulting in less training / serving skew.

### Understanding the PushSource

Let's take a look at an example `FeatureView` in this repo that uses a `PushSource`:

```python
from feast import (
    FileSource,
    PushSource,
)
driver_stats = FileSource(
    name="driver_stats_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="test2@gmail.com",
)
# A push source is useful if you have upstream systems that transform features (e.g. stream processing jobs)
driver_stats_push_source = PushSource(
    name="driver_stats_push_source", batch_source=driver_stats,
)
driver_daily_features_view = FeatureView(
    name="driver_daily_features",
    entities=["driver"],
    ttl=timedelta(seconds=8640000000),
    schema=[Field(name="daily_miles_driven", dtype=Float32),],
    online=True,
    source=driver_stats_push_source,
    tags={"production": "True"},
    owner="test2@gmail.com",
)
```

Using a `PushSource` alleviates this. The data scientist by using the `driver_daily_features` feature view that at serving time, the model will have access to as fresh of a value as possible. Engineers now just need to make sure that any registered `PushSource`s have feature values being regularly pushed to make the feature consistently available.

In the upcoming release, Feast will support the concept of a `StreamFeatureView` as well, which simplifies the life for the engineer further. This will allow common configuration of streaming sources (e.g. Kafka) and apply transformations (defined by data scientists) so an engineer doesn't need to scan for `PushSource`s and push data into Feast.

## Step 6: Materialize batch features & ingest streaming features

We'll switch gears into a Jupyter notebook. This will guide you through:
- Registering a `FeatureView` that has a single schema across both a batch source (`FileSource`) with aggregate features and a stream source (`PushSource`).
  - **Note:** Feast also supports directly authoring a `StreamFeatureView` that contains stream transformations / aggregations (e.g. via Spark, Flink, or Bytewax), but the onus is on you to actually execute those transformations.
- Materializing feature view values from batch sources to the online store (e.g. Redis).
- Ingesting feature view values from streaming sources (e.g. window aggregate features from Spark + Kafka)
- Retrieve features at low latency from Redis through Feast.
- Working with a Feast push server + feature server to ingest and retrieve features through HTTP endpoints (instead of needing `feature_store.yaml` and `FeatureStore` instances)

Run the Jupyter notebook ([feature_repo/workshop.ipynb](feature_repo/module_1.ipynb)).

### A note on Feast feature servers + push servers
The above notebook introduces a way to curl an HTTP endpoint to push or retrieve features from Redis.

The servers by default cache the registry (expiring and reloading every 10 minutes). If you want to customize that time period, you can do so in `feature_store.yaml`.

Let's look at the `feature_store.yaml` used in this module (which configures the registry differently than in the previous module):

```yaml
project: feast_demo_local
provider: local
registry:
  path: data/local_registry.db
  cache_ttl_seconds: 5
online_store:
  type: redis
  connection_string: localhost:6379
offline_store:
  type: file
```

The `registry` config maps to constructor arguments for `RegistryConfig` Pydantic model([reference](https://rtd.feast.dev/en/master/index.html#feast.repo_config.RegistryConfig)).
- In the `feature_store.yaml` above, note that there is a `cache_ttl_seconds` of 5. This ensures that every five seconds, the feature server and push server will expire its registry cache. On the following request, it will refresh its registry by pulling from the registry path.
- Feast adds a convenience wrapper so if you specify just `registry: [path]`, Feast will map that to `RegistryConfig(path=[your path])`.

## Step 7: Scaling up and scheduling materialization
### Background: configuring materialization
By default, materialization will pull all the latest feature values for each unique entity into memory, and then write to the online store. 

You can speed up / scale this up in different ways:
- Using a more scalable materialization mechanism (e.g. using the Bytewax or Spark materialization engines)
- Running materialization jobs on a per feature view basis
- Running materialization jobs in parallel

To run many parallel materialization jobs, you'll want to use the **SQL registry** (which is already used in this module).
Then you could run multiple materialization jobs in parallel (e.g. using `feast materialize [FEATURE_VIEW_NAME] start_time end_time`) 

### Step 7: Scheduling materialization
To ensure fresh features, you'll want to schedule materialization jobs regularly. This can be as simple as having a cron job that calls `feast materialize-incremental`. 

Users may also be interested in integrating with Airflow, in which case you can build a custom Airflow image with the Feast SDK installed, and then use a `PythonOperator` (with `store.materialize`).

#### Step 7a: Setting up Airflow

We setup a standalone version of Airflow to set up the PythonOperator (Airflow now prefers @task for this). 

```bash
cd airflow_demo; sh setup_airflow.sh
```

#### Step 7b: Examine the Airflow DAG

The example dag is going to run on a daily basis and materialize *all* feature views based on the start and end interval. Note that there is a 1 hr overlap in the start time to account for potential late arriving data in the offline store.

```python
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
        store = FeatureStore(config=repo_config)
        # Add 1 hr overlap to account for late data
        # Note: normally, you'll probably have different feature views with different freshness requirements, instead of materializing all feature views every day.
        store.materialize(data_interval_start.subtract(hours=1), data_interval_end)

    materialize()

materialization_dag = materialize_dag()
```

In this test case, you can also use a single command `feast materialize-incremental $(date +%Y-%m-%d)` and that will materialize until the current time. 

#### Q: What if different feature views have different freshness requirements?

There's no built in mechanism for this, but you could store this logic in the feature view tags (e.g. a `batch_schedule`).
 
Then, you can parse these feature view in your Airflow job. You could for example have one DAG that runs all the daily `batch_schedule` feature views, and another DAG that runs all feature views with an hourly `batch_schedule`.

#### Step 7c: Enable the Airflow DAG
Now go to `localhost:8080`, use Airflow's auto-generated admin password to login, and toggle on the `materialize_dag`. It should run one task automatically.

### Step 7d (optional): Run a backfill
To run a backfill (i.e. process previous days of the above while letting Airflow manage state), you can do (from the `airflow_demo` directory):

> **Warning:** This works correctly with the Redis online store because it conditionally writes. This logic has not been implemented for other online stores yet, and so can result in incorrect behavior

```bash
export AIRFLOW_HOME=$(pwd)/airflow_home
airflow dags backfill \
    --start-date 2019-11-21 \
    --end-date 2019-11-25 \
    materialize_dag
```


# Conclusion
By the end of this module, you will have learned how to build streaming features power real time models with Feast. Feast abstracts away the need to think about data modeling in the online store and helps you:
- maintain fresh features in the online store by
  - ingesting batch features into the online store (via `feast materialize` or `feast materialize-incremental`)
  - ingesting streaming features into the online store (e.g. through `feature_store.push` or a Push server endpoint (`/push`))
- serve features (e.g. through `feature_store.get_online_features` or through feature servers)

# FAQ

### How do you synchronize materialized features with pushed features from streaming?
This relies on individual online store implementations. The existing Redis online store implementation for example will check timestamps of incoming events and prefer the latest version.

Doing this event timestamp checking is expensive though and slows down writes. In many cases, this is not preferred. Databases often support storing multiple versions of the same value, so you can leverage that (+ TTLs) to query the most recent version at read time.

### Does Feast allow pushing features to the offline store?
Yes! See more details at https://docs.feast.dev/reference/data-sources/push#pushing-data

### Can feature / push servers refresh their registry in response to an event? e.g. after a PR merges and `feast apply` is run?
Unfortunately, currently the servers don't support this. Feel free to contribute a PR though to enable this! The tricky part here is that Feast would need to keep track of these servers in the registry (or in some other way), which is not the way Feast is currently designed.
