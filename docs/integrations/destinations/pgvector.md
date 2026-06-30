# PGVector Destination

This page guides you through setting up the PGVector destination connector.

The PGVector destination loads data in three stages:

- **Processing** - Splits individual records into chunks that fit the context window. You configure which fields to use as context and which are supplementary metadata.
- **Embedding** - Converts text into a vector representation using a pre-trained model. Supported embedding providers: OpenAI, Cohere, Azure OpenAI, OpenAI-compatible, and Fake (for testing).
- **Postgres connection** - Stores the vectors in Postgres tables using the `VECTOR` data type provided by the [pgvector](https://github.com/pgvector/pgvector) extension.

## Prerequisites

To use the PGVector destination, you need:

- An account with API access for your chosen embedding provider
- A Postgres database with support for [pgvector](https://github.com/pgvector/pgvector)

You need the following information to configure the destination:

- **Embedding service API key** - The API key for your embedding provider
- **Host** - The hostname of your Postgres database
- **Port** - The port number the server is listening on. Defaults to 5432.
- **Database** - The database name
- **Default Schema** - The schema to use. Defaults to `public`.
- **Username**
- **Password**

### Configure network access

Make sure your Postgres database can be accessed by Airbyte. If your database is within a VPC, you
may need to allow access from the IP you're using to expose Airbyte.

## Step 1: Set up Postgres

### Permissions

You need a Postgres user with permissions to create tables, write rows, and create schemas.

To create a dedicated user for Airbyte:

```sql
CREATE USER airbyte_user WITH PASSWORD '<password>';
GRANT CREATE, TEMPORARY ON DATABASE <database> TO airbyte_user;
```

You can also use a pre-existing user, but we recommend creating a dedicated user for Airbyte.

Enable the pgvector extension:

```sql
CREATE EXTENSION vector;
```

For more information, see the [pgvector documentation](https://github.com/pgvector/pgvector).

## Step 2: Set up the PGVector connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **New destination**.
3. Search for and select **PGVector**.
4. Enter the processing configuration (chunk size, text fields, metadata fields).
5. Enter the embedding configuration (provider and API key).
6. For **Host**, **Port**, and **Database**, enter the hostname, port number, and name of your Postgres database.
7. Enter the **Default Schema**. Schema names are case sensitive. The `public` schema is set by default.
8. For **Username** and **Password**, enter the credentials you created in [Step 1](#step-1-set-up-postgres).

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Data type mapping

All fields specified as metadata fields will be stored in the metadata object of the document and can be used for filtering. The following data types are allowed for metadata fields:
* String
* Number (integer or floating point, gets converted to a 64 bit floating point)
* Booleans (true, false)
* List of String

All other fields are ignored.

## Configuration

### Processing

Each record is split into text fields and metadata fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Metadata fields can only be used for filtering (not retrieval) and must be of type string, number, or boolean. All other values are ignored. There is a 40 KB limit on the total size of the metadata saved for each entry. Options for configuring the chunking process use the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. **OpenAI** - Uses the [OpenAI API](https://platform.openai.com/docs/api-reference/embeddings) to produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration is constrained by the [OpenAI rate limits](https://platform.openai.com/docs/guides/rate-limits/overview).
2. **Cohere** - Uses the [Cohere API](https://docs.cohere.com/reference/embed) to produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.
3. **Azure OpenAI** - Uses an Azure-hosted OpenAI deployment for embeddings.
4. **OpenAI-compatible** - Uses any API that implements the OpenAI embeddings interface.

For testing purposes, you can use the Fake embeddings integration, which generates random embeddings suitable for testing a data pipeline without incurring embedding costs.

### Indexing and data storage

All streams are stored in a table with the same name as the stream. The table is created if it doesn't exist. Each table has the following columns:

- `document_id` (string) - The unique identifier of the document, created from the primary keys in the stream schema
- `chunk_id` (string) - The unique identifier of the chunk, created by appending the chunk number to the document_id
- `metadata` (variant) - The metadata of the document, stored as key-value pairs
- `document_content` (string) - The text content of the chunk
- `embedding` (vector) - The embedding of the chunk, stored as a list of floats

## Limitations & troubleshooting

### psycopg2.OperationalError could not translate host name something@hostname to address

Given your password contains the character `@`, it is likely that the connection string will not be created properly given it is a reserved character. If it is the case, we suggest replacing `@` to `%40` (the equivalent UTF-8 character) in order for the authentication to properly work.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
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
