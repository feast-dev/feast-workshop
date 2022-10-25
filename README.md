

## <img src="images/feast_icon.png" width=20>&nbsp; Workshop: Learning Feast 

This workshop aims to teach users about [Feast](http://feast.dev), an open-source feature store. 

We explain concepts & best practices by example, and also showcase how to address common use cases.

### What is Feast?
Feast is an operational system for managing and serving machine learning features to models in production. It can serve features from a low-latency online store (for real-time prediction) or from an offline store (for  batch scoring). 

<img src="images/feast_marchitecture.png" width=750>

### What is Feast not?
- Feast does not orchestrate data pipelines (e.g. batch / stream transformation or materialization jobs), but provides a framework to integrate with adjacent tools like dbt, Airflow, and Spark.
- Feast also does not solve other commonly faced issues like data quality, experiment management, etc. 

See more details at [What Feast is not](https://docs.feast.dev/#what-feast-is-not).

### Why Feast?
Feast solves several common challenges teams face:
1. Lack of feature reuse across teams
2. Complex point-in-time-correct data joins for generating training data
3. Difficulty operationalizing features for online inference while minimizing training / serving skew

### Pre-requisites
This workshop assumes you have the following installed:
- A local development environment that supports running Jupyter notebooks (e.g. VSCode with Jupyter plugin)
- Python 3.8+
- pip
  - Docker & Docker Compose (e.g. `brew install docker docker-compose`)
- **Module 0 pre-requisites**:
  - Terraform ([docs](https://learn.hashicorp.com/tutorials/terraform/install-cli#install-terraform))
  - Either AWS or GCP setup:
    - AWS
      - AWS CLI
      - An AWS account setup with credentials via `aws configure` (e.g see [AWS credentials quickstart](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds))
    - GCP
      - GCP account
      - `gcloud` CLI
- **Module 1 pre-requisites**:
  - Java 11 (for Spark, e.g. `brew install java11`)

Since we'll be learning how to leverage Feast in CI/CD, you'll also need to fork this workshop repository.

**Caveats** 
- M1 Macbook development is untested with this flow. See also [How to run / develop for Feast on M1 Macs](https://github.com/feast-dev/feast/issues/2105).
- Windows development has only been tested with WSL. You will need to follow this [guide](https://docs.docker.com/desktop/windows/wsl/) to have Docker play nicely.

## Modules
*See also: [Feast quickstart](https://docs.feast.dev/getting-started/quickstart), [Feast x Great Expectations tutorial](https://docs.feast.dev/tutorials/validating-historical-features)*

These are meant mostly to be done in order, with examples building on previous concepts.

| Time (min) | Description                                                                      | Module&nbsp;&nbsp;&nbsp;       |
| :--------: | :------------------------------------------------------------------------------- | :----------------------------- |
|   30-45    | Setting up Feast projects & CI/CD + powering batch predictions                   | [Module 0](module_0/README.md) |
|   15-20    | Streaming ingestion & online feature retrieval with Kafka, Spark, Airflow, Redis | [Module 1](module_1/README.md) |
|   10-15    | Real-time feature engineering with on demand transformations                     | [Module 2](module_2/README.md) |
|     30     | (WIP) Orchestrated batch/stream transformations using dbt + Airflow with Feast   | [Module 3](module_3/README.md) |