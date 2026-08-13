# Chroma

This page guides you through setting up the [Chroma](https://docs.trychroma.com/) destination connector.

The connector splits the text fields of your records into chunks, turns each chunk into an embedding vector, and writes the vectors, the chunk text, and the record metadata to a single Chroma collection. You can either let Airbyte compute the embeddings with an external service, pass embeddings that already exist in your records, or let Chroma compute them with its own default embedding function.

## Prerequisites

- A Chroma database. The connector can connect to a Chroma server over HTTP, or read and write a database directory on the machine running Airbyte.
- A username and password, if your Chroma server requires basic authentication.
- An API key for OpenAI, Azure OpenAI, Cohere, or another OpenAI-compatible embedding service, if you want Airbyte to compute the embeddings. You don't need one if your records already contain embeddings or if you use Chroma's default embedding function.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

Overwrite syncs don't delete the collection. At the start of the sync, the connector deletes the documents whose `_ab_stream` metadata value matches the streams being overwritten, so documents from other streams and from other tools stay in place.

Deduplicating syncs require a primary key on the stream. Before writing a record, the connector deletes the documents whose `_ab_record_id` metadata value matches that record's primary key.

## Output schema

All source streams are written to one Chroma collection, which you name in the connector configuration. Each chunk becomes one document in that collection:

- The document ID is a randomly generated UUID. Source primary keys are stored in metadata instead, so you can't look a record up by its source ID.
- The chunk text is stored as the document, unless you enable **Do not store raw text**.
- The embedding is stored as the document's embedding. If you use Chroma's default embedding function, Airbyte sends no embedding and Chroma computes one.
- The fields you select as metadata are stored as document metadata, along with `_ab_stream` (the stream identifier, in the form `namespace_stream` when the stream has a namespace) and `_ab_record_id` (the record's primary key, for deduplicating streams).

Chroma metadata values must be strings, numbers, or booleans. The connector JSON-encodes any other value, such as an object or an array, into a string.

## Namespace support

Source namespaces don't create separate Chroma collections. Everything is written to the collection you configure, and the namespace becomes part of the `_ab_stream` metadata value, which you can filter on when you query Chroma.

## Set up the Chroma destination

### Connection mode

Choose one of the following connection modes.

**Client/Server Mode** connects to a running Chroma server:

- **Host**: the hostname of the Chroma instance, for example `localhost`.
- **Port**: the port the Chroma instance listens on, for example `8000`.
- **SSL**: whether to connect over HTTPS.
- **Username** and **Password**: only needed if the server is configured for basic authentication. Leave both empty otherwise.

Make sure the Chroma server is reachable from Airbyte. If it runs inside a VPC, allow access from the IP address that Airbyte syncs from.

**Persistent Client Mode** stores the database in a directory on the machine running Airbyte:

- **Path**: an absolute path prefixed with `/local`, for example `/local/chroma`.

In Docker deployments, `/local` is mapped to the directory Airbyte mounts for local files, which is `/tmp/airbyte_local` unless you change the `LOCAL_ROOT` environment variable. On macOS, Docker Desktop must be allowed to share `/tmp` and `/private`, because `/tmp` is a symlink to `/private/tmp`. Grant access in **Settings** > **Resources** > **File sharing**, then apply and restart.

:::danger

Persistent Client Mode isn't supported on Kubernetes, because the sync pod has no durable local storage. Use Client/Server Mode instead.

:::

### Collection name

Set **Collection Name** to the collection you want to load data into. The connector creates the collection if it doesn't exist. Chroma uses the name in URLs, so it must:

- Be between 3 and 63 characters long.
- Start and end with a lowercase letter or a digit.
- Contain only alphanumeric characters, dots, dashes, and underscores.
- Contain no two consecutive dots.
- Not be a valid IPv4 address.

The connector checks these rules during the connection test and reports a specific error when the name is invalid.

### Embedding

Pick how the embeddings are produced:

- **OpenAI**: uses `text-embedding-ada-002` with 1536 dimensions. Requires an **OpenAI API key**.
- **Azure OpenAI**: uses `text-embedding-ada-002` with 1536 dimensions from your own Azure resource. Requires the **Azure OpenAI API key**, **Resource base URL**, and **Deployment**.
- **Cohere**: requires a **Cohere API key**.
- **OpenAI-compatible**: for self-hosted or third-party services that expose the OpenAI embeddings API. Requires the **Base URL**, **Embedding dimensions**, and, depending on the service, an **API key** and **Model name**.
- **From Field**: uses an embedding that already exists in the record. Set **Field name** to the field holding the vector and **Embedding dimensions** to its length. Records whose vector has a different length fail the sync.
- **Fake**: random vectors with 1536 dimensions, for testing a pipeline without paying for embeddings.
- **Chroma Default Embedding Function**: Airbyte sends no embedding, and Chroma embeds the documents itself with a local sentence-transformers model. This can be slow, depending on the hardware running Chroma, and suits prototypes better than production loads.

### Processing

These options control how records become chunks:

- **Chunk size** (required): the maximum size of a chunk in tokens, up to 8191. Keep it small enough for the context window of the model you query with.
- **Chunk overlap**: how many tokens consecutive chunks share, which helps preserve context across chunk boundaries. Defaults to 0.
- **Text fields to embed**: the record fields to embed. Use dot notation for nested fields, such as `user.name`, and wildcards for arrays, such as `users.*.name`. If you leave this empty, all fields are embedded.
- **Fields to store as metadata**: the record fields to store as document metadata. If you leave this empty, all fields are stored as metadata.
- **Text splitter**: how to split text that exceeds the chunk size. You can split by separator, by Markdown header level, or by the syntax of a programming language.
- **Field name mappings**: renames source fields before they're written.
- **Do not store raw text**: stores only the embedding and metadata. Use this when the source text is sensitive or already available elsewhere. Retrieval-augmented generation workflows that read the chunk text from Chroma break when you enable it.

The connector writes documents to Chroma in batches of 128 chunks.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                      |
|:--------|:-----------| :-------------------------------------------------------- |:-------------------------------------------------------------|
| 0.0.55 | 2026-08-13 | [84361](https://github.com/airbytehq/airbyte/pull/84361) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.0.54 | 2025-05-03 | [59326](https://github.com/airbytehq/airbyte/pull/59326) | Update dependencies |
| 0.0.53 | 2025-04-26 | [58256](https://github.com/airbytehq/airbyte/pull/58256) | Update dependencies |
| 0.0.52 | 2025-04-12 | [57652](https://github.com/airbytehq/airbyte/pull/57652) | Update dependencies |
| 0.0.51 | 2025-04-05 | [57169](https://github.com/airbytehq/airbyte/pull/57169) | Update dependencies |
| 0.0.50 | 2025-03-29 | [56624](https://github.com/airbytehq/airbyte/pull/56624) | Update dependencies |
| 0.0.49 | 2025-03-22 | [56120](https://github.com/airbytehq/airbyte/pull/56120) | Update dependencies |
| 0.0.48 | 2025-03-08 | [55393](https://github.com/airbytehq/airbyte/pull/55393) | Update dependencies |
| 0.0.47 | 2025-03-01 | [54852](https://github.com/airbytehq/airbyte/pull/54852) | Update dependencies |
| 0.0.46 | 2025-02-22 | [54209](https://github.com/airbytehq/airbyte/pull/54209) | Update dependencies |
| 0.0.45 | 2025-02-15 | [53930](https://github.com/airbytehq/airbyte/pull/53930) | Update dependencies |
| 0.0.44 | 2025-02-08 | [53428](https://github.com/airbytehq/airbyte/pull/53428) | Update dependencies |
| 0.0.43 | 2025-02-01 | [52941](https://github.com/airbytehq/airbyte/pull/52941) | Update dependencies |
| 0.0.42 | 2025-01-25 | [52189](https://github.com/airbytehq/airbyte/pull/52189) | Update dependencies |
| 0.0.41 | 2025-01-18 | [51744](https://github.com/airbytehq/airbyte/pull/51744) | Update dependencies |
| 0.0.40 | 2025-01-11 | [51296](https://github.com/airbytehq/airbyte/pull/51296) | Update dependencies |
| 0.0.39 | 2025-01-04 | [50913](https://github.com/airbytehq/airbyte/pull/50913) | Update dependencies |
| 0.0.38 | 2024-12-28 | [50445](https://github.com/airbytehq/airbyte/pull/50445) | Update dependencies |
| 0.0.37 | 2024-12-21 | [50221](https://github.com/airbytehq/airbyte/pull/50221) | Update dependencies |
| 0.0.36 | 2024-12-14 | [48956](https://github.com/airbytehq/airbyte/pull/48956) | Update dependencies |
| 0.0.35 | 2024-11-25 | [48668](https://github.com/airbytehq/airbyte/pull/48668) | Update dependencies |
| 0.0.34 | 2024-11-04 | [48236](https://github.com/airbytehq/airbyte/pull/48236) | Update dependencies |
| 0.0.33 | 2024-10-29 | [47053](https://github.com/airbytehq/airbyte/pull/47053) | Update dependencies |
| 0.0.32 | 2024-10-12 | [46434](https://github.com/airbytehq/airbyte/pull/46434) | Update dependencies |
| 0.0.31 | 2024-09-28 | [46192](https://github.com/airbytehq/airbyte/pull/46192) | Update dependencies |
| 0.0.30 | 2024-09-21 | [45553](https://github.com/airbytehq/airbyte/pull/45553) | Update dependencies |
| 0.0.29 | 2024-09-07 | [45322](https://github.com/airbytehq/airbyte/pull/45322) | Update dependencies |
| 0.0.28 | 2024-08-31 | [45017](https://github.com/airbytehq/airbyte/pull/45017) | Update dependencies |
| 0.0.27 | 2024-08-24 | [44717](https://github.com/airbytehq/airbyte/pull/44717) | Update dependencies |
| 0.0.26 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.0.25 | 2024-08-17 | [44292](https://github.com/airbytehq/airbyte/pull/44292) | Update dependencies |
| 0.0.24 | 2024-08-12 | [43734](https://github.com/airbytehq/airbyte/pull/43734) | Update dependencies |
| 0.0.23 | 2024-08-10 | [43702](https://github.com/airbytehq/airbyte/pull/43702) | Update dependencies |
| 0.0.22 | 2024-08-03 | [43133](https://github.com/airbytehq/airbyte/pull/43133) | Update dependencies |
| 0.0.21 | 2024-07-27 | [42628](https://github.com/airbytehq/airbyte/pull/42628) | Update dependencies |
| 0.0.20 | 2024-07-20 | [42160](https://github.com/airbytehq/airbyte/pull/42160) | Update dependencies |
| 0.0.19 | 2024-07-13 | [41802](https://github.com/airbytehq/airbyte/pull/41802) | Update dependencies |
| 0.0.18 | 2024-07-10 | [41384](https://github.com/airbytehq/airbyte/pull/41384) | Update dependencies |
| 0.0.17 | 2024-07-09 | [41165](https://github.com/airbytehq/airbyte/pull/41165) | Update dependencies |
| 0.0.16 | 2024-07-06 | [40926](https://github.com/airbytehq/airbyte/pull/40926) | Update dependencies |
| 0.0.15 | 2024-06-29 | [40634](https://github.com/airbytehq/airbyte/pull/40634) | Update dependencies |
| 0.0.14 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.0.13 | 2024-06-25 | [40431](https://github.com/airbytehq/airbyte/pull/40431) | Update dependencies |
| 0.0.12 | 2024-06-23 | [40222](https://github.com/airbytehq/airbyte/pull/40222) | Update dependencies |
| 0.0.11 | 2024-06-22 | [40068](https://github.com/airbytehq/airbyte/pull/40068) | Update dependencies |
| 0.0.10  | 2024-04-15 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Updated CDK & pytest version to fix security vulnerabilities |
| 0.0.9   | 2023-12-11 | [#33303](https://github.com/airbytehq/airbyte/pull/33303) | Fix bug with embedding special tokens                        |
| 0.0.8   | 2023-12-01 | [#32697](https://github.com/airbytehq/airbyte/pull/32697) | Allow omitting raw text                                      |
| 0.0.7   | 2023-11-16 | [#32608](https://github.com/airbytehq/airbyte/pull/32608) | Support deleting records for CDC sources                     |
| 0.0.6   | 2023-11-13 | [#32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema                                          |
| 0.0.5   | 2023-10-23 | [#31563](https://github.com/airbytehq/airbyte/pull/31563) | Add field mapping option                                     |
| 0.0.4   | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329) | Add OpenAI-compatible embedder option                        |
| 0.0.3   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size                               |
| 0.0.2   | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820) | Update CDK                                                   |
| 0.0.1   | 2023-09-08 | [#30023](https://github.com/airbytehq/airbyte/pull/30023) | 🎉 New Destination: Chroma (Vector Database)                 |

</details>
