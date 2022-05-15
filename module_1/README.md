# Module 1: Serving fresh online features with Feast, Kafka, Redis

In module 1, we focus on building features for online serving, and keeping them fresh with a combination of batch feature materialization and stream feature ingestion. 

- **Data sources**: Kafka + File source
- **Online store**: Redis
- **Use case**: Predicting churn for drivers in real time.

## Setup

### Setting up Feast

First, we install Feast with Spark and Redis support:
```bash
pip install "feast[spark, redis]"
```

We have already set up a feature repository in [feature_repo/](feature_repo/). 

### Docker + Kafka + Redis

We then use Docker Compose to spin up a local Kafka cluster and automatically publish events to it. 
- This leverages a script (in `kafka_demo/`) that creates a topic, reads from `feature_repo/data/driver_stats.parquet`, generates newer timestamps, and emits them to the topic.

Start up the Docker daemon and then use Docker Compose to spin up the services as described above:
```console
$ docker-compose up

Creating network "module_1_default" with the default driver
Creating redis     ... done
Creating zookeeper ... done
Creating broker    ... done
Creating kafka_events ... done
Attaching to zookeeper, redis, broker, kafka_events
...
```

## Continue with the workshop

Now run the Jupyter notebook ([feature_repo/workshop.ipynb](feature_repo/module_1.ipynb))
