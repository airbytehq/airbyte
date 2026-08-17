# Weaviate

## Overview

This page guides you through the process of setting up the [Weaviate](https://weaviate.io/) destination connector.

There are three parts to this:

- Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
- Embedding - convert the text into a vector representation, either by calling an embedding service, by reading a pre-calculated vector from the record, or by letting Weaviate's own vectorizer do it.
- Indexing - store the vectors in a vector database for similarity search

The connector uses version 3 of the Weaviate Python client, so it works with Weaviate's class-based schema API. Newer Weaviate documentation calls these objects collections, but this connector and its configuration refer to them as classes.

## Prerequisites

To use the Weaviate destination, you'll need:

- Access to a running Weaviate instance (either self-hosted or Weaviate Cloud), minimum version 1.21.2
- One of the following, depending on how you want vectors to be produced:
  - An account with API access for OpenAI, Azure OpenAI, Cohere, or another OpenAI-compatible embedding service
  - Pre-calculated embeddings stored in a field in your source records
  - A [vectorizer module](https://docs.weaviate.io/weaviate/model-providers) configured in Weaviate, so Weaviate embeds the text itself

You'll need the following information to configure the destination:

- **Public Endpoint** - The URL of the Weaviate cluster to load data into, for example `https://my-cluster.weaviate.network`.
- **Authentication** - How to authenticate against the cluster: an API token (Weaviate Cloud), a username and password (self-managed clusters), or no authentication (local test clusters only).
- **Embedding service API key** - Only required if Airbyte calculates the embeddings for you.

On Airbyte Cloud, the endpoint must start with `https://` and authentication must be enabled. The connection check fails if either condition isn't met, so **No Authentication** and plain HTTP endpoints only work in self-managed Airbyte deployments.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Data type mapping

All fields specified as metadata fields will be stored as properties in the object can be used for filtering. The following data types are allowed for metadata fields:

- String
- Number (integer or floating point, gets converted to a 64 bit floating point)
- Booleans (true, false)
- List of String

All other fields are serialized into their JSON representation. Metadata fields holding an empty list are dropped instead of written, because Weaviate rejects them when they aren't part of a predefined schema.

## Configuration

### Processing

Each record will be split into text fields and metadata fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. You can split text by separator, by Markdown header, or at syntax boundaries for a specific programming language.

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using the [OpenAI embeddings API](https://platform.openai.com/docs/api-reference/embeddings), the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. Throughput is limited by [OpenAI's rate limits](https://platform.openai.com/docs/guides/rate-limits).

2. Azure OpenAI - the same model and dimensions as OpenAI, but served from your own Azure OpenAI resource. You need the resource base URL, the deployment name, and an API key. Azure's API accepts at most 16 documents per request, so this option is slower than OpenAI for large syncs.

3. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.

4. OpenAI-compatible - for self-hosted or third-party services that implement the OpenAI embeddings API. You provide the base URL, the model name, and the number of dimensions the model returns. The dimensions you enter must match the model's actual output, because the connector doesn't verify it.

5. From field - if you have pre-calculated embeddings stored in a field in your source records, you can use the `From field` integration to load them into Weaviate. The field must be a JSON array of numbers, e.g. `[0.1, 0.2, 0.3]`, and its length must match the configured number of dimensions.

6. No external embedding - Airbyte sends no vector at all. Use this when the target class has a [vectorizer](https://docs.weaviate.io/weaviate/model-providers) configured so Weaviate embeds the text itself, or when the class is only used for keyword search. Set **Default Vectorizer** and, if the vectorizer needs an API key, pass it with **Additional headers**.

For testing purposes, it's also possible to use the `Fake` embedding integration. It generates random 1536-dimension vectors and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

The indexing section has the following options:

| Option | Default | Description |
| :--- | :--- | :--- |
| **Batch Size** | 128 | Number of objects sent to Weaviate per batch. Lower it if the cluster rejects large batches or runs out of memory. |
| **Text Field** | `text` | Property that receives the embedded text chunk. It must match the `text_key` your query code and any vectorizer expect. |
| **Tenant ID** | empty | Enables multi-tenancy for this connection. Leave empty to disable multi-tenancy. |
| **Default Vectorizer** | `none` | Vectorizer set on classes the connector creates. Only relevant when Weaviate should embed the text itself. |
| **Additional headers** | empty | Extra HTTP headers sent with every request, for example `X-OpenAI-Api-Key` for a `text2vec-openai` vectorizer. |

All streams will be indexed into separate classes derived from the stream name. The connector strips everything except letters, digits, and underscores from the stream name and capitalizes the first character, so the `users_v2` stream becomes the `Users_v2` class and `my orders!` becomes `Myorders`.

If a class doesn't exist in the schema of the cluster, the connector creates it with the configured default vectorizer and a single `_ab_record_id` property. Weaviate infers the remaining properties from the first objects it receives, so auto-schema has to be enabled on the server.

You can also create the class in Weaviate in advance if you need more control over the schema. In this case, create the text properties `_ab_stream` and `_ab_record_id` for bookkeeping reasons. Deduplication and CDC deletes depend on `_ab_record_id`: if the existing class doesn't have that property, the connector skips the delete step and older versions of a record stay in the class alongside the new ones.

When a sync runs in `Overwrite` mode, the class is deleted and recreated with the same schema it had before, so any properties Weaviate inferred earlier are preserved.

Properties in Weaviate have to start with a lowercase letter and can't contain spaces or special characters, so field names might be updated during the loading process. The field names `id`, `_id`, and `_additional` are reserved keywords in Weaviate, so they are renamed to `raw_id`, `raw__id`, and `raw__additional` respectively.

When using [multi-tenancy](https://docs.weaviate.io/weaviate/manage-collections/multi-tenancy), the tenant id can be configured in the connector configuration. If not specified, multi-tenancy will be disabled. In case you want to index into an already created class, you need to make sure the class is created with multi-tenancy enabled. In case the class doesn't exist, it will be created with multi-tenancy properly configured. If the class already exists but the tenant id is not associated with the class, the connector will automatically add the tenant id to the class. This allows you to configure multiple connections for different tenants on the same schema.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                      |
|:--------| :--------- | :--------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.64 | 2026-08-13 | [84358](https://github.com/airbytehq/airbyte/pull/84358) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.2.63 | 2026-07-02 | [81386](https://github.com/airbytehq/airbyte/pull/81386) | Upgrade pillow from 11.x to 12.3.0 to resolve security vulnerabilities GHSA-cfh3-3jmp-rvhc, GHSA-pwv6-vv43-88gr, GHSA-whj4-6x5x-4v2j, GHSA-xg8h-j46f-w952 |
| 0.2.62 | 2026-07-01 | [81364](https://github.com/airbytehq/airbyte/pull/81364) | Bump authlib 1.6.3 to 1.6.12 to resolve security vulnerabilities |
| 0.2.61 | 2026-03-31 | [75645](https://github.com/airbytehq/airbyte/pull/75645) | Bump version to force registry update for supportLevel change to community |
| 0.2.60 | 2025-10-16 | [61103](https://github.com/airbytehq/airbyte/pull/61103) | Update dependencies |
| 0.2.59 | 2025-05-17 | [57180](https://github.com/airbytehq/airbyte/pull/57180) | Update dependencies |
| 0.2.58 | 2025-03-29 | [56089](https://github.com/airbytehq/airbyte/pull/56089) | Update dependencies |
| 0.2.57 | 2025-03-08 | [55424](https://github.com/airbytehq/airbyte/pull/55424) | Update dependencies |
| 0.2.56 | 2025-03-01 | [54880](https://github.com/airbytehq/airbyte/pull/54880) | Update dependencies |
| 0.2.55 | 2025-02-22 | [54278](https://github.com/airbytehq/airbyte/pull/54278) | Update dependencies |
| 0.2.54 | 2025-02-15 | [53894](https://github.com/airbytehq/airbyte/pull/53894) | Update dependencies |
| 0.2.53 | 2025-02-08 | [53424](https://github.com/airbytehq/airbyte/pull/53424) | Update dependencies |
| 0.2.52 | 2025-02-01 | [52944](https://github.com/airbytehq/airbyte/pull/52944) | Update dependencies |
| 0.2.51 | 2025-01-25 | [52211](https://github.com/airbytehq/airbyte/pull/52211) | Update dependencies |
| 0.2.50 | 2025-01-18 | [51759](https://github.com/airbytehq/airbyte/pull/51759) | Update dependencies |
| 0.2.49 | 2025-01-11 | [51259](https://github.com/airbytehq/airbyte/pull/51259) | Update dependencies |
| 0.2.48 | 2025-01-04 | [50908](https://github.com/airbytehq/airbyte/pull/50908) | Update dependencies |
| 0.2.47 | 2024-12-28 | [50444](https://github.com/airbytehq/airbyte/pull/50444) | Update dependencies |
| 0.2.46 | 2024-12-21 | [50182](https://github.com/airbytehq/airbyte/pull/50182) | Update dependencies |
| 0.2.45 | 2024-12-14 | [49317](https://github.com/airbytehq/airbyte/pull/49317) | Update dependencies |
| 0.2.44 | 2024-11-25 | [48640](https://github.com/airbytehq/airbyte/pull/48640) | Update dependencies |
| 0.2.43 | 2024-11-04 | [48244](https://github.com/airbytehq/airbyte/pull/48244) | Update dependencies |
| 0.2.42 | 2024-10-29 | [47063](https://github.com/airbytehq/airbyte/pull/47063) | Update dependencies |
| 0.2.41 | 2024-10-12 | [46848](https://github.com/airbytehq/airbyte/pull/46848) | Update dependencies |
| 0.2.40 | 2024-10-05 | [46465](https://github.com/airbytehq/airbyte/pull/46465) | Update dependencies |
| 0.2.39 | 2024-09-28 | [46189](https://github.com/airbytehq/airbyte/pull/46189) | Update dependencies |
| 0.2.38 | 2024-09-21 | [45822](https://github.com/airbytehq/airbyte/pull/45822) | Update dependencies |
| 0.2.37 | 2024-09-14 | [45560](https://github.com/airbytehq/airbyte/pull/45560) | Update dependencies |
| 0.2.36 | 2024-09-07 | [45216](https://github.com/airbytehq/airbyte/pull/45216) | Update dependencies |
| 0.2.35 | 2024-08-31 | [44964](https://github.com/airbytehq/airbyte/pull/44964) | Update dependencies |
| 0.2.34 | 2024-08-24 | [44668](https://github.com/airbytehq/airbyte/pull/44668) | Update dependencies |
| 0.2.33 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.32 | 2024-08-17 | [44216](https://github.com/airbytehq/airbyte/pull/44216) | Update dependencies |
| 0.2.31 | 2024-08-12 | [43906](https://github.com/airbytehq/airbyte/pull/43906) | Update dependencies |
| 0.2.30 | 2024-08-10 | [43599](https://github.com/airbytehq/airbyte/pull/43599) | Update dependencies |
| 0.2.29 | 2024-08-03 | [43084](https://github.com/airbytehq/airbyte/pull/43084) | Update dependencies |
| 0.2.28 | 2024-07-27 | [42629](https://github.com/airbytehq/airbyte/pull/42629) | Update dependencies |
| 0.2.27 | 2024-07-20 | [42283](https://github.com/airbytehq/airbyte/pull/42283) | Update dependencies |
| 0.2.26 | 2024-07-13 | [41935](https://github.com/airbytehq/airbyte/pull/41935) | Update dependencies |
| 0.2.25 | 2024-07-10 | [41504](https://github.com/airbytehq/airbyte/pull/41504) | Update dependencies |
| 0.2.24 | 2024-07-09 | [41222](https://github.com/airbytehq/airbyte/pull/41222) | Update dependencies |
| 0.2.23 | 2024-07-06 | [40943](https://github.com/airbytehq/airbyte/pull/40943) | Update dependencies |
| 0.2.22 | 2024-06-29 | [40633](https://github.com/airbytehq/airbyte/pull/40633) | Update dependencies |
| 0.2.21 | 2024-06-25 | [40274](https://github.com/airbytehq/airbyte/pull/40274) | Update dependencies |
| 0.2.20 | 2024-06-22 | [40109](https://github.com/airbytehq/airbyte/pull/40109) | Update dependencies |
| 0.2.19 | 2024-06-06 | [39212](https://github.com/airbytehq/airbyte/pull/39212) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.18 | 2024-05-15 | [38272](https://github.com/airbytehq/airbyte/pull/38272) | Replace AirbyteLogger with logging.Logger |
| 0.2.17  | 2024-04-15 | [#37333](https://github.com/airbytehq/airbyte/pull/37333)  | Update CDK & pytest version to fix security vulnerabilities.                                                                                 |
| 0.2.16  | 2024-03-22 | [#35911](https://github.com/airbytehq/airbyte/pull/35911)  | Fix tests and move to Poetry                                                                                                                 |
| 0.2.15  | 2023-01-25 | [#34529](https://github.com/airbytehq/airbyte/pull/34529)  | Fix tests                                                                                                                                    |
| 0.2.14  | 2023-01-15 | [#34229](https://github.com/airbytehq/airbyte/pull/34229)  | Allow configuring tenant id                                                                                                                  |
| 0.2.13  | 2023-12-11 | [#33303](https://github.com/airbytehq/airbyte/pull/33303)  | Fix bug with embedding special tokens                                                                                                        |
| 0.2.12  | 2023-12-07 | [#33218](https://github.com/airbytehq/airbyte/pull/33218)  | Normalize metadata field names                                                                                                               |
| 0.2.11  | 2023-12-01 | [#32697](https://github.com/airbytehq/airbyte/pull/32697)  | Allow omitting raw text                                                                                                                      |
| 0.2.10  | 2023-11-16 | [#32608](https://github.com/airbytehq/airbyte/pull/32608)  | Support deleting records for CDC sources                                                                                                     |
| 0.2.9   | 2023-11-13 | [#32357](https://github.com/airbytehq/airbyte/pull/32357)  | Improve spec schema                                                                                                                          |
| 0.2.8   | 2023-11-03 | [#32134](https://github.com/airbytehq/airbyte/pull/32134)  | Improve test coverage                                                                                                                        |
| 0.2.7   | 2023-11-03 | [#32134](https://github.com/airbytehq/airbyte/pull/32134)  | Upgrade weaviate client library                                                                                                              |
| 0.2.6   | 2023-11-01 | [#32038](https://github.com/airbytehq/airbyte/pull/32038)  | Retry failed object loads                                                                                                                    |
| 0.2.5   | 2023-10-24 | [#31953](https://github.com/airbytehq/airbyte/pull/31953)  | Fix memory leak                                                                                                                              |
| 0.2.4   | 2023-10-23 | [#31563](https://github.com/airbytehq/airbyte/pull/31563)  | Add field mapping option, improve append+dedupe sync performance and remove unnecessary retry logic                                          |
| 0.2.3   | 2023-10-19 | [#31599](https://github.com/airbytehq/airbyte/pull/31599)  | Base image migration: remove Dockerfile and use the python-connector-base image                                                              |
| 0.2.2   | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329)  | Add OpenAI-compatible embedder option                                                                                                        |
| 0.2.1   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075)  | Fix OpenAI embedder batch size and conflict field name handling                                                                              |
| 0.2.0   | 2023-09-22 | [#30151](https://github.com/airbytehq/airbyte/pull/30151)  | Add embedding capabilities, overwrite and dedup support and API key auth mode, make certified. 🚨 Breaking changes - check migrations guide. |
| 0.1.1   | 2022-02-08 | [\#22527](https://github.com/airbytehq/airbyte/pull/22527) | Multiple bug fixes: Support String based IDs, arrays of uknown type and additionalProperties of type object and array of objects             |
| 0.1.0   | 2022-12-06 | [\#20094](https://github.com/airbytehq/airbyte/pull/20094) | Add Weaviate destination                                                                                                                     |

</details>
