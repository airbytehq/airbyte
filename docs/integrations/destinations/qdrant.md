# Qdrant

This page guides you through the process of setting up the [Qdrant](https://qdrant.tech/documentation/) destination connector.

## Output schema

The connector writes every source stream into a single Qdrant [collection](https://qdrant.tech/documentation/concepts/collections/), which you name in the connector configuration. If that collection doesn't exist, the connector creates it, using the vector size of your embedding model and the distance metric you select.

If the collection already exists, its vector size must match the dimensions of your embedding model and its distance metric must match the **Distance Metric** you select. Otherwise, the connection check fails. To change either setting, create a new collection or select a different collection name.

Each record is chunked, and each chunk becomes a [point](https://qdrant.tech/documentation/concepts/points/) with a randomly generated UUID as its [point id](https://qdrant.tech/documentation/concepts/points/#point-ids). The chunk's embedding is the point vector. The point payload contains the record's metadata fields and, unless you enable **Do not store raw text**, the embedded text in the field named by **Text Field**.

The connector adds and indexes two payload fields it uses to manage records:

- `_ab_stream`: the source stream, prefixed with the namespace when the stream has one, as `namespace_stream`.
- `_ab_record_id`: the record's primary key. Present only for streams in append + deduped mode that have a primary key.

In overwrite mode, the connector deletes all points matching `_ab_stream` for that stream before the sync, rather than dropping the collection. Points from other streams in the same collection are untouched.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Requirements

To use this destination, you need:

- A running Qdrant server, either in [Qdrant Cloud](https://qdrant.tech/documentation/cloud-intro/) or self-hosted. The connector always connects over the network, so Qdrant's embedded local mode and on-disk local persistence aren't supported. To try the connector locally, run Qdrant in Docker.
- The endpoint URL of that server, and an API key if the server requires authentication.
- Credentials for the embedding service you choose, unless you use the **Fake** embedder for testing.

## Set up Qdrant

### Qdrant Cloud

1. Create a cluster by following Qdrant's [cloud quickstart](https://qdrant.tech/documentation/quickstart-cloud/).
2. Copy the cluster endpoint URL. It looks like `https://xyz-example.eu-central.aws.cloud.qdrant.io:6333`.
3. Create a [database API key](https://qdrant.tech/documentation/cloud/authentication/) for the cluster. Qdrant shows the key only once, so store it before closing the dialog. Give the key permission to write to the cluster, and, if you scope the key to specific collections, include the collection this connector writes to.

### Self-hosted Qdrant

1. Start Qdrant, for example with [Docker](https://qdrant.tech/documentation/quickstart/): `docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant`.
2. Use `http://<host>:6333` as the endpoint URL. Qdrant serves its REST API on port `6333` and its gRPC API on port `6334`.
3. Self-hosted Qdrant has no authentication by default. If you haven't [set an API key](https://qdrant.tech/documentation/guides/security/), select the no-authentication option in the connector. Anyone who can reach an unauthenticated server has full access to it, so don't expose one to the internet.

### Configure network access

Airbyte must be able to reach your Qdrant server. If the server is in a VPC, allow access from the IP address Airbyte connects from.

Airbyte connects to the REST port in the endpoint URL. When **Prefer gRPC** is enabled, it also connects to gRPC port `6334` on the same host. The connector can't change the gRPC port, so make sure `6334` is reachable, and that gRPC is enabled on a self-hosted server. If you can only expose the REST port, disable **Prefer gRPC**.

## Set up the Qdrant destination in Airbyte

Configure the following fields.

### Processing

- (Required) **Chunk size**: The maximum number of tokens per chunk. Keep it within the context window of your embedding model.
- (Optional) **Chunk overlap**: The number of tokens repeated between consecutive chunks. Defaults to `0`.
- (Optional) **Text fields to embed**: The record fields to embed. If you leave this empty, the connector embeds all fields.
- (Optional) **Fields to store as metadata**: The record fields to write to the point payload. If you leave this empty, the connector stores all fields.
- (Optional) **Text splitter**: How to split long text into chunks. Choose splitting by separator, by Markdown headers, or by code syntax.
- (Optional) **Field name mappings**: Rename source fields before they're written to the payload.

### Embedding

(Required) Choose how to produce vectors. Options are **OpenAI**, **Azure OpenAI**, **Cohere**, **OpenAI-compatible** (for self-hosted or third-party services that implement the OpenAI embedding API), **From Field** (for vectors already present in each record), and **Fake** (random vectors, for testing only). Each option has its own configuration fields, including credentials or vector dimensions where applicable.

### Indexing

- (Required) **Public Endpoint**: The URL of your Qdrant server, such as `https://xyz-example.eu-central.aws.cloud.qdrant.io:6333` or `http://localhost:6333`.
- (Optional) **Authentication Method**: Either API key authentication, with your Qdrant API key, or no authentication. Defaults to API key authentication. When you use an API key, the endpoint must start with `https://`.
- (Optional) **Prefer gRPC**: Whether to prefer gRPC over HTTP. Enabled by default, and recommended for Qdrant Cloud clusters.
- (Required) **Collection Name**: The collection to write to.
- (Optional) **Distance Metric**: The metric used to compare vectors. Choose [Dot product](https://en.wikipedia.org/wiki/Dot_product), [Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity), or [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance). Defaults to cosine similarity. The connector applies this only when it creates the collection. For an existing collection, the value must match the collection's metric.
- (Optional) **Text Field**: The payload field that holds the embedded text. Defaults to `text`.

### Advanced

- (Optional) **Do not store raw text**: Write only the vector and metadata, without the text that was embedded.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). All streams share one collection, so a stream's namespace appears in the `_ab_stream` payload field instead of creating a separate collection.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                  |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------------------------------------- |
| 0.1.42 | 2026-08-13 | [84360](https://github.com/airbytehq/airbyte/pull/84360) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.1.41 | 2025-05-10 | [59814](https://github.com/airbytehq/airbyte/pull/59814) | Update dependencies |
| 0.1.40 | 2025-05-03 | [58718](https://github.com/airbytehq/airbyte/pull/58718) | Update dependencies |
| 0.1.39 | 2025-04-19 | [58282](https://github.com/airbytehq/airbyte/pull/58282) | Update dependencies |
| 0.1.38 | 2025-04-12 | [57610](https://github.com/airbytehq/airbyte/pull/57610) | Update dependencies |
| 0.1.37 | 2025-04-05 | [57162](https://github.com/airbytehq/airbyte/pull/57162) | Update dependencies |
| 0.1.36 | 2025-03-29 | [56564](https://github.com/airbytehq/airbyte/pull/56564) | Update dependencies |
| 0.1.35 | 2025-03-22 | [56159](https://github.com/airbytehq/airbyte/pull/56159) | Update dependencies |
| 0.1.34 | 2025-03-08 | [55363](https://github.com/airbytehq/airbyte/pull/55363) | Update dependencies |
| 0.1.33 | 2025-03-01 | [54889](https://github.com/airbytehq/airbyte/pull/54889) | Update dependencies |
| 0.1.32 | 2025-02-22 | [54246](https://github.com/airbytehq/airbyte/pull/54246) | Update dependencies |
| 0.1.31 | 2025-02-15 | [53939](https://github.com/airbytehq/airbyte/pull/53939) | Update dependencies |
| 0.1.30 | 2025-02-08 | [53389](https://github.com/airbytehq/airbyte/pull/53389) | Update dependencies |
| 0.1.29 | 2025-02-01 | [52917](https://github.com/airbytehq/airbyte/pull/52917) | Update dependencies |
| 0.1.28 | 2025-01-25 | [52171](https://github.com/airbytehq/airbyte/pull/52171) | Update dependencies |
| 0.1.27 | 2025-01-18 | [51716](https://github.com/airbytehq/airbyte/pull/51716) | Update dependencies |
| 0.1.26 | 2025-01-11 | [51232](https://github.com/airbytehq/airbyte/pull/51232) | Update dependencies |
| 0.1.25 | 2025-01-04 | [50917](https://github.com/airbytehq/airbyte/pull/50917) | Update dependencies |
| 0.1.24 | 2024-12-28 | [50459](https://github.com/airbytehq/airbyte/pull/50459) | Update dependencies |
| 0.1.23 | 2024-12-21 | [50222](https://github.com/airbytehq/airbyte/pull/50222) | Update dependencies |
| 0.1.22 | 2024-12-14 | [49290](https://github.com/airbytehq/airbyte/pull/49290) | Update dependencies |
| 0.1.21 | 2024-11-25 | [48641](https://github.com/airbytehq/airbyte/pull/48641) | Update dependencies |
| 0.1.20 | 2024-11-04 | [48191](https://github.com/airbytehq/airbyte/pull/48191) | Update dependencies |
| 0.1.19 | 2024-10-29 | [47757](https://github.com/airbytehq/airbyte/pull/47757) | Update dependencies |
| 0.1.18 | 2024-10-28 | [47621](https://github.com/airbytehq/airbyte/pull/47621) | Update dependencies |
| 0.1.17 | 2024-10-28 | [47054](https://github.com/airbytehq/airbyte/pull/47054) | Update dependencies |
| 0.1.16 | 2024-10-12 | [46774](https://github.com/airbytehq/airbyte/pull/46774) | Update dependencies |
| 0.1.15 | 2024-10-05 | [46417](https://github.com/airbytehq/airbyte/pull/46417) | Update dependencies |
| 0.1.14 | 2024-09-28 | [46137](https://github.com/airbytehq/airbyte/pull/46137) | Update dependencies |
| 0.1.13 | 2024-09-21 | [45830](https://github.com/airbytehq/airbyte/pull/45830) | Update dependencies |
| 0.1.12 | 2024-09-14 | [45526](https://github.com/airbytehq/airbyte/pull/45526) | Update dependencies |
| 0.1.11 | 2024-09-07 | [45217](https://github.com/airbytehq/airbyte/pull/45217) | Update dependencies |
| 0.1.10 | 2024-08-31 | [44678](https://github.com/airbytehq/airbyte/pull/44678) | Update dependencies |
| 0.1.9 | 2024-08-17 | [44293](https://github.com/airbytehq/airbyte/pull/44293) | Update dependencies |
| 0.1.8 | 2024-08-12 | [43744](https://github.com/airbytehq/airbyte/pull/43744) | Update dependencies |
| 0.1.7 | 2024-08-10 | [43529](https://github.com/airbytehq/airbyte/pull/43529) | Update dependencies |
| 0.1.6 | 2024-08-03 | [43219](https://github.com/airbytehq/airbyte/pull/43219) | Update dependencies |
| 0.1.5 | 2024-07-27 | [42620](https://github.com/airbytehq/airbyte/pull/42620) | Update dependencies |
| 0.1.4 | 2024-07-20 | [42384](https://github.com/airbytehq/airbyte/pull/42384) | Update dependencies |
| 0.1.3 | 2024-07-13 | [41919](https://github.com/airbytehq/airbyte/pull/41919) | Update dependencies |
| 0.1.2 | 2024-07-10 | [41530](https://github.com/airbytehq/airbyte/pull/41530) | Update dependencies |
| 0.1.1 | 2024-07-09 | [41096](https://github.com/airbytehq/airbyte/pull/41096) | Update dependencies |
| 0.1.0 | 2024-06-27 | [41020](https://github.com/airbytehq/airbyte/pull/41020) | Update to Airbyte CDK 2.3 and qdrant-client 1.10 |
| 0.0.13 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.0.12 | 2024-06-06 | [39172](https://github.com/airbytehq/airbyte/pull/39172) | [autopull] Upgrade base image to v1.2.2 |
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

</details>
