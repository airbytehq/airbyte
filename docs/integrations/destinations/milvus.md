# Milvus

## Overview

This page guides you through the process of setting up the [Milvus](https://milvus.io/) destination connector.

There are three parts to this:
* Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
* Embedding - convert the text into a vector representation using a pre-trained model (Currently, OpenAI's `text-embedding-ada-002` and Cohere's `embed-english-light-v2.0` are supported.)
* Indexing - store the vectors in a vector database for similarity search

## Prerequisites

To use the Milvus destination, you'll need:

- An account with API access for OpenAI or Cohere (depending on which embedding method you want to use)
- Either a running self-managed Milvus instance or a [Zilliz](https://zilliz.com/) account

You'll need the following information to configure the destination:

- **Embedding service API Key** - The API key for your OpenAI or Cohere account
- **Milvus Endpoint URL** - The URL of your Milvus instance
- Either **Milvus API token** or **Milvus Instance Username and Password**
- **Milvus Collection name** - The name of the collection to load data into

## Features

| Feature                        | Supported?           | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  | Deleting records via CDC is not supported (see issue [#29827](https://github.com/airbytehq/airbyte/issues/29827))  |
| Partitions                     | No                   |       |
| Record-defined ID                     | No                   | Auto-id needs to be enabled |

## Configuration

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks.

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**. 

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

To get started, create a new collection in your Milvus instance. Make sure that
* The primary key field is set to [auto_id](https://milvus.io/docs/create_collection.md)
* There is a vector field with the correct dimensionality (1536 for OpenAI, 1024 for Cohere) and [a configured index](https://milvus.io/docs/build_index.md)

If the record contains a field with the same name as the primary key, it will be prefixed with an underscore so Milvus can control the primary key internally.

### Setting up a collection

When using the Zilliz cloud, this can be done using the UI - in this case only the colleciton name and the vector dimensionality needs to be configured, the vector field with index will be automatically created under the name `vector`. Using the REST API, the following command will create the index:
```
POST /v1/vector/collections/create
{
  "collectionName": "my-collection",
  "dimension": 1536,
  "metricType": "L2",
  "vectorField": "vector",
  “primaryField”: “pk”
}
```

When using a self-hosted Milvus clustger, the collection needs to be created using the Milvus CLI or Python client. The following commands will create a collection set up for loading data via Airbyte:
```python
from pymilvus import CollectionSchema, FieldSchema, DataType

pk = FieldSchema(name="pk",dtype=DataType.INT64, is_primary=True, auto_id=True)
vector = FieldSchema(name="vector",dtype=DataType.FLOAT_VECTOR,dim=1536)
schema = CollectionSchema(fields=[id, vector], enable_dynamic_field=True)
collection = Collection(name="test_collection", schema=schema)
collection.create_index(field_name="vector", index_params={ "metric_type":"L2", "index_type":"IVF_FLAT", "params":{"nlist":1024} })
```

### Langchain integration

To initialize a langchain vector store based on the indexed data, use the following code:
```python
embeddings = OpenAIEmbeddings(openai_api_key="my-key")
vector_store = Milvus(embeddings=embeddings, collection_name="my-collection", connection_args={"uri": "my-zilliz-endpoint", "token": "my-api-key"})
vector_store.fields.append("text")
# call  vs.fields.append() for all fields you need from the metadata

vector_store.similarity_search("test")
```


## CHANGELOG

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.0.5 | 2023-10-16 | [TBDGUS](https://github.com/airbytehq/airbyte/pull/TBDGUS) | Use our base image and remove Dockerfile |
| 0.0.4   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size |
| 0.0.3   | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820)     | Update CDK | 
| 0.0.2   | 2023-08-25 | [#30689](https://github.com/airbytehq/airbyte/pull/30689)     | Update CDK to support azure OpenAI embeddings and text splitting options, make sure primary key field is not accidentally set, promote to certified | 

## Build instructions

### Use `airbyte-ci` to build your connector
The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name destination-milvus build
```

### Build your own connector image
This connector is built using our dynamic built process.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be to:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/destination-milvus:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/destination-milvus:dev .
# Running the spec command against your patched connector
docker run airbyte/destination-milvus:dev spec
```

### Customizing our build process
When contributing on our connector you might need to customize the build process to add a system dependency or set an env var.
You can customize our build process by adding a `build_customization.py` module to your connector.
This module should contain a `pre_connector_install` and `post_connector_install` async function that will mutate the base image and the connector container respectively.
It will be imported at runtime by our build process and the functions will be called if they exist.

Here is an example of a `build_customization.py` module:
```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Feel free to check the dagger documentation for more information on the Container object and its methods.
    # https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    return await base_image_container.with_env_variable("MY_PRE_BUILD_ENV_VAR", "my_pre_build_env_var_value")

async def post_connector_install(connector_container: Container) -> Container:
    return await connector_container.with_env_variable("MY_POST_BUILD_ENV_VAR", "my_post_build_env_var_value")
```
| 0.0.1   | 2023-08-12 | [#29442](https://github.com/airbytehq/airbyte/pull/29442)     | Milvus connector with some embedders  | 