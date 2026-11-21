# openGauss DataVec

## Overview

This page guides you through the process of setting up the openGauss DataVec destination connector.

openGauss DataVec stores embedded record chunks in openGauss tables using a `vector` column. Like other Airbyte vector destinations, this connector has three parts:

- Processing - Split records into chunks, choose which fields are embedded as text, and choose which fields are stored as metadata.
- Embedding - Convert the selected text into vector embeddings using a supported embedding provider.
- Indexing - Store chunk content, metadata, and embedding vectors in openGauss DataVec tables.

The connector uses the Airbyte CDK vector destination framework for document processing, text splitting, embedding, and writer orchestration.

## Prerequisites

To use the openGauss DataVec destination, you need:

- An openGauss database that can be reached from Airbyte.
- DataVec/vector support enabled in the target openGauss database. The connector creates columns with the `vector(<dimensions>)` type.
- A database user with permission to create schemas, create tables, create indexes, drop/rename tables for overwrite syncs, and insert/delete rows.
- An account with API access for your embedding provider. This is not required if you use the Fake embeddings option for testing.

You need the following information to configure the destination:

- **Host** - The hostname or IP address of your openGauss database.
- **Port** - The database port. Defaults to `5432`.
- **Database** - The database name to sync into.
- **Default Schema** - The schema used when an Airbyte stream does not have a namespace. Defaults to `public`.
- **Username** - The database user.
- **Password** - The database password.
- **SSL Mode** - The SSL mode for the database connection.
- **Embedding configuration** - The API key and provider-specific settings for the embedding method.

### Permissions

Use a dedicated database user for Airbyte when possible. The user must be able to create and modify destination objects. The exact grant syntax depends on your openGauss deployment and security model, but the user needs privileges equivalent to:

- Connect to the target database.
- Create schemas and tables.
- Insert rows into destination tables.
- Delete rows from destination tables when using Append + Deduped.
- Create indexes.
- Drop and rename tables when using Overwrite.

### DataVec setup

Before running a sync, verify that the target database accepts the `vector` type with the dimensions produced by your embedding method. For example, if you use an embedding method with 1536 dimensions, openGauss must be able to create a column like:

```sql
embedding vector(1536)
```

The connector does not create or install the DataVec extension for you.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

### Sync behavior

The connector writes records at chunk level. One source record can produce multiple rows in the destination table.

- **Overwrite** - The connector creates a staging table named `_airbyte_tmp_<stream>`, bulk loads chunks into the staging table with `COPY`, then drops the previous final table and renames the staging table to the final table after a successful sync.
- **Append** - The connector creates the final stream table if needed and bulk appends chunks directly to it with `COPY`.
- **Append + Deduped** - The connector creates the final stream table if needed, creates an index on `document_id`, deletes old chunks for each incoming document id, then bulk appends the new chunks directly to the final table with `COPY`.

## Destination table layout

Each Airbyte stream is written to one openGauss table. Airbyte namespaces map to openGauss schemas. If a stream has no namespace, the connector uses the configured default schema.

Destination table names follow this pattern:

```text
<normalized_namespace_or_default_schema>.<normalized_stream_name>
```

The connector creates tables with the following columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `document_id` | `text` | Record-level document id. Chunks from the same source record share the same `document_id`. |
| `chunk_id` | `text` | Chunk-level id generated from `document_id`, the chunk index, and a content hash. |
| `content` | `text` | The chunk text. This column is omitted when **Do not store raw text** is enabled. |
| `embedding` | `vector(<embedding_dimensions>)` | The embedding vector for the chunk. The dimensions come from the selected embedding method. |
| User metadata columns | Mapped from the Airbyte schema | Metadata fields selected in Processing. Each metadata field is stored as its own column. |
| `_airbyte_extracted_at` | `timestamp with time zone` | The record emitted timestamp converted from the Airbyte record message. |
| `_airbyte_meta` | `jsonb` | Field-level write metadata. For example, values nulled because of conversion errors or `bigint` overflow. |

Example:

