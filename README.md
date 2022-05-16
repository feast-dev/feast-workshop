![](images/feast_logo.png)
## Workshop: Learning Feast

This workshop aims to teach users about [Feast](http://feast.dev), an open-source feature store. 

We explain concepts & best practices by example, and also showcase how to address common use cases.

<img src="images/hero.png" width=600 style="padding: 5px; background-color: white">

### Pre-requisites
This workshop assumes you have the following installed:
- A local development environment that supports running Jupyter notebooks (e.g. VSCode with Jupyter plugin)
- Python 3.7+
- pip
- Docker & Docker Compose (e.g. `brew install docker docker-compose`)

Since we'll be learning how to leverage Feast in CI/CD, you'll also need to fork this workshop repository.

## Modules
*See also: [Feast quickstart](https://docs.feast.dev/getting-started/quickstart), [Feast x Great Expectations tutorial](https://docs.feast.dev/tutorials/validating-historical-features)*

These are meant mostly to be done in order, with examples building on previous concepts.

| Time (min) | Description                                                             | Module&nbsp;&nbsp;&nbsp;       |
| :--------- | :---------------------------------------------------------------------- | ------------------------------ |
| 30-45      | Setting up Feast projects & CI/CD + powering batch predictions          | [Module 0](module_0/README.md) |
| 10-15      | Streaming ingestion & online feature retrieval with Kafka, Spark, Redis | [Module 1](module_1/README.md) |
| 10         | On demand feature views                                                 | [Module 2](module_2/README.md) |
| TBD        | Feature server deployment (embed, as a service, AWS Lambda)             | TBD                            |
| TBD        | Versioning features / models in Feast                                   | TBD                            |
| TBD        | Data quality monitoring in Feast                                        | TBD                            |

