# Snowflake Cortex Destination

This destination writes records into Snowflake tables that use the [`VECTOR`](https://docs.snowflake.com/en/sql-reference/data-types-vector) data type, so you can query them with [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex) functions such as `VECTOR_COSINE_SIMILARITY` or with Cortex Search and LLM functions.

Every sync does three things:

- **Processing**: splits each record into text chunks that fit the embedding model's context window, and decides which fields become embedded text and which become metadata.
- **Embedding**: turns each chunk into a vector by calling an embedding service that you configure, such as OpenAI or Cohere. The connector calls that service directly. It does not use Snowflake's `EMBED_TEXT_*` functions, so embedding happens outside your Snowflake account and is billed by the embedding provider.
- **Indexing**: writes one row per chunk into a Snowflake table named after the stream.

## Prerequisites

- A Snowflake account, and a warehouse, database, and schema for Airbyte to write to.
- A Snowflake user and a role with `USAGE` on the warehouse, database, and schema, and `CREATE TABLE` on the schema. The connector creates, replaces, and deletes tables in the schema you configure, so a read-only role isn't sufficient.
- An API key for an embedding service, unless you use the fake embeddings option for testing.

### Authentication

This destination signs in to Snowflake with a username and password. It doesn't support key pair authentication, OAuth, or SSO, so you can't use a Snowflake user that requires MFA or an external identity provider.

Snowflake is [phasing out sign-in with only a password](https://docs.snowflake.com/en/user-guide/security-mfa-rollout). Because no person is present to answer an MFA prompt during a sync, create a dedicated user with `TYPE = LEGACY_SERVICE`, which Snowflake exempts from MFA enforcement. Check Snowflake's rollout schedule for the dates that apply to your account, because that exemption is temporary.

## Configure the destination

### Snowflake connection

| Field | Description |
| :--- | :--- |
| Host | Your account identifier, in the form `<organization>-<account>` — the part of your account URL before `.snowflakecomputing.com`. |
| Role | The role the connector activates for the session. |
| Warehouse | The warehouse that runs the load. |
| Database | The database that holds the tables. |
| Default Schema | The schema the connector writes to. It's created if it doesn't exist. |
| Username | The Snowflake user. |
| Password | The password for that user. |

### Embedding

Choose one embedding option. The number of dimensions the option produces determines the width of the `VECTOR(FLOAT, n)` column, and Snowflake supports at most 4096 dimensions.

| Option | Model | Dimensions |
| :--- | :--- | :--- |
| OpenAI | `text-embedding-ada-002` | 1536 |
| Azure OpenAI | The deployment you point at, which must serve `text-embedding-ada-002` | 1536 |
| Cohere | `embed-english-light-v2.0` | 1024 |
| OpenAI-compatible | The model you name on your own endpoint | You specify |
| Fake | None. Generates random vectors for testing without embedding costs. | 1536 |

Sync speed is usually limited by the embedding service, not by Snowflake. For OpenAI, the connector batches chunks to stay under the token limits described in the [OpenAI rate limit documentation](https://platform.openai.com/docs/guides/rate-limits).

Changing the embedding option changes the vector length, and the connector doesn't alter the type of an existing `embedding` column. If you switch options for a connection that has already synced, drop the affected tables so the connector recreates them.

### Processing

The connector concatenates the fields you list as text fields, then splits the result into chunks. Chunk length is measured in tokens produced by the `tiktoken` library, up to 8191 tokens, the limit of `text-embedding-ada-002`. Configure an overlap if you want consecutive chunks to share context. Chunking uses the [LangChain](https://python.langchain.com/docs/introduction/) text splitters, and you can split on a separator, on Markdown headers, or on the syntax of a programming language.

When you name text or metadata fields, use dot notation for nested fields, such as `user.name`, and wildcards to reach into arrays, such as `users.*.name`. Field name mappings rename the extracted fields after extraction, so map `from_field` to the path you selected, not to the original nested field name.

Metadata fields are stored as-is in the `metadata` column and aren't embedded, so you can filter on them but not retrieve them by similarity. The connector adds these metadata fields itself:

- `_ab_stream` identifies the source stream and namespace.
- `_ab_record_id` holds the stream identifier and the record's primary key values. It's only added for streams that sync with deduplication and define a primary key.

### Output table schema

Each stream is written to a table with the same name as the stream. The table has these columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `document_id` | `VARCHAR` | Identifies the source record, in the form `Stream_<stream>_Key_<primary key values>`. Streams with no primary key get a random value instead, which means the connector can't recognize later versions of the same record. |
| `chunk_id` | `VARCHAR` | Identifies the chunk. Each record produces one row per chunk. |
| `metadata` | `VARIANT` | The metadata fields for the record. |
| `document_content` | `VARIANT` | The text of the chunk. |
| `embedding` | `VECTOR(FLOAT, n)` | The chunk's vector, where `n` is the dimension count of your embedding option. |

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

Because one record becomes several rows, deduplication works on whole documents: for every `document_id` in the batch, the connector deletes all existing chunks of that document before inserting the new ones. Deduplication needs a primary key, so define one on the stream if you sync with dedup.

## Namespace support

This destination doesn't support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). Every stream is written to the schema you set in **Default Schema**.

## Limitations

- Password authentication only, as described in [Authentication](#authentication).
- Vectors are capped at Snowflake's limit of 4096 dimensions.
- The `embedding` column can't be used as a clustering key, and `VECTOR` values can't be nested inside a `VARIANT`. See Snowflake's [`VECTOR` data type documentation](https://docs.snowflake.com/en/sql-reference/data-types-vector) for the full list of restrictions.
- Chunk text is always written to `document_content`. There's no option to store vectors without the source text.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.30 | 2026-08-13 | [84363](https://github.com/airbytehq/airbyte/pull/84363) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.2.29 | 2026-07-02 | [81385](https://github.com/airbytehq/airbyte/pull/81385) | Upgrade pillow from 11.x to 12.3.0 to resolve security vulnerabilities GHSA-cfh3-3jmp-rvhc, GHSA-pwv6-vv43-88gr, GHSA-whj4-6x5x-4v2j, GHSA-xg8h-j46f-w952 |
| 0.2.28 | 2026-03-31 | [75645](https://github.com/airbytehq/airbyte/pull/75645) | Bump version to force registry update for supportLevel change to community |
| 0.2.27 | 2025-10-21 | [68344](https://github.com/airbytehq/airbyte/pull/68344) | Update dependencies |
| 0.2.26 | 2025-10-14 | [63066](https://github.com/airbytehq/airbyte/pull/63066) | Update dependencies |
| 0.2.25 | 2025-05-17 | [51743](https://github.com/airbytehq/airbyte/pull/51743) | Update dependencies |
| 0.2.24 | 2025-03-01 | [54735](https://github.com/airbytehq/airbyte/pull/54735) | Bump snowflake-connector-python from 3.12.2 to 3.13.1 in /airbyte-integrations/connectors/destination-snowflake-cortex |
| 0.2.23 | 2025-01-11 | [45786](https://github.com/airbytehq/airbyte/pull/45786) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.22 | 2024-09-14 | [45489](https://github.com/airbytehq/airbyte/pull/45489) | Update dependencies |
| 0.2.21 | 2024-09-07 | [45313](https://github.com/airbytehq/airbyte/pull/45313) | Update dependencies |
| 0.2.20 | 2024-08-31 | [44982](https://github.com/airbytehq/airbyte/pull/44982) | Update dependencies |
| 0.2.19 | 2024-08-24 | [44694](https://github.com/airbytehq/airbyte/pull/44694) | Update dependencies |
| 0.2.18 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.17 | 2024-08-17 | [43898](https://github.com/airbytehq/airbyte/pull/43898) | Update dependencies |
| 0.2.16 | 2024-08-10 | [43584](https://github.com/airbytehq/airbyte/pull/43584) | Update dependencies |
| 0.2.15 | 2024-08-03 | [43093](https://github.com/airbytehq/airbyte/pull/43093) | Update dependencies |
| 0.2.14 | 2024-07-27 | [42684](https://github.com/airbytehq/airbyte/pull/42684) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42263](https://github.com/airbytehq/airbyte/pull/42263) | Update dependencies |
| 0.2.12 | 2024-07-13 | [41758](https://github.com/airbytehq/airbyte/pull/41758) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41368](https://github.com/airbytehq/airbyte/pull/41368) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41173](https://github.com/airbytehq/airbyte/pull/41173) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40836](https://github.com/airbytehq/airbyte/pull/40836) | Update dependencies |
| 0.2.8 | 2024-06-29 | [40630](https://github.com/airbytehq/airbyte/pull/40630) | Update dependencies |
| 0.2.7 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.2.6 | 2024-06-25 | [40468](https://github.com/airbytehq/airbyte/pull/40468) | Update dependencies |
| 0.2.5 | 2024-06-23 | [40225](https://github.com/airbytehq/airbyte/pull/40225) | Update dependencies |
| 0.2.4 | 2024-06-22 | [40047](https://github.com/airbytehq/airbyte/pull/40047) | Update dependencies |
| 0.2.3 | 2024-06-04 | [38955](https://github.com/airbytehq/airbyte/pull/38955) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.2   | 2024-06-04 | [#39092](https://github.com/airbytehq/airbyte/pull/39092) | Fix writing when multiple chunks exist for a document.
| 0.2.1   | 2024-06-03 | [#38830](https://github.com/airbytehq/airbyte/pull/38830) | Add handling for unexpected/undefined state codes.
| 0.2.0   | 2024-05-30 | [#38337](https://github.com/airbytehq/airbyte/pull/38337) | Fix `merge` behavior when multiple chunks exist for a document. Includes additional refactoring and improvements.
| 0.1.2   | 2024-05-17 | [#38327](https://github.com/airbytehq/airbyte/pull/38327) | Fix chunking related issue.
| 0.1.1   | 2024-05-15 | [#38206](https://github.com/airbytehq/airbyte/pull/38206) | Bug fixes.
| 0.1.0   | 2024-05-14 | [#36807](https://github.com/airbytehq/airbyte/pull/36807) | Add support for Snowflake as a Vector destination.

</details>
