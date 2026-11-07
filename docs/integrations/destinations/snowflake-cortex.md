# Snowflake Cortex Destination

This destination writes records into Snowflake tables that use the [`VECTOR`](https://docs.snowflake.com/en/sql-reference/data-types-vector) data type, so you can query them with Snowflake's vector similarity functions, such as `VECTOR_COSINE_SIMILARITY`, and use the results with [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex) LLM functions.

Every sync does three things:

- **Processing**: splits each record into text chunks that fit the embedding model's context window, and decides which fields become embedded text and which become metadata.
- **Embedding**: turns each chunk into a vector by calling the embedding service you configure, such as OpenAI or Cohere. The connector calls that service directly. It doesn't use Snowflake's `EMBED_TEXT_*` functions, so embedding happens outside your Snowflake account and the embedding provider bills you for it.
- **Indexing**: writes one row per chunk into a Snowflake table named after the stream.

## Prerequisites

- A Snowflake account, a warehouse, and a database for Airbyte to write to.
- A Snowflake user and a role with `USAGE` on the warehouse, database, and schema, and `CREATE TABLE` on the schema. If the schema doesn't exist yet, the role also needs `CREATE SCHEMA` on the database. The connector creates, replaces, and deletes tables in the schema you configure, so a read-only role isn't sufficient.
- An API key or endpoint for an embedding service, unless you use the **Fake** embedding option for testing.

### Authentication

This destination signs in to Snowflake with a username and password only. It doesn't support key pair authentication, OAuth, or MFA.

:::warning
Snowflake is [deprecating single-factor password sign-ins](https://docs.snowflake.com/en/user-guide/security-mfa-rollout). Snowflake estimates that it will enforce the final phase in accounts on a rolling basis from August through October 2026, and notifies each account of its enforcement date. Once that phase is enforced in your account, service users can't sign in with a password, existing `LEGACY_SERVICE` users are converted to `SERVICE` users, and human users must provide a second factor. After that, this destination can't sign in to your account. The rollout doesn't apply to trial accounts or reader accounts.
:::

## Configure the destination

### Snowflake connection

| Field | Description |
| :--- | :--- |
| Host | Your account identifier, which is the part of your account URL before `.snowflakecomputing.com`. For example, `myorg-myaccount`. |
| Role | The role the connector activates for the session. |
| Warehouse | The warehouse that runs the load. |
| Database | The database that holds the tables. |
| Default Schema | The schema the connector writes to. The connector creates it if it doesn't exist. |
| Username | The Snowflake user. |
| Password | The password for that user. |

### Embedding

Choose one embedding option. The number of dimensions the option produces sets the width of the `VECTOR(FLOAT, n)` column. Snowflake supports at most 4096 dimensions.

| Option | Model | Dimensions |
| :--- | :--- | :--- |
| OpenAI | `text-embedding-ada-002` | 1536 |
| Azure OpenAI | The deployment you configure. It must produce 1536-dimension vectors, such as a `text-embedding-ada-002` deployment. | 1536 |
| Cohere | `embed-english-light-v2.0` | 1024 |
| OpenAI-compatible | The model you name on your own endpoint | The value you set in **Embedding dimensions** |
| Fake | None. Generates random vectors so you can test a pipeline without embedding costs. | 1536 |

The embedding service usually limits sync speed more than Snowflake does. For OpenAI and Azure OpenAI, the connector batches chunks to stay under 150,000 tokens per request and retries when the API returns a rate limit error. See the [OpenAI rate limit documentation](https://platform.openai.com/docs/guides/rate-limits) for your account's limits.

The connector doesn't change the type of an existing `embedding` column. If you switch to an option with a different number of dimensions after a connection has synced, drop the affected tables or run a Full Refresh - Overwrite sync so the connector recreates them with the new width.

### Processing

The connector concatenates the fields you list in **Text fields to embed**, then splits the result into chunks. If you don't list any text fields, the connector embeds every field in the record. If a record contains none of the text fields you listed, the sync fails with a configuration error.

Chunk length is measured in tokens produced by the `tiktoken` library, from 1 to 8191 tokens. Set **Chunk overlap** if you want consecutive chunks to share context. The connector uses [LangChain](https://python.langchain.com/docs/introduction/) text splitters, and you can split on separators, on Markdown headers, or on the syntax of a programming language.

To name nested fields, use dot notation, such as `user.name`. To reach into arrays, use wildcards, such as `users.*.name`. **Field name mappings** rename fields after extraction, so set **From field name** to the path you selected, such as `user.name`, not the original nested field name.

The connector stores fields you list in **Fields to store as metadata** in the `metadata` column without embedding them, so you can filter on them but similarity search doesn't match them. If you don't list any metadata fields, the connector stores every field as metadata. The connector also adds these metadata fields:

- `_ab_stream`: The stream name, prefixed with the namespace if the stream has one.
- `_ab_record_id`: The stream identifier and the record's primary key values. The connector only adds it for streams that sync with **Incremental Sync - Append + Deduped** and define a primary key.

### Output table schema

The connector writes each stream to a table with the same name as the stream, and creates the table if it doesn't exist. The table has these columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `document_id` | `VARCHAR` | Identifies the source record, in the form `Stream_<stream>_Key_<primary key values>`. Streams with no primary key get a random value instead, so the connector can't recognize later versions of the same record. |
| `chunk_id` | `VARCHAR` | A random identifier for the chunk. Each record produces one row per chunk. |
| `metadata` | `VARIANT` | The metadata fields for the record. |
| `document_content` | `VARIANT` | The text of the chunk. |
| `embedding` | `VECTOR(FLOAT, n)` | The chunk's vector, where `n` is the number of dimensions of your embedding option. |

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

Because one record becomes several rows, deduplication works on whole documents. For every `document_id` in a batch, the connector deletes all existing chunks of that document, then inserts the new ones. Deduplication requires a primary key on the stream.

## Namespace support

This destination doesn't support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). It writes every stream to the schema you set in **Default Schema**.

## Limitations

- The connector only supports password authentication. See [Authentication](#authentication).
- Vectors are limited to Snowflake's maximum of 4096 dimensions.
- The connector always writes chunk text to `document_content`. The **Do not store raw text** option in the **Advanced** section has no effect.
- The connector doesn't remove rows for records that a CDC source marks as deleted. It skips those records, so their existing chunks stay in the table.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.31 | 2026-10-07 | [88166](https://github.com/airbytehq/airbyte/pull/88166) | Remove the ruff dev dependency so connector CI formats with the repository ruff version |
| 0.2.30 | 2026-08-13 | [84363](https://github.com/airbytehq/airbyte/pull/84363) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.2.29 | 2026-07-02 | [81385](https://github.com/airbytehq/airbyte/pull/81385) | Upgrade pillow from 11.x to 12.3.0 to resolve security vulnerabilities GHSA-cfh3-3jmp-rvhc, GHSA-pwv6-vv43-88gr, GHSA-whj4-6x5x-4v2j, GHSA-xg8h-j46f-w952 |
| 0.2.28 | 2026-03-31 | [75645](https://github.com/airbytehq/airbyte/pull/75645) | Bump version to force registry update for supportLevel change to community |
| 0.2.27 | 2025-10-21 | [68344](https://github.com/airbytehq/airbyte/pull/68344) | Update dependencies |
| 0.2.26 | 2025-10-16 | [63066](https://github.com/airbytehq/airbyte/pull/63066) | Update dependencies |
| 0.2.25 | 2025-06-09 | [51743](https://github.com/airbytehq/airbyte/pull/51743) | Update dependencies |
| 0.2.24 | 2025-03-01 | [54735](https://github.com/airbytehq/airbyte/pull/54735) | Bump snowflake-connector-python from 3.12.2 to 3.13.1 in /airbyte-integrations/connectors/destination-snowflake-cortex |
| 0.2.23 | 2025-01-15 | [45786](https://github.com/airbytehq/airbyte/pull/45786) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.22 | 2024-09-15 | [45489](https://github.com/airbytehq/airbyte/pull/45489) | Update dependencies |
| 0.2.21 | 2024-09-08 | [45313](https://github.com/airbytehq/airbyte/pull/45313) | Update dependencies |
| 0.2.20 | 2024-09-01 | [44982](https://github.com/airbytehq/airbyte/pull/44982) | Update dependencies |
| 0.2.19 | 2024-08-25 | [44694](https://github.com/airbytehq/airbyte/pull/44694) | Update dependencies |
| 0.2.18 | 2024-08-21 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.17 | 2024-08-18 | [43898](https://github.com/airbytehq/airbyte/pull/43898) | Update dependencies |
| 0.2.16 | 2024-08-11 | [43584](https://github.com/airbytehq/airbyte/pull/43584) | Update dependencies |
| 0.2.15 | 2024-08-04 | [43093](https://github.com/airbytehq/airbyte/pull/43093) | Update dependencies |
| 0.2.14 | 2024-07-28 | [42684](https://github.com/airbytehq/airbyte/pull/42684) | Update dependencies |
| 0.2.13 | 2024-07-21 | [42263](https://github.com/airbytehq/airbyte/pull/42263) | Update dependencies |
| 0.2.12 | 2024-07-14 | [41758](https://github.com/airbytehq/airbyte/pull/41758) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41368](https://github.com/airbytehq/airbyte/pull/41368) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41173](https://github.com/airbytehq/airbyte/pull/41173) | Update dependencies |
| 0.2.9 | 2024-07-07 | [40836](https://github.com/airbytehq/airbyte/pull/40836) | Update dependencies |
| 0.2.8 | 2024-06-30 | [40630](https://github.com/airbytehq/airbyte/pull/40630) | Update dependencies |
| 0.2.7 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.2.6 | 2024-06-26 | [40468](https://github.com/airbytehq/airbyte/pull/40468) | Update dependencies |
| 0.2.5 | 2024-06-24 | [40225](https://github.com/airbytehq/airbyte/pull/40225) | Update dependencies |
| 0.2.4 | 2024-06-23 | [40047](https://github.com/airbytehq/airbyte/pull/40047) | Update dependencies |
| 0.2.3 | 2024-06-05 | [38955](https://github.com/airbytehq/airbyte/pull/38955) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.2   | 2024-06-04 | [#39092](https://github.com/airbytehq/airbyte/pull/39092) | Fix writing when multiple chunks exist for a document. |
| 0.2.1   | 2024-06-04 | [#38830](https://github.com/airbytehq/airbyte/pull/38830) | Add handling for unexpected/undefined state codes. |
| 0.2.0   | 2024-05-31 | [#38337](https://github.com/airbytehq/airbyte/pull/38337) | Fix `merge` behavior when multiple chunks exist for a document. Includes additional refactoring and improvements. |
| 0.1.2   | 2024-05-18 | [#38327](https://github.com/airbytehq/airbyte/pull/38327) | Fix chunking related issue. |
| 0.1.1   | 2024-05-15 | [#38206](https://github.com/airbytehq/airbyte/pull/38206) | Bug fixes. |
| 0.1.0   | 2024-05-14 | [#36807](https://github.com/airbytehq/airbyte/pull/36807) | Add support for Snowflake as a Vector destination. |

</details>
