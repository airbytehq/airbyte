# Pinecone

## Overview

This page guides you through the process of setting up the [Pinecone](https://pinecone.io/) destination connector.

There are three parts to this:

- Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
- Embedding - convert the text into a vector representation using a pre-trained model (Currently, OpenAI's `text-embedding-ada-002` and Cohere's `embed-english-light-v2.0` are supported.)
- Indexing - store the vectors in a vector database for similarity search

## Prerequisites

To use the Pinecone destination, you'll need:

- An account with API access for OpenAI or Cohere (depending on which embedding method you want to use)
- A Pinecone project with a pre-created index with the correct dimensionality based on your embedding method

You'll need the following information to configure the destination:

- **Embedding service API Key** - The API key for your OpenAI or Cohere account
- **Pinecone API Key** - The API key for your Pinecone account
- **Pinecone Environment** - The name of the Pinecone environment to use
- **Pinecone Index name** - The name of the Pinecone index to load data into

## Features

| Feature                        | Supported? | Notes                                                                                                             |
| :----------------------------- | :--------- | :---------------------------------------------------------------------------------------------------------------- |
| Full Refresh Sync              | Yes        |                                                                                                                   |
| Incremental - Append Sync      | Yes        |                                                                                                                   |
| Incremental - Append + Deduped | Yes        | Deleting records via CDC is not supported (see issue [#29827](https://github.com/airbytehq/airbyte/issues/29827)) |
| Namespaces                     | Yes        |                                                                                                                   |

## Data type mapping

All fields specified as metadata fields will be stored in the metadata object of the document and can be used for filtering. The following data types are allowed for metadata fields:

- String
- Number (integer or floating point, gets converted to a 64 bit floating point)
- Booleans (true, false)
- List of String

All other fields are ignored.

## Configuration

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Please note that meta data fields can only be used for filtering and not for retrieval and have to be of type string, number, boolean (all other values are ignored). Please note that there's a 40kb limit on the _total_ size of the metadata saved for each entry. Options around configuring the chunking process use the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

To get started, use the [Pinecone web UI or API](https://docs.pinecone.io/docs/quickstart) to create a project and an index before running the destination. All streams will be indexed into the same index, the `_ab_stream` metadata field is used to distinguish between streams. Overall, the size of the metadata fields is limited to 30KB per document.

OpenAI and Fake embeddings produce vectors with 1536 dimensions, and the Cohere embeddings produce vectors with 1024 dimensions. Make sure to configure the index accordingly.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                                                                      |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| 0.1.39 | 2025-02-22 | [54255](https://github.com/airbytehq/airbyte/pull/54255) | Update dependencies |
| 0.1.38 | 2025-02-15 | [53879](https://github.com/airbytehq/airbyte/pull/53879) | Update dependencies |
| 0.1.37 | 2025-02-08 | [53434](https://github.com/airbytehq/airbyte/pull/53434) | Update dependencies |
| 0.1.36 | 2025-02-01 | [52908](https://github.com/airbytehq/airbyte/pull/52908) | Update dependencies |
| 0.1.35 | 2025-01-25 | [51762](https://github.com/airbytehq/airbyte/pull/51762) | Update dependencies |
| 0.1.34 | 2025-01-11 | [51245](https://github.com/airbytehq/airbyte/pull/51245) | Update dependencies |
| 0.1.33 | 2025-01-04 | [50904](https://github.com/airbytehq/airbyte/pull/50904) | Update dependencies |
| 0.1.32 | 2024-12-28 | [50480](https://github.com/airbytehq/airbyte/pull/50480) | Update dependencies |
| 0.1.31 | 2024-12-21 | [50203](https://github.com/airbytehq/airbyte/pull/50203) | Update dependencies |
| 0.1.30 | 2024-12-14 | [49303](https://github.com/airbytehq/airbyte/pull/49303) | Update dependencies |
| 0.1.29 | 2024-11-25 | [48654](https://github.com/airbytehq/airbyte/pull/48654) | Update dependencies |
| 0.1.28 | 2024-11-05 | [48323](https://github.com/airbytehq/airbyte/pull/48323) | Update dependencies |
| 0.1.27 | 2024-10-29 | [47106](https://github.com/airbytehq/airbyte/pull/47106) | Update dependencies |
| 0.1.26 | 2024-10-12 | [46782](https://github.com/airbytehq/airbyte/pull/46782) | Update dependencies |
| 0.1.25 | 2024-10-05 | [46474](https://github.com/airbytehq/airbyte/pull/46474) | Update dependencies |
| 0.1.24 | 2024-09-28 | [46127](https://github.com/airbytehq/airbyte/pull/46127) | Update dependencies |
| 0.1.23 | 2024-09-21 | [45791](https://github.com/airbytehq/airbyte/pull/45791) | Update dependencies |
| 0.1.22 | 2024-09-14 | [45490](https://github.com/airbytehq/airbyte/pull/45490) | Update dependencies |
| 0.1.21 | 2024-09-07 | [45247](https://github.com/airbytehq/airbyte/pull/45247) | Update dependencies |
| 0.1.20 | 2024-08-31 | [45063](https://github.com/airbytehq/airbyte/pull/45063) | Update dependencies |
| 0.1.19 | 2024-08-24 | [44669](https://github.com/airbytehq/airbyte/pull/44669) | Update dependencies |
| 0.1.18 | 2024-08-17 | [44302](https://github.com/airbytehq/airbyte/pull/44302) | Update dependencies |
| 0.1.17 | 2024-08-12 | [43932](https://github.com/airbytehq/airbyte/pull/43932) | Update dependencies |
| 0.1.16 | 2024-08-10 | [43701](https://github.com/airbytehq/airbyte/pull/43701) | Update dependencies |
| 0.1.15 | 2024-08-03 | [43134](https://github.com/airbytehq/airbyte/pull/43134) | Update dependencies |
| 0.1.14 | 2024-07-27 | [42594](https://github.com/airbytehq/airbyte/pull/42594) | Update dependencies |
| 0.1.13 | 2024-07-20 | [42243](https://github.com/airbytehq/airbyte/pull/42243) | Update dependencies |
| 0.1.12 | 2024-07-13 | [41901](https://github.com/airbytehq/airbyte/pull/41901) | Update dependencies |
| 0.1.11 | 2024-07-10 | [41598](https://github.com/airbytehq/airbyte/pull/41598) | Update dependencies |
| 0.1.10 | 2024-07-09 | [41194](https://github.com/airbytehq/airbyte/pull/41194) | Update dependencies |
| 0.1.9 | 2024-07-07 | [40753](https://github.com/airbytehq/airbyte/pull/40753) | Fix a regression with AirbyteLogger |
| 0.1.8 | 2024-07-06 | [40780](https://github.com/airbytehq/airbyte/pull/40780) | Update dependencies |
| 0.1.7 | 2024-06-29 | [40627](https://github.com/airbytehq/airbyte/pull/40627) | Update dependencies |
| 0.1.6 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.5 | 2024-06-25 | [40430](https://github.com/airbytehq/airbyte/pull/40430) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40150](https://github.com/airbytehq/airbyte/pull/40150) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39148](https://github.com/airbytehq/airbyte/pull/39148) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2   | 2023-05-17 | [#38336](https://github.com/airbytehq/airbyte/pull/338336) | Fix for regression:Custom namespaces not created automatically
| 0.1.1   | 2023-05-14 | [#38151](https://github.com/airbytehq/airbyte/pull/38151) | Add airbyte source tag for attribution
| 0.1.0   | 2023-05-06 | [#37756](https://github.com/airbytehq/airbyte/pull/37756) | Add support for Pinecone Serverless                                                                                          |
| 0.0.24  | 2023-04-15 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Update CDK & pytest version to fix security vulnerabilities.                                                                 |
| 0.0.23  | 2023-03-22 | [#35911](https://github.com/airbytehq/airbyte/pull/35911) | Bump versions to latest, resolves test failures.                                                                             |
| 0.0.22  | 2023-12-11 | [#33303](https://github.com/airbytehq/airbyte/pull/33303) | Fix bug with embedding special tokens                                                                                        |
| 0.0.21  | 2023-12-01 | [#32697](https://github.com/airbytehq/airbyte/pull/32697) | Allow omitting raw text                                                                                                      |
| 0.0.20  | 2023-11-13 | [#32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema                                                                                                          |
| 0.0.19  | 2023-10-20 | [#31329](https://github.com/airbytehq/airbyte/pull/31373) | Improve error messages                                                                                                       |
| 0.0.18  | 2023-10-20 | [#31329](https://github.com/airbytehq/airbyte/pull/31373) | Add support for namespaces and fix index cleaning when namespace is defined                                                  |
| 0.0.17  | 2023-10-19 | [#31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                                              |
| 0.0.16  | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329) | Add OpenAI-compatible embedder option                                                                                        |
| 0.0.15  | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size                                                                                               |
| 0.0.14  | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820) | Update CDK                                                                                                                   |
| 0.0.13  | 2023-09-26 | [#30649](https://github.com/airbytehq/airbyte/pull/30649) | Allow more text splitting options                                                                                            |
| 0.0.12  | 2023-09-25 | [#30649](https://github.com/airbytehq/airbyte/pull/30649) | Fix bug with stale documents left on starter pods                                                                            |
| 0.0.11  | 2023-09-22 | [#30649](https://github.com/airbytehq/airbyte/pull/30649) | Set visible certified flag                                                                                                   |
| 0.0.10  | 2023-09-20 | [#30514](https://github.com/airbytehq/airbyte/pull/30514) | Fix bug with failing embedding step on large records                                                                         |
| 0.0.9   | 2023-09-18 | [#30510](https://github.com/airbytehq/airbyte/pull/30510) | Fix bug with overwrite mode on starter pods                                                                                  |
| 0.0.8   | 2023-09-14 | [#30296](https://github.com/airbytehq/airbyte/pull/30296) | Add Azure embedder                                                                                                           |
| 0.0.7   | 2023-09-13 | [#30382](https://github.com/airbytehq/airbyte/pull/30382) | Promote to certified/beta                                                                                                    |
| 0.0.6   | 2023-09-09 | [#30193](https://github.com/airbytehq/airbyte/pull/30193) | Improve documentation                                                                                                        |
| 0.0.5   | 2023-09-07 | [#30133](https://github.com/airbytehq/airbyte/pull/30133) | Refactor internal structure of connector                                                                                     |
| 0.0.4   | 2023-09-05 | [#30086](https://github.com/airbytehq/airbyte/pull/30079) | Switch to GRPC client for improved performance.                                                                              |
| 0.0.3   | 2023-09-01 | [#30079](https://github.com/airbytehq/airbyte/pull/30079) | Fix bug with potential data loss on append+dedup syncing. 🚨 Streams using append+dedup mode need to be reset after upgrade. |
| 0.0.2   | 2023-08-31 | [#29442](https://github.com/airbytehq/airbyte/pull/29946) | Improve test coverage                                                                                                        |
| 0.0.1   | 2023-08-29 | [#29539](https://github.com/airbytehq/airbyte/pull/29539) | Pinecone connector with some embedders                                                                                       |

</details>
