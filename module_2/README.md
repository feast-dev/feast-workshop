<h1>Module 2: On demand transformations</h1>

In this module, we introduce the concept of on demand transforms. These are transformations that execute on-the-fly and accept as input other feature views or request data.

TODO:
- add architecture
- Define request data
- Define on demand transforms
  - Note that this can also transforms pushed features (e.g. stream features)
  - Note that this can combine multiple feature views and request data

<h2>Table of Contents</h2>

- [Workshop](#workshop)
  - [Step 1: Install Feast](#step-1-install-feast)
  - [Step 2: Look at the data we have](#step-2-look-at-the-data-we-have)
  - [Step 3: Apply features](#step-3-apply-features)
  - [Step 3: Materialize batch features](#step-3-materialize-batch-features)
  - [Step 4: Test retrieve features](#step-4-test-retrieve-features)
- [Conclusion](#conclusion)
  
# Workshop
## Step 1: Install Feast

First, we install Feast as well as a Geohash module we want to use:
```bash
pip install feast
pip install pygeohash
```

## Step 2: Look at the data we have
We used `data/gen_lat_lon.py` to append randomly generated latitude and longitudes to the original driver stats dataset.

```python
import pandas as pd
pd.read_parquet("data/driver_stats_lat_lon.parquet")
```

![](data.png)

## Step 3: Apply features
```console
$ feast apply

Created entity driver
Created feature view driver_daily_features
Created feature view driver_hourly_stats
Created on demand feature view transformed_conv_rate
Created on demand feature view avg_hourly_miles_driven
Created on demand feature view location_features_from_push
Created feature service model_v3
Created feature service model_v2
Created feature service model_v1

Created sqlite table feast_demo_odfv_driver_daily_features
Created sqlite table feast_demo_odfv_driver_hourly_stats
```

## Step 3: Materialize batch features
```console
$ feast materialize-incremental $(date +%Y-%m-%d)

Materializing 2 feature views to 2022-05-17 12:41:18-04:00 into the sqlite online store.

driver_hourly_stats from 1748-08-01 16:41:20-04:56:02 to 2022-05-17 12:41:18-04:00:
100%|████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 495.03it/s]
driver_daily_features from 1748-08-01 16:41:20-04:56:02 to 2022-05-17 12:41:18-04:00:
100%|███████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 1274.48it/s]
```

## Step 4: Test retrieve features 
Now we'll see how these transformations are executed offline at `get_historical_features` and online at `get_online_features` time. We'll also see how `OnDemandFeatureView` interacts with request data, regular feature views, and streaming / push features.

Try out the Jupyter notebook in [client/module_2_client.ipynb](client/module_2_client.ipynb). This is in a separate directory that contains just a `feature_store.yaml`.

# Conclusion
TODO