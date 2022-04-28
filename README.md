# Feast Spark + Kafka workshop

## Overview

This workshop focuses on how to achieve a common architecture:

TODO: add architecture diagram

- **Data sources**: Kafka + File source
- **Online store**: Redis
- **Use cases**: Predicting churn for drivers 
  - Batch scoring via offline store
  - Real time scoring via online store

We will generate a model that will predict whether a driver will churn

## Setup

### Docker + Kafka + Redis
First, we need Docker and Docker Compose
```
brew install docker docker-compose
```

We then install the requirements:
```
pip install -r requirements.txt
```

We then spin up a local Kafka cluster that generates events into a topic.

```
docker-compose up
```

### Generate a topic
If you run `python kafka_demo.py`, we now start generating streaming events from the parquet file continously (with sleeps to slow down event writes). We hard-code events to be a year fresher than what is available in the file.

### Register a push source
This push source reflects the transformed features you're generating in Spark Structured Streaming. Here, we have a push source that will materialize the transformed features from the batch file source as well as push transformed features into the online store from a Push API.

```python
driver_stats = FileSource(
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
    description="A table describing the stats of a driver based on hourly logs",
    owner="test@gmail.com",
)

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