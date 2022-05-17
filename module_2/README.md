# Module 2: On demand transformations
TODO

- Define request data
- Define on demand transforms
  - Note that this can also transforms pushed features (e.g. stream features)
  - Note that this can combine multiple feature views and request data


<h1>Module 2: On demand transformations</h1>

In this module, we introduce the concept of on demand transforms. These are transformations that execute on-the-fly and accept as input other feature views or request data.

We  and focus on building features for online serving, and keeping them fresh with a combination of batch feature materialization and stream feature ingestion. We'll be roughly working towards the following:

- **Data sources**: Kafka + File source
- **Online store**: Redis
- **Use case**: Predicting churn for drivers in real time.

<img src="architecture.png" width=750>

<h2>Table of Contents</h2>

# Workshop
## Step 1: Install Feast

First, we install Feast with Spark and Redis support:
```bash
pip install "feast[spark,redis]"
```