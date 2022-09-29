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
  - [Step 4: Spin up Kafka + Redis + Feast services](#step-4-spin-up-kafka--redis--feast-services)
  - [Step 5: Why register streaming features in Feast?](#step-5-why-register-streaming-features-in-feast)
    - [Understanding the PushSource](#understanding-the-pushsource)
  - [Step 6: Materialize batch features & ingest streaming features](#step-6-materialize-batch-features--ingest-streaming-features)
    - [Scheduling materialization](#scheduling-materialization)
      - [Airflow PythonOperator](#airflow-pythonoperator)
      - [Airflow BashOperator](#airflow-bashoperator)
    - [A note on Feast feature servers + push servers](#a-note-on-feast-feature-servers--push-servers)
- [Conclusion](#conclusion)
- [FAQ](#faq)
    - [How do you synchronize materialized features with pushed features from streaming?](#how-do-you-synchronize-materialized-features-with-pushed-features-from-streaming)
    - [Does Feast allow pushing features to the offline store?](#does-feast-allow-pushing-features-to-the-offline-store)
    - [Can feature / push servers refresh their registry in response to an event? e.g. after a PR merges and `feast apply` is run?](#can-feature--push-servers-refresh-their-registry-in-response-to-an-event-eg-after-a-pr-merges-and-feast-apply-is-run)
    - [How do I speed up or scale up materialization?](#how-do-i-speed-up-or-scale-up-materialization)

# Workshop
## Step 1: Install Feast

First, we install Feast with Spark and Redis support:
```bash
pip install "feast[spark,redis]"
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

## Step 4: Spin up Kafka + Redis + Feast services

We then use Docker Compose to spin up the services we need.
- This leverages a script (in `kafka_demo/`) that creates a topic, reads from `feature_repo/data/driver_stats.parquet`, generates newer timestamps, and emits them to the topic.
- This also deploys an instance of Redis.
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
  - **Note:** Feast will, in the future, also support directly authoring a `StreamFeatureView` that contains stream transformations / aggregations (e.g. via Spark, Flink, or Bytewax)
- Materializing feature view values from batch sources to the online store (e.g. Redis).
- Ingesting feature view values from streaming sources (e.g. window aggregate features from Spark + Kafka)
- Retrieve features at low latency from Redis through Feast.
- Working with a Feast push server + feature server to ingest and retrieve features through HTTP endpoints (instead of needing `feature_store.yaml` and `FeatureStore` instances)

Run the Jupyter notebook ([feature_repo/workshop.ipynb](feature_repo/module_1.ipynb)).

### Scheduling materialization
To ensure fresh features, you'll want to schedule materialization jobs regularly. This can be as simple as having a cron job that calls `feast materialize-incremental`.

Users may also be interested in integrating with Airflow, in which case you can build a custom Airflow image with the Feast SDK installed, and then use a `BashOperator` (with `feast materialize-incremental`) or `PythonOperator` (with `store.materialize_incremental(datetime.datetime.now())`).

We setup a standalone version of Airflow to 

#### Airflow PythonOperator

```python
# Define Python callable
def materialize():
  repo_config = RepoConfig(
    registry=RegistryConfig(path="s3://[YOUR BUCKET]/registry.pb"),
    project="feast_demo_aws",
    provider="aws",
    offline_store="file",
    online_store=DynamoDBOnlineStoreConfig(region="us-west-2")
  )
  store = FeatureStore(config=repo_config)
  store.materialize_incremental(datetime.datetime.now())

# Use PythonOperator
materialize_python = PythonOperator(
    task_id='materialize_python',
    python_callable=materialize,
)
```

#### Airflow BashOperator
```python
# Use BashOperator
materialize_bash = BashOperator(
    task_id='materialize',
    bash_command=f'feast materialize-incremental {datetime.datetime.now().replace(microsecond=0).isoformat()}',
)
```

See also [FAQ: How do I speed up or scale up materialization?](#how-do-i-speed-up-or-scale-up-materialization)

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
Not yet! See more details at https://github.com/feast-dev/feast/issues/2732

Many users have asked for this functionality as a quick way to get started, but often users work with two flows:
- To power the online store, using stream processing to generate fresh features and pushing to the online store
- To power the offline store, using some ETL / ELT pipelines that process and clean the raw data.

Though this is more complex, one key advantage of this is that you can construct new features based on the data while iterating on model training. If you rely on streaming features to generate historical feature values, then you need to rely on a log-and-wait approach, which can slow down model iteration.

### Can feature / push servers refresh their registry in response to an event? e.g. after a PR merges and `feast apply` is run?
Unfortunately, currently the servers don't support this. Feel free to contribute a PR though to enable this! The tricky part here is that Feast would need to keep track of these servers in the registry (or in some other way), which is not the way Feast is currently designed.

### How do I speed up or scale up materialization?
Materialization in Feast by default pulls the latest feature values for each unique entity locally and writes in batches to the online store.

- Feast users can materialize multiple feature views by using the CLI:
`feast materialize-incremental [FEATURE_VIEW_NAME]`
  - **Caveat**: By default, Feast's registry store is a single protobuf written to a file. This means that there's the chance that metadata around materialization intervals gets lost if the registry has changed during materialization.
    - The community is ideating on how to improve this. See [RFC-035: Scalable Materialization](https://docs.google.com/document/d/1tCZzClj3H8CfhJzccCytWK-bNDw_lkZk4e3fUbPYIP0/edit#)
- Users often also implement their own custom providers. The provider interface has a `materialize_single_feature_view` method, which users are free to implement differently (e.g. materializing with Spark or Dataflow jobs).

In general, the community is actively investigating ways to speed up materialization. Contributions are welcome!