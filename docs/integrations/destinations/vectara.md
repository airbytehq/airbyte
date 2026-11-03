# Vectara

This page contains the setup guide and reference information for the Vectara destination connector.

[Vectara](https://vectara.com/) is the trusted GenAI platform that provides Retrieval Augmented Generation or [RAG](https://vectara.com/grounded-generation/) as a service.

The Vectara destination connector allows you to connect any Airbyte source to Vectara and ingest data into Vectara for your RAG pipeline.

:::info
If you have issues, use the following public channels for support:

- For Airbyte related issues such as data source or processing: [Open a Github issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug%2Carea%2Fconnectors%2Cneeds-triage&projects=&template=1-issue-connector.yaml)
- For Vectara related issues such as data indexing or RAG: Create a post in the [Vectara forum](https://discuss.vectara.com/) or reach out on [Vectara's Discord server](https://discord.gg/GFb8gMz6UH)

:::

## Overview

The Vectara destination connector supports Full Refresh Overwrite, Full Refresh Append, and Incremental Append. It uses the [Vectara REST API v2](https://docs.vectara.com/docs/rest-api/).

### Output schema

The connector writes all streams into a single Vectara corpus, which you specify by name in the connector configuration. Each record becomes one structured document in that corpus:

- **Sections**: Each configured text field becomes one document section, formatted as `field_name: value`.
- **Title**: The value of the configured title field, or `Untitled` if you don't set a title field or the record doesn't contain it.
- **Metadata**: The configured metadata fields, plus an `_ab_stream` field that contains `{namespace}_{stream_name}` and identifies the source stream. Values that aren't strings, numbers, or booleans are stored as JSON-encoded strings.
- **Document ID**: If the stream has a primary key, the document ID is built from the namespace, stream name, and primary key values. If the stream has no primary key, the connector generates a random ID for each record.

The connector looks up the corpus by its exact name:

- If no corpus with that name exists, the connector creates one. It derives the corpus key from the name by replacing any character other than letters, digits, `_`, `=`, and `-` with `_`, and truncating the result to 50 characters. It also creates the `_ab_stream` filter attribute on the new corpus.
- If exactly one corpus with that name exists, the connector uses it.
- If more than one corpus has that name, the connection check fails because the connector can't determine which corpus to use.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

How the sync modes behave in Vectara:

- **Full Refresh - Overwrite**: At the start of the sync, the connector deletes every document in the corpus whose `_ab_stream` metadata matches the stream, then indexes the new records. The stream's documents are unavailable in the corpus until the sync re-indexes them.
- **Append modes and primary keys**: If a stream has a primary key and a document with the same ID already exists in the corpus, Vectara rejects the new document and the connector keeps the existing one. Updated records with an existing primary key aren't re-indexed in append modes. To pick up changes to existing records, use Full Refresh - Overwrite. If a stream has no primary key, every synced record is indexed as a new document, so repeated syncs can create duplicates.

## Getting started

You need a Vectara account to use Vectara with Airbyte.

1. [Sign up](https://vectara.com/integrations/airbyte) for a Vectara account if you don't already have one.
2. Optionally, create the corpus you want to load data into. If you skip this step, the connector creates the corpus for you during the first connection check or sync.
   - To create a corpus in the Vectara console, click **Corpora** and then **Create corpus**. Enter a name and a key for the corpus. For details, see [Create a Corpus](https://docs.vectara.com/docs/console-ui/creating-a-corpus).
   - If you create the corpus yourself, you **must** add a document-level filter attribute named `_ab_stream` with the **Text** data type, and mark it as indexed. The connector uses this attribute to identify source streams and to delete a stream's documents during Full Refresh - Overwrite syncs.
   - Optionally, add filter attributes for any other metadata fields you want to filter on.
3. Create an app client for OAuth 2.0 authentication. In the Vectara console, go to **API access** > **App clients** and click **Create app client**. Give the client roles that allow it to list and create corpora, and to index, list, and delete documents in your corpus. Copy the **Client ID** and **Client Secret**. For details, see [App Clients for OAuth](https://docs.vectara.com/docs/console-ui/app-clients) and [OAuth 2.0](https://docs.vectara.com/docs/security/authentication/oauth-2).

### Set up the Vectara destination in Airbyte

Configure the Vectara destination with the following information:

- (Required) **OAuth Client ID** and **OAuth Client Secret**: The credentials of the app client you created.
- (Optional) **Customer ID**: Kept only for backward compatibility. Vectara API v2 authenticates with the OAuth 2.0 client credentials alone, so you can leave this field empty.
- (Required) **Corpus Name**: The name of the corpus to load data into. If no corpus with this name exists, the connector creates it.
- (Optional) **Parallelize**: Index documents into Vectara using multiple threads. Defaults to `false`.

You can also control how the connector maps record fields to Vectara documents. These settings apply to all streams. Fields that don't exist in a record are ignored. To reference nested fields, use dot notation, for example `user.name`. To reference a field in every element of an array, use a wildcard, for example `users.*.name`.

- **Text fields to index with Vectara** (`text_fields`): The fields that become document sections, which Vectara uses for search and summarization. If you don't specify any, all fields are text fields. Each record must contain at least one configured text field, or the sync fails.
- **Text field to use as document title with Vectara** (`title_field`): The field that populates each document's title.
- **Fields to store as metadata** (`metadata_fields`): The fields to store as document metadata. If you don't specify any, all fields are stored as metadata. When a nested path matches multiple values, the connector stores them as an array in a metadata field named after the path.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). All namespaces write to the same corpus. The namespace is part of the `_ab_stream` metadata value, so streams with the same name in different namespaces remain distinguishable.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                      |
|:--------| :--------- | :-------------------------------------------------------- | :----------------------------------------------------------- |
| 0.3.0 | 2026-11-03 | [90862](https://github.com/airbytehq/airbyte/pull/90862) | Upgrade to Python 3.13 (python-connector-base 4.1.1) and airbyte-cdk 7 |
| 0.2.32 | 2026-10-07 | [88339](https://github.com/airbytehq/airbyte/pull/88339) | Migrate from the retired Vectara API v1 (and per-customer Cognito OAuth endpoint) to API v2 / `auth.vectara.com` |
| 0.2.31 | 2024-11-25 | [48659](https://github.com/airbytehq/airbyte/pull/48659) | Update dependencies |
| 0.2.30 | 2024-11-04 | [48222](https://github.com/airbytehq/airbyte/pull/48222) | Update dependencies |
| 0.2.29 | 2024-10-29 | [47744](https://github.com/airbytehq/airbyte/pull/47744) | Update dependencies |
| 0.2.28 | 2024-10-23 | [47084](https://github.com/airbytehq/airbyte/pull/47084) | Update dependencies |
| 0.2.27 | 2024-10-12 | [46812](https://github.com/airbytehq/airbyte/pull/46812) | Update dependencies |
| 0.2.26 | 2024-10-05 | [46438](https://github.com/airbytehq/airbyte/pull/46438) | Update dependencies |
| 0.2.25 | 2024-09-28 | [46114](https://github.com/airbytehq/airbyte/pull/46114) | Update dependencies |
| 0.2.24 | 2024-09-21 | [45806](https://github.com/airbytehq/airbyte/pull/45806) | Update dependencies |
| 0.2.23 | 2024-09-14 | [45481](https://github.com/airbytehq/airbyte/pull/45481) | Update dependencies |
| 0.2.22 | 2024-09-07 | [45324](https://github.com/airbytehq/airbyte/pull/45324) | Update dependencies |
| 0.2.21 | 2024-08-31 | [45021](https://github.com/airbytehq/airbyte/pull/45021) | Update dependencies |
| 0.2.20 | 2024-08-24 | [44657](https://github.com/airbytehq/airbyte/pull/44657) | Update dependencies |
| 0.2.19 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.18 | 2024-08-17 | [44310](https://github.com/airbytehq/airbyte/pull/44310) | Update dependencies |
| 0.2.17 | 2024-08-12 | [43858](https://github.com/airbytehq/airbyte/pull/43858) | Update dependencies |
| 0.2.16 | 2024-08-10 | [43494](https://github.com/airbytehq/airbyte/pull/43494) | Update dependencies |
| 0.2.15 | 2024-08-03 | [43153](https://github.com/airbytehq/airbyte/pull/43153) | Update dependencies |
| 0.2.14 | 2024-07-27 | [42705](https://github.com/airbytehq/airbyte/pull/42705) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42168](https://github.com/airbytehq/airbyte/pull/42168) | Update dependencies |
| 0.2.12 | 2024-07-13 | [41829](https://github.com/airbytehq/airbyte/pull/41829) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41362](https://github.com/airbytehq/airbyte/pull/41362) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41140](https://github.com/airbytehq/airbyte/pull/41140) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40953](https://github.com/airbytehq/airbyte/pull/40953) | Update dependencies |
| 0.2.8 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.2.7 | 2024-06-25 | [40321](https://github.com/airbytehq/airbyte/pull/40321) | Update dependencies |
| 0.2.6 | 2024-06-22 | [39973](https://github.com/airbytehq/airbyte/pull/39973) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39193](https://github.com/airbytehq/airbyte/pull/39193) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-05-20 | [38432](https://github.com/airbytehq/airbyte/pull/38432) | [autopull] base image + poetry + up_to_date |
| 0.2.3   | 2024-03-22 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Updated CDK & pytest version to fix security vulnerabilities |
| 0.2.2   | 2024-03-22 | [#36261](https://github.com/airbytehq/airbyte/pull/36261) | Move project to Poetry                                       |
| 0.2.1   | 2024-03-05 | [#35206](https://github.com/airbytehq/airbyte/pull/35206) | Fix: improved title parsing                                  |
| 0.2.0   | 2024-01-29 | [#34579](https://github.com/airbytehq/airbyte/pull/34579) | Add document title file configuration                        |
| 0.1.0   | 2023-11-10 | [#31958](https://github.com/airbytehq/airbyte/pull/31958) | 🎉 New Destination: Vectara (Vector Database)                |

</details>
