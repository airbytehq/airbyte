# Milvus

## Overview

This page guides you through the process of setting up the [Milvus](https://milvus.io/) destination connector.

There are three parts to this:

- Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
- Embedding - convert the text into a vector representation using a pre-trained model (Currently, OpenAI's `text-embedding-ada-002` and Cohere's `embed-english-light-v2.0` are supported.)
- Indexing - store the vectors in a vector database for similarity search

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

| Feature                        | Supported? | Notes                       |
| :----------------------------- | :--------- | :-------------------------- |
| Full Refresh Sync              | Yes        |                             |
| Incremental - Append Sync      | Yes        |                             |
| Incremental - Append + Deduped | Yes        |                             |
| Partitions                     | No         |                             |
| Record-defined ID              | No         | Auto-id needs to be enabled |

## Configuration

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Options around configuring the chunking process use the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

If the specified collection doesn't exist, the connector will create it for you with a primary key field `pk` and the configured vector field matching the embedding configuration. Dynamic fields will be enabled. The vector field will have an L2 IVF_FLAT index with an `nlist` parameter of 1024.

If you want to change any of these settings, create a new collection in your Milvus instance yourself. Make sure that

- The primary key field is set to [auto_id](https://milvus.io/docs/create_collection.md)
- There is a vector field with the correct dimensionality (1536 for OpenAI, 1024 for Cohere) and [a configured index](https://milvus.io/docs/build_index.md)

If the record contains a field with the same name as the primary key, it will be prefixed with an underscore so Milvus can control the primary key internally.

### Setting up a collection

When using the Zilliz cloud, this can be done using the UI - in this case only the collection name and the vector dimensionality needs to be configured, the vector field with index will be automatically created under the name `vector`. Using the REST API, the following command will create the index:

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

When using a self-hosted Milvus cluster, the collection needs to be created using the Milvus CLI or Python client. The following commands will create a collection set up for loading data via Airbyte:

```python
from pymilvus import CollectionSchema, FieldSchema, DataType, connections, Collection

connections.connect() # connect to locally running Milvus instance without authentication

pk = FieldSchema(name="pk",dtype=DataType.INT64, is_primary=True, auto_id=True)
vector = FieldSchema(name="vector",dtype=DataType.FLOAT_VECTOR,dim=1536)
schema = CollectionSchema(fields=[pk, vector], enable_dynamic_field=True)
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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                                                                                             |
|:--------| :--------- | :-------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.0.30 | 2024-08-31 | [44960](https://github.com/airbytehq/airbyte/pull/44960) | Update dependencies |
| 0.0.29 | 2024-08-24 | [44754](https://github.com/airbytehq/airbyte/pull/44754) | Update dependencies |
| 0.0.28 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.0.27 | 2024-08-17 | [44242](https://github.com/airbytehq/airbyte/pull/44242) | Update dependencies |
| 0.0.26 | 2024-08-12 | [43776](https://github.com/airbytehq/airbyte/pull/43776) | Update dependencies |
| 0.0.25 | 2024-08-10 | [43619](https://github.com/airbytehq/airbyte/pull/43619) | Update dependencies |
| 0.0.24 | 2024-08-03 | [43111](https://github.com/airbytehq/airbyte/pull/43111) | Update dependencies |
| 0.0.23 | 2024-07-27 | [42823](https://github.com/airbytehq/airbyte/pull/42823) | Update dependencies |
| 0.0.22 | 2024-07-20 | [42213](https://github.com/airbytehq/airbyte/pull/42213) | Update dependencies |
| 0.0.21 | 2024-07-13 | [41793](https://github.com/airbytehq/airbyte/pull/41793) | Update dependencies |
| 0.0.20 | 2024-07-10 | [41495](https://github.com/airbytehq/airbyte/pull/41495) | Update dependencies |
| 0.0.19 | 2024-07-06 | [40632](https://github.com/airbytehq/airbyte/pull/40632) | Update dependencies |
| 0.0.18 | 2024-06-26 | [40537](https://github.com/airbytehq/airbyte/pull/40537) | Update dependencies |
| 0.0.17 | 2024-06-25 | [40446](https://github.com/airbytehq/airbyte/pull/40446) | Update dependencies |
| 0.0.16 | 2024-06-22 | [40161](https://github.com/airbytehq/airbyte/pull/40161) | Update dependencies |
| 0.0.15 | 2024-05-20 | [38276](https://github.com/airbytehq/airbyte/pull/38276) | Replace AirbyteLogger with logging.Logger |
| 0.0.14  | 2024-3-22  | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Update CDK & pytest version to fix security vulnerabilities                                                                                         |
| 0.0.13  | 2024-3-22  | [#35911](https://github.com/airbytehq/airbyte/pull/35911) | Move to poetry; Fix tests                                                                                                                           |
| 0.0.12  | 2023-12-11 | [#33303](https://github.com/airbytehq/airbyte/pull/33303) | Fix bug with embedding special tokens                                                                                                               |
| 0.0.11  | 2023-12-01 | [#32697](https://github.com/airbytehq/airbyte/pull/32697) | Allow omitting raw text                                                                                                                             |
| 0.0.10  | 2023-11-16 | [#32608](https://github.com/airbytehq/airbyte/pull/32608) | Support deleting records for CDC sources                                                                                                            |
| 0.0.9   | 2023-11-13 | [#32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema                                                                                                                                 |
| 0.0.8   | 2023-11-08 | [#31563](https://github.com/airbytehq/airbyte/pull/32262) | Auto-create collection if it doesn't exist                                                                                                          |
| 0.0.7   | 2023-10-23 | [#31563](https://github.com/airbytehq/airbyte/pull/31563) | Add field mapping option                                                                                                                            |
| 0.0.6   | 2023-10-19 | [#31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                     |
| 0.0.5   | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329) | Add OpenAI-compatible embedder option                                                                                                               |
| 0.0.4   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size                                                                                                                      |
| 0.0.3   | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820) | Update CDK                                                                                                                                          |
| 0.0.2   | 2023-08-25 | [#30689](https://github.com/airbytehq/airbyte/pull/30689) | Update CDK to support azure OpenAI embeddings and text splitting options, make sure primary key field is not accidentally set, promote to certified |
| 0.0.1   | 2023-08-12 | [#29442](https://github.com/airbytehq/airbyte/pull/29442) | Milvus connector with some embedders                                                                                                                |

</details>
