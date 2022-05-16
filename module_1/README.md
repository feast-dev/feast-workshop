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

## Step 3: Setting up push servers + feature servers
TODO
- Have some feature servers be read-only (for `/get_online_features`)
  - (pre-alpha): with `go_feature_retrieval=True` and a `LoggingConfig`, the feature server will also log served features to the offline store.
- Have some feature servers be write-only (for `/push`)