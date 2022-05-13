# Module 1: Serving fresh online features with Feast, Kafka, Redis

In module 1, we focus on building some test features and go through common flows in Feast

- **Data sources**: Kafka + File source
- **Online store**: Redis
- **Use case**: Predicting churn for drivers 
  - Batch scoring via offline store
  - Real time scoring via online store

## Setup

### Docker + Kafka + Redis
First, we install Feast with Redis support:
```
pip install "feast[redis]"
```

We then use Docker Compose to spin up a local Kafka cluster and automatically publish events to it. 
- This leverages a script (in `kafka_demo/`) that creates a topic, reads from `feature_repo/data/driver_stats.parquet`, generates newer timestamps, and emits them to the topic.

```
docker-compose up
```

### Setting up Feast

Install Feast using pip

```
pip install 'feast[redis]'
```

We have already set up a feature repository in [feature_repo/](feature_repo/). 

Deploy the feature store by running `apply` from within the `feature_repo/` folder
```
cd feature_repo/
feast apply
```

Output:
```
Created entity driver
Created feature view driver_hourly_stats
Created feature view driver_daily_features
Created on demand feature view transformed_conv_rate
Created feature service convrate_plus100

Deploying infrastructure for driver_hourly_stats
Deploying infrastructure for driver_daily_features
```

Next we load features into the online store using the `materialize-incremental` command. This command will load the
latest feature values from a data source into the online store.

```
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
feast materialize-incremental $CURRENT_TIME
```

Output:
```
Materializing 2 feature views to 2022-04-28 12:38:01-04:00 into the redis online store.

driver_hourly_stats from 1748-07-13 16:38:03-04:56:02 to 2022-04-28 12:38:01-04:00:
100%|████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 759.42it/s]
driver_daily_features from 1748-07-13 16:38:03-04:56:02 to 2022-04-28 12:38:01-04:00:
100%|███████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 1081.28it/s]
```

## Continue with the workshop

Now run the Jupyter notebook ([feature_repo/workshop.ipynb](feature_repo/workshop.ipynb))