# Module 2: Working with remote files and registries

In module 1, we worked with a local feature repository and materialized to local clusters.

In this module, we simulate a slightly more realistic scenario:
- You have file sources in S3
- You have a remote server that needs to call Feast to retrieve features, including executing on demand transformations to pass for model inference.
- As a result of having multiple services needing central access to a registry, you also have your registry stored in S3.
- You have multiple data scientists needing access to features

TODO
