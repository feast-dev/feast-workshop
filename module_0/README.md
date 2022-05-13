# Module 0: Setting up a feature repo, sharing features, batch predictions

Welcome! Here we use a basic example to explain key concepts and user flows in Feast. 

We focus on a specific example (that does not include online features + models):
- **Use case**: building a platform for data scientists to share features for training offline models
- **Stack**: you have data in a combination of data warehouses (to be explored in a future module) and data lakes (e.g. S3)

# 1. Mapping to Feast concepts
To support this, you'll need:
| Concept         | Requirements                                                                                          |
| :-------------- | :---------------------------------------------------------------------------------------------------- |
| Data sources    | `FileSource` (with S3 paths and endpoint overrides) and `FeatureView`s registered with `feast apply`  |
| Feature views   | Feature views tied to data sources that are shared by data scientists, registered with `feast apply`  |
| Provider        | In `feature_store.yaml`, specifying the `aws` provider to ensure your registry can be stored in S3    |
| Registry        | In `feature_store.yaml`, specifying a path (within an existing S3 bucket) the registry is written to. |
| Transformations | Feast supports last mile transformations with `OnDemandFeatureView` that can be re-used               |

# 2. User flows
There are three user groups here worth considering. The ML platform team, the data scientists, and the ML engineers scheduling models in batch. We visit the first two of these in 

## 2a. ML Platform Team
The team here sets up the centralized Feast feature repository in GitHub. This is what's seen in `feature_repo_aws/`.

### Step 1: Setup the feature repo
Here, the first thing a platform team needs to do is setup the `feature_store.yaml` within a version controlled repo like GitHub:

```yaml
project: feast_demo_aws
provider: aws
registry: s3://[YOUR BUCKET]/registry.pb
online_store: null
offline_store:
  type: file
flags:
  alpha_features: true
  on_demand_transforms: true
```

Some quick recap of what's happening here:
- `project` gives infrastructure isolation. 
  - Commonly, to start, users will start with one large project for multiple teams.
  - All Feast objects like `FeatureView`s have associated projects. Users can only request features from a single project.
  - Online stores (if used) namespace by project names 
- `provider` defines registry locations & sets defaults for offline / online stores options 
  - For example, the `gcp` provider will enable registries in GCS and sets BigQuery + Datastore as the default offline / online stores. 
  - Provider defaults can be easily overriden in `feature_store.yaml`
- `registry` defines the specific path for the registry
  - The Feast registry is the source of truth on registered Feast objects. 
    - Users + model servers will pull from this to get the latest registered features + metadata.  
  - **Note**: technically, multiple projects can use the same registry, though Feast was not designed with this in mind. Discovery of adjacent features is possible in this flow, but not retrieval.
- `online_store` here is set to null. 
  - If you don't need to power real time models with fresh features, this is not needed. 
  - If you are batch scoring, for example, then the online store is optional.
- `offline_store` defines the offline compute that executes point in time joins
  - Can only be one type (cannot mix Snowflake + file for example)
  - Here, for instruction purposes, we use `file` sources. 
    - This will directly read from files (local or remote) and use Dask to execute point-in-time joins. 
    - We **do not** recommend this for production usage.
  - We recommend users to use data warehouses as their offline store for performant training dataset generation. 
  - There is also a contrib plugin (`SparkOfflineStore`) which supports retrieving features with Spark.
- `flags` are the legacy way of controlling alpha features 
  - We're likely to deprecate this system soon, but today it still gates `OnDemandFeatureView` which is still under development.
  
With the `feature_store.yaml` setup, you can now run `feast apply` to create & populate the registry. 

### Step 2: Adding the feature repo to version control

<img src="ci_cd_flow.png" width=600 style="padding: 10px 0">

We setup CI/CD to automatically manage the registry. You'll want e.g. a GitHub workflow that
- on pull request, runs `feast plan` 
- on PR merge, runs `feast apply`.

#### **feast plan**
See [feast_plan.yml](https://github.com/feast-dev/feast-demo/blob/main/.github/workflows/feast_plan.yml) as an example of a workflow that automatically runs `feast plan` on new incoming PRs, which alerts you on what changes will occur. 
- This is useful for helping PR reviewers understand the effects of a change.
- One example is whether a PR may change features that are already depended on in production by another model (e.g. `FeatureService`). 

#### **feast apply**
This will parse the feature, data source, and feature service definitions and publish them to the registry. It may also setup some tables in the online store to materialize batch features to. 

Sample output of `feast apply`:
```bash
Registered entity driver_id
Registered feature view driver_hourly_stats
Deploying infrastructure for driver_hourly_stats
```

### Step 3 (optional): Access control for the registry
We don't dive into this deeply, but you don't want to allow arbitrary users to clone the feature repository, change definitions and run `feast apply`. Thus, you should lock down your registry (e.g. with an S3 bucket policy) to only allow changes from your CI/CD user and perhaps some ML engineers.

### Step 4 (optional): Setup a Web UI endpoint
Feast comes with an experimental Web UI. Users can already spin this up locally with `feast ui`, but you may want to have a Web UI that is universally available. Here, you'd likely deploy a service that runs `feast ui` on top of a `feature_store.yaml`, with some configuration on how frequently the UI should be refreshing its registry.

![Feast UI](sample_web_ui.png)

### Other best practices
Many Feast users use `tags` on objects extensively. Some examples of how this may be used:
- To give more detailed documentation on a `FeatureView`
- To highlight what groups you need to join to gain access to certain feature views.
- To denote whether a feature service is in production or in staging.

Additionally, users will often want to have a dev/staging environment that's separate from production. In this case, once pattern that works is to have separate projects:

```bash
├── .github
│   └── workflows
│       ├── production.yml
│       └── staging.yml
│
├── staging
│   ├── driver_repo.py
│   └── feature_store.yaml
│
└── production
    ├── driver_repo.py
    └── feature_store.yaml
```

## 2b. Data scientists
TODO

Two ways of working
- Use the `client/` folder approach of not authoring features and primarily re-using features already used in production.
- Have a local copy of the feature repository (e.g. `git clone`). Then the data scientist can iterate on features locally, apply features to their own dev project with a local registry, and then submit PRs to include features that should be used in production (including A/B experiments, or model training iterations)

Data scientists can also investigate other models and their dependent features / data sources / on demand transformations through the repository or through the Web UI (by running `feast ui`)

## 2c. ML engineers

Data scientists or ML engineers can use the defined `FeatureService` (corresponding to model versions) and schedule regular jobs that generate batch predictions (or regularly retrain).  

Feast right now requires timestamps in `get_historical_features`, so what you'll need to do is append an event timestamp of `now()`. e.g.

```python
# Get the latest feature values for unique entities
entity_df["event_timestamp"] = pd.to_datetime('now')
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=store.get_feature_service("model_v1")
).to_df()

# Make batch predictions
predictions = model.predict(training_df)
```

# Conclusion
As a result:
- You have file sources (possibly remote) and a remote registry (e.g. in S3)
- Data scientists are able to author + reuse features based on a centrally managed registry. 
- ML engineers are able to use these same features with a reference to the registry to regularly generating predictions on the latest timestamp.
- You have CI/CD setup to automatically update the registry + online store infrastructure when changes are merged into the version controlled feature repo. 