```sql
CREATE TABLE IF NOT EXISTS public.users (
  document_id text,
  chunk_id text,
  content text,
  embedding vector(1536),
  category text,
  source_id bigint,
  _airbyte_extracted_at timestamp with time zone,
  _airbyte_meta jsonb
);
```

## Data type mapping

Metadata fields are mapped from the Airbyte catalog JSON schema to openGauss/Postgres-compatible column types.

| Airbyte or JSON schema type | Destination type |
| :--- | :--- |
| `boolean` | `boolean` |
| `integer`, `big_integer` | `bigint` |
| `number`, `float`, `decimal` | `decimal` |
| `string` | `text` |
| `format: date` | `date` |
| `format: date-time`, `timestamp_with_timezone` | `timestamp with time zone` |
| `timestamp_without_timezone` | `timestamp` |
| `time_with_timezone` | `time with time zone` |
| `time_without_timezone` | `time` |
| `array`, `object`, union types, unknown types | `jsonb` |

If a `bigint` metadata value cannot be converted or exceeds the openGauss `bigint` range, the connector writes `null` for that field and records the change in `_airbyte_meta`.

## Configuration

### Processing

Each record is split into text fields and metadata fields as configured in the Processing section.

Text fields are concatenated into one string and split into chunks. The chunking process uses the LangChain Python text splitters provided by the Airbyte CDK. When specifying text fields, you can access nested fields with dot notation, such as `user.name`. Wildcards are also supported for text extraction, such as `users.*.name`.

Metadata fields are stored alongside each embedded chunk. Unlike Pinecone, openGauss DataVec stores each selected metadata field as a separate SQL column instead of one metadata object. When `metadata_fields` is empty, the connector uses the top-level stream fields as metadata fields.

The connector normalizes metadata column names:

- Characters other than letters, numbers, and underscores are replaced with `_`.
- Consecutive underscores are collapsed.
- Names that start with a number are prefixed with `_`.
- Names that conflict with reserved connector columns, such as `document_id`, `chunk_id`, `content`, `embedding`, `_airbyte_extracted_at`, or `_airbyte_meta`, are prefixed with `_`.
- Long identifiers are truncated and suffixed with a hash to fit openGauss identifier limits.

### Embedding

The connector can use one of the following embedding methods:

1. **OpenAI** - Uses the OpenAI API to produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**.
2. **Cohere** - Uses the Cohere API to produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.
3. **Azure OpenAI** - Uses an Azure-hosted OpenAI deployment. The embedding dimensions depend on the deployed model.
4. **OpenAI-compatible** - Uses any service that implements an OpenAI-compatible embeddings API. Configure the base URL, model name, and dimensions for your service.
5. **Fake** - Generates random vectors with **1536 dimensions** for testing.

The destination table's `embedding vector(<dimensions>)` column must match the embedding dimensions.

### Indexing

In the Indexing section, configure the openGauss connection:

- **Host**
- **Port**
- **Database**
- **Default Schema**
- **Username**
- **Password**
- **SSL Mode**

The connector supports these SSL modes:

| SSL mode | Description |
| :--- | :--- |
| `disable` | Do not use SSL. |
| `allow` | Allow SSL when required by the server. |
| `prefer` | Prefer SSL when supported by the server. |
| `require` | Require SSL encryption without validating the server certificate. |
| `verify-ca` | Require SSL and validate the server certificate chain with the configured CA certificate. |

For `verify-ca`, provide the CA certificate in PEM format. The connector writes the certificate to a temporary file and passes it to the database driver as `sslrootcert`.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

Airbyte stream namespaces become openGauss schemas. Streams without a namespace use the configured default schema.

## Limitations

- The connector creates a regular `document_id` index only for Append + Deduped syncs. It does not create vector search indexes.
- The connector does not install or enable DataVec/vector support in openGauss.
- The connector does not support `verify-full` SSL mode.
- Metadata fields that do not exist in the stream JSON schema are ignored when creating destination columns.
- Nested metadata fields are supported through dot notation when the corresponding path exists in the stream JSON schema.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2026-05-28 | | Add openGauss DataVec destination connector. |

</details>
