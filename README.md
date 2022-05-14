# Workshop: Learning Feast

## Overview

This workshop aims to teach basic Feast concepts & best practices by example. We walk through how to address common use cases and architectures.

## Pre-requisites
This workshop assumes you have the following installed:
- A local development environment that supports running Jupyter notebooks (e.g. VSCode with Jupyter plugin)
- Python 3.7+
- pip
- Docker & Docker Compose (e.g. `brew install docker docker-compose`)

## Modules
*See also: [Feast quickstart](https://docs.feast.dev/getting-started/quickstart)*

These are meant mostly to be done in order, with examples building on previous concepts.

| Description                                                    | Module                         |
| :------------------------------------------------------------- | ------------------------------ |
| Setting up Feast projects & CI/CD + powering batch predictions | [Module 0](module_0/README.md) |
| Online feature retrieval with Kafka, Spark, Redis              | [Module 1](module_1/README.md) |
| On demand feature views                                        | [Module 2](module_2/README.md) |
| Versioning features / models in Feast                          | TBD                            |
| Data quality monitoring in Feast                               | TBD                            |
| Feature server deployment (embed, as a service, AWS Lambda)    | TBD                            |

