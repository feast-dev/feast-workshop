# Module 1: Streaming ingestion & online feature retrieval with Kafka, Spark, Redis

In this module, we focus on building features for online serving, and keeping them fresh with a combination of batch feature materialization and stream feature ingestion. We'll be roughly working towards the following:

- **Data sources**: Kafka + File source
- **Online store**: Redis
- **Use case**: Predicting churn for drivers in real time.

<img src="architecture.png" width=750>

## Setup

### Setting up Feast

First, we install Feast with Spark and Redis support:
```bash
pip install "feast[spark,redis]"
```

### Step 1: Docker + Kafka + Redis

We then use Docker Compose to spin up a local Kafka cluster and automatically publish events to it. 
- This leverages a script (in `kafka_demo/`) that creates a topic, reads from `feature_repo/data/driver_stats.parquet`, generates newer timestamps, and emits them to the topic.
- This also deploys a Feast push server + a Feast feature server. The Dockerfile mostly delegates to calling the `feast serve` CLI command:
  ```yaml
  FROM python:3.7

  RUN pip install "feast[redis]"

  COPY feature_repo/feature_store.yaml feature_store.yaml

  # Needed to reach online store within Docker network.
  RUN sed -i 's/localhost:6379/redis:6379/g' feature_store.yaml
  ENV FEAST_USAGE=False

  CMD ["feast", "serve", "-h", "0.0.0.0"]
  ```

Start up the Docker daemon and then use Docker Compose to spin up the services as described above:
```console
$ docker-compose up

Creating network "module_1_default" with the default driver
Creating zookeeper ... done
Creating redis     ... done
Creating broker               ... done
Creating feast_feature_server ... done
Creating feast_push_server    ... done
Creating kafka_events         ... done
Attaching to zookeeper, redis, broker, feast_push_server, feast_feature_server, kafka_events
...
```

## Step 2: Materialize batch features & ingest streaming features

Run the Jupyter notebook ([feature_repo/workshop.ipynb](feature_repo/module_1.ipynb)).

This will guide you through:
- Registering a `FeatureView` that has a single schema across both a batch source (`FileSource`) with aggregate features and a stream source (`PushSource`).
  - **Note:** Feast will, in the future, also support directly authoring a `StreamFeatureView` that contains stream transformations / aggregations (e.g. via Spark, Flink, or Bytewax)
- Materializing feature view values from batch sources to the online store (e.g. Redis).
- Ingesting feature view values from streaming sources (e.g. window aggregate features from Spark + Kafka)
- Retrieve features at low latency from Redis through Feast.
- Working with a Feast push server + feature server to ingest and retrieve features through HTTP endpoints (instead of needing `feature_store.yaml` and `FeatureStore` instances)

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
- Feast adds a convenience wrapper though so if you specify just `registry: [path]`, Feast will map that to `RegistryConfig(path=[your path])`.

## FAQ

### Can feature / push servers refresh their registry in response to an event? e.g. after a PR merges and `feast apply` is run?
Unfortunately, currently the servers don't support this. Feel free to contribute a PR though to enable this! The tricky part here is that Feast would need to keep track of these servers in the registry (or in some other way), which is not the way Feast is currently designed.

### How do I scale up materialization?
Materialization in Feast by default pulls the latest feature values for each unique entity locally and writes in batches to the online store.

- Feast users can materialize multiple feature views by using the CLI:
`feast materialize-incremental [FEATURE_VIEW_NAME]`
  - **Caveat**: By default, Feast's registry store is a single protobuf written to a file. This means that there's the chance that metadata around materialization intervals gets lost if the registry has changed during materialization.
    - The community is ideating on how to improve this. See [RFC-035: Scalable Materialization](https://docs.google.com/document/d/1tCZzClj3H8CfhJzccCytWK-bNDw_lkZk4e3fUbPYIP0/edit#)
- Users often also implement their own custom providers. The provider interface has a `materialize_single_feature_view` method, which users are free to implement differently (e.g. materializing with Spark or Dataflow jobs).

In general, the community is actively investigating ways to speed up materialization. Contributions are welcome!