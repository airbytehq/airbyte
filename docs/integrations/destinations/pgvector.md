# PGVector Destination

## Overview

This page guides you through setting up the PGVector destination connector. The connector writes each
record as one or more embedded text chunks into a Postgres table, so you can run similarity searches
in Postgres instead of a dedicated vector database.

Configuring the destination has three parts:

- **Processing** - Split records into chunks that fit your model's context window, and decide which
  fields to embed and which to keep as metadata.
- **Embedding** - Convert the text into a vector using an embedding model. See
  [Embedding](#embedding) for the supported services and their vector sizes.
- **Postgres connection** - Where to store the vectors. The connector writes to Postgres tables that
  use the `vector` column type provided by the pgvector extension.

## Prerequisites

To use the PGVector destination, you need:

- A Postgres database with the [pgvector](https://github.com/pgvector/pgvector) extension installed.
- Credentials for the embedding service you want to use, unless you use fake embeddings for testing.

Collect the following information before you configure the destination:

- **Host** - The host name or address of the Postgres server.
- **Port** - The port the server listens on. Defaults to the PostgreSQL standard port (5432).
- **Database** - The name of the database to write to.
- **Default Schema** - The schema the connector writes its tables into. Defaults to `public`. The
  connector writes to a single schema, and schema names are case sensitive.
- **Username** and **Password** - The Postgres user Airbyte authenticates as.
- **Embedding service credentials** - The API key, and any other fields the service requires, for the
  embedding method you choose.

#### Configure network access

Make sure Airbyte can reach your Postgres database. If the database is in a VPC, you may need to
allow access from the IP address Airbyte connects from. The connector also reaches out to your
embedding service, so allow outbound access to `api.openai.com`, `api.cohere.ai`, or the base URL of
your Azure OpenAI or OpenAI-compatible service.

## Step 1: Set up Postgres

#### Permissions

The Postgres user needs to create tables and insert rows in the target schema. If the schema doesn't
exist yet, the connector creates it, so the user also needs the privilege to create schemas.

You can create a dedicated user by running:

```sql
CREATE USER airbyte_user WITH PASSWORD '<password>';
GRANT CREATE, TEMPORARY ON DATABASE <database> TO airbyte_user;
```

If you want the connector to write into a schema that already exists, grant privileges on that schema
too:

```sql
GRANT CREATE, USAGE ON SCHEMA <schema> TO airbyte_user;
```

You can also use an existing user, but a dedicated user is strongly recommended.

#### Enable pgvector

Run this once in the database you sync to. On most Postgres installations, creating the extension
requires a superuser or a managed-service role that permits extension creation. If the extension
isn't available at all, follow the [pgvector installation
instructions](https://github.com/pgvector/pgvector#installation) first.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 2: Set up the PGVector connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or your self-managed
   Airbyte instance.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **New
   destination**.
3. Select **PGVector** from the list of destination types, and enter a name for your destination.
4. In the **Processing** section, list the **Text fields to embed**, the **Fields to store as
   metadata**, and set the **Chunk size**.
5. In the **Embedding** section, choose an embedding method and enter its credentials.
6. In the **Postgres Connection** section, enter the **Host**, **Port**, **Database**, **Default
   Schema**, **Username**, and **Password** for the user you created in
   [Step 1](#step-1-set-up-postgres).
7. Click **Set up destination**.

## Naming conventions

The connector creates one table per stream, in the schema you set as the **Default Schema**. Stream
names are normalized before they're used as table names: characters are folded to lower case and
every character that isn't a letter or a digit is replaced with an underscore. Names that begin with
a digit are prefixed with an underscore.

Postgres also truncates identifiers longer than 63 bytes. Streams whose names differ only in case, in
punctuation, or beyond the first 63 bytes normalize to the same table name and overwrite each other's
data. See [Postgres SQL
identifiers](https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS)
for the full identifier rules.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Data type mapping

Fields you list as metadata fields are stored as JSON in the `metadata` column, so strings, numbers,
booleans, arrays, and nested objects are all preserved. Fields that you list as neither text fields
nor metadata fields aren't written to the destination.

## Configuration

### Processing

Each record is split into text fields and metadata fields, as configured in the **Processing**
section. All text fields are concatenated into a single string, which is then split into chunks of
the configured length. Metadata fields are stored alongside each chunk of the record they came from.
The chunking options come from the [LangChain Python
library](https://python.langchain.com/docs/introduction/).

If you leave **Text fields to embed** empty, every field in the record is embedded. If you leave
**Fields to store as metadata** empty, every field is also stored as metadata.

When specifying text fields, you can access nested fields in the record by using dot notation. For
example, `user.name` accesses the `name` field in the `user` object. You can also use wildcards to
access all fields in an object. For example, `users.*.name` accesses all `name` fields in all entries
of the `users` array.

By default, text is split on paragraph, line, sentence, and word boundaries. You can instead split on
your own list of separators, on Markdown headers, or on code structure for a specific programming
language, using the **Text splitter** option.

Chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens,
which is the maximum input length of the `text-embedding-ada-002` model.

The stream name is added to each chunk as an `_ab_stream` metadata field. For streams that sync with
the **Incremental Sync - Append + Deduped** mode and have a primary key, the primary key is also
added as an `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods. The method you choose sets the
dimension count of the `vector` column when the connector creates the table, and the connector never
alters that column afterward. Switching to a method with a different dimension count means the table
has to be recreated.

| Method | Model | Dimensions |
| :--- | :--- | :--- |
| [OpenAI](https://platform.openai.com/docs/api-reference/embeddings) | `text-embedding-ada-002` | 1536 |
| [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/reference#embeddings) | `text-embedding-ada-002` | 1536 |
| [Cohere](https://docs.cohere.com/reference/embed) | `embed-english-light-v2.0` | 1024 |
| OpenAI-compatible service | Whatever model you name | Whatever you configure |
| Fake | None. Random vectors. | 1536 |

For OpenAI, sync throughput is bound by the [OpenAI embedding API rate
limits](https://platform.openai.com/docs/guides/rate-limits). Azure OpenAI needs the API key, the
resource base URL, and the deployment name from your Azure OpenAI resource. An OpenAI-compatible
service needs the base URL, the model name, and the number of dimensions the model produces.

Fake embeddings generate random vectors. Use them to test a pipeline end to end without paying for
embedding calls. They aren't useful for search.

### Indexing and data storage

Each stream is written to a table of the same name in the default schema, and the connector creates
the schema and table if they don't exist. Every table has these columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `document_id` | string | Identifies the source record. For records with a primary key, it's `Stream_{stream name}_Key_{primary key values}`. For records without one, it's a random identifier, which means chunks can't be traced back to the record. |
| `chunk_id` | string | A random identifier for the chunk. |
| `metadata` | JSON | The metadata fields of the record, plus `_ab_stream` and, when present, `_ab_record_id`. |
| `document_content` | string | The text content of the chunk. |
| `embedding` | vector | The embedding of the chunk. |

The connector doesn't create an index on the `embedding` column. Sequential scans are fine for small
tables, but for larger ones, create an [HNSW or IVFFlat
index](https://github.com/pgvector/pgvector#indexing) yourself, using the distance operator your
queries use.

Because one record becomes several chunks, deduplication deletes every existing row for a
`document_id` and reinserts the record's current chunks, rather than updating rows in place.

## Limitations and troubleshooting

### psycopg2.OperationalError could not translate host name something@hostname to address

The connector builds its connection string from your credentials, and `@` is a reserved character in
that string. If your password contains `@`, replace it with `%40` so authentication works.

### The "Do not store raw text" setting has no effect

This destination always writes chunk text to the `document_content` column, even when the advanced
**Do not store raw text** option is enabled.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.12 | 2026-08-13 | [84364](https://github.com/airbytehq/airbyte/pull/84364) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.1.11 | 2026-07-02 | [81384](https://github.com/airbytehq/airbyte/pull/81384) | Upgrade pillow from 11.x to 12.3.0 to resolve security vulnerabilities GHSA-cfh3-3jmp-rvhc, GHSA-pwv6-vv43-88gr, GHSA-whj4-6x5x-4v2j, GHSA-xg8h-j46f-w952 |
| 0.1.10 | 2026-07-02 | [81395](https://github.com/airbytehq/airbyte/pull/81395) | Bump aiohttp to >= 3.13.3 to resolve GHSA-6mq8-rvhq-8wgg |
| 0.1.9 | 2026-03-31 | [75645](https://github.com/airbytehq/airbyte/pull/75645) | Bump version to force registry update for supportLevel change to community |
| 0.1.8 | 2025-10-21 | [68347](https://github.com/airbytehq/airbyte/pull/68347) | Update dependencies |
| 0.1.7 | 2025-10-14 | [67996](https://github.com/airbytehq/airbyte/pull/67996) | Update dependencies |
| 0.1.6 | 2025-10-07 | [67175](https://github.com/airbytehq/airbyte/pull/67175) | Update dependencies |
| 0.1.5 | 2025-09-30 | [65045](https://github.com/airbytehq/airbyte/pull/65045) | Update dependencies |
| 0.1.4 | 2025-07-05 | [61623](https://github.com/airbytehq/airbyte/pull/61623) | Update dependencies |
| 0.1.3 | 2025-05-17 | [51728](https://github.com/airbytehq/airbyte/pull/51728) | Update dependencies |
| 0.1.2 | 2025-01-11 | [45767](https://github.com/airbytehq/airbyte/pull/45767) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.1   | 2024-09-23 | [#45636](https://github.com/airbytehq/airbyte/pull/45636)     | Add default values for default_schema and port.
| 0.1.0   | 2024-09-16 | [#45428](https://github.com/airbytehq/airbyte/pull/45428)     | Add support for PGVector as a Vector destination.

</details>
