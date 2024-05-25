# Qdrant

This page guides you through the process of setting up the [Qdrant](https://qdrant.tech/documentation/) destination connector.

## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |

#### Output Schema

Only one stream will exist to collect payload and vectors (optional) from all source streams. This will be in a [collection](https://qdrant.tech/documentation/concepts/collections/) in [Qdrant](https://qdrant.tech/documentation/) whose name will be defined by the user. If the collection does not already exist in the Qdrant instance, a new collection with the same name will be created.

For each [point](https://qdrant.tech/documentation/concepts/points/) in the collection, a UUID string is generated and used as the [point id](https://qdrant.tech/documentation/concepts/points/#point-ids). The embeddings generated as defined or extracted from the source stream will be stored as the point vectors. The point payload will contain primarily the record metadata. The text field will then be stored in a field (as defined in the config) in the point payload.

## Getting Started

You can connect to a Qdrant instance either in local mode or cloud mode.

- For the local mode, you will need to set it up using Docker. Check the Qdrant docs [here](https://qdrant.tech/documentation/guides/installation/#docker) for an official guide. After setting up, you would need your host, port and if applicable, your gRPC port.
- To setup to an instance in Qdrant cloud, check out [this official guide](https://qdrant.tech/documentation/cloud/) to get started. After setting up the instance, you would need the instance url and an API key to connect.

Note that this connector does not support a local persistent mode. To test, use the docker option.

#### Requirements

To use the Qdrant destination, you'll need:

- An account with API access for OpenAI, Cohere (depending on which embedding method you want to use) or neither (if you want to extract the vectors from the source stream)
- A Qdrant db instance (local mode or cloud mode)
- Qdrant API Credentials (for cloud mode)
- Host and Port (for local mode)
- gRPC port (if applicable in local mode)

#### Configure Network Access

Make sure your Qdrant database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

### Setup the Qdrant Destination in Airbyte

You should now have all the requirements needed to configure Qdrant as a destination in the UI. You'll need the following information to configure the Qdrant destination:

- (Required) **Text fields to embed**
- (Optional) **Text splitter** Options around configuring the chunking process provided by the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).
- (Required) **Fields to store as metadata**
- (Required) **Collection** The name of the collection in Qdrant db to store your data
- (Required) **The field in the payload that contains the embedded text**
- (Required) **Prefer gRPC** Whether to prefer gRPC over HTTP.
- (Required) **Distance Metric** The Distance metrics used to measure similarities among vectors. Select from:
  - [Dot product](https://en.wikipedia.org/wiki/Dot_product)
  - [Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
  - [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance)
- (Required) Authentication method
  - For local mode
    - **Host** for example localhost
    - **Port** for example 8000
    - **gRPC Port** (Optional)
  - For cloud mode
    - **Url** The url of the cloud Qdrant instance.
    - **API Key** The API Key for the cloud Qdrant instance
- (Optional) Embedding
  - **OpenAI API key** if using OpenAI for embedding
  - **Cohere API key** if using Cohere for embedding
  - Embedding **Field name** and **Embedding dimensions** if getting the embeddings from stream records

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                  |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------------------------------------- |
| 0.0.11  | 2024-04-15 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Updated CDK and pytest versions to fix security vulnerabilities          |
| 0.0.10  | 2023-12-11 | [#33303](https://github.com/airbytehq/airbyte/pull/33303) | Fix bug with embedding special tokens                                    |
| 0.0.9   | 2023-12-01 | [#32697](https://github.com/airbytehq/airbyte/pull/32697) | Allow omitting raw text                                                  |
| 0.0.8   | 2023-11-29 | [#32608](https://github.com/airbytehq/airbyte/pull/32608) | Support deleting records for CDC sources and fix spec schema             |
| 0.0.7   | 2023-11-13 | [#32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema                                                      |
| 0.0.6   | 2023-10-23 | [#31563](https://github.com/airbytehq/airbyte/pull/31563) | Add field mapping option                                                 |
| 0.0.5   | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329) | Add OpenAI-compatible embedder option                                    |
| 0.0.4   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size                                           |
| 0.0.3   | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820) | Update CDK                                                               |
| 0.0.2   | 2023-09-25 | [#30689](https://github.com/airbytehq/airbyte/pull/30689) | Update CDK to support Azure OpenAI embeddings and text splitting options |
| 0.0.1   | 2023-09-22 | [#30332](https://github.com/airbytehq/airbyte/pull/30332) | 🎉 New Destination: Qdrant (Vector Database)                             |
