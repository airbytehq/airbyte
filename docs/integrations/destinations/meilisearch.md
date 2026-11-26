# Meilisearch

## Overview

The Airbyte Meilisearch destination allows you to sync data to [Meilisearch](https://www.meilisearch.com),
a search engine that makes your data searchable without writing any SQL.

### Sync overview

#### Output schema

Each stream is written to its own index in Meilisearch, named `<namespace>_<stream>`, or `<stream>`
for streams without a namespace. Characters other than letters, numbers, `-` and `_` are replaced
by `_`. Each document has an attribute for every top-level field of a record, plus:

- `_ab_pk`: the ID of the document, which is the primary key of the index. For streams synced with
  deduplication, it is the record's primary key if that is a single integer, or a string made of
  letters, numbers, `-` and `_`. Otherwise it is a hash of the primary key.
- `_airbyte_generation_id`: the generation of the sync that wrote the document, used to remove the
  documents of earlier generations after a refresh.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes                                                       |
| :----------------------------- | :------------------- | :---------------------------------------------------------- |
| Full Refresh Sync              | Yes                  |                                                             |
| Incremental - Append Sync      | Yes                  |                                                             |
| Incremental - Append + Deduped | Yes                  | Records with `_ab_cdc_deleted_at` set delete the document. |
| Namespaces                     | Yes                  |                                                             |

#### Performance and reliability

Documents are sent in batches of up to `batch_size` documents (10,000 by default). Meilisearch
indexes documents asynchronously, so the destination checkpoints the sync only once every batch
before the checkpoint has been indexed successfully. To avoid waiting for small batches when a
source checkpoints often, checkpoints are spaced out to one per batch of records, or one every 30
seconds. If Meilisearch fails to index a batch, for example because a document is invalid, the
sync fails with the error reported by Meilisearch. Requests that fail because of network issues or
temporary server errors are retried.

Append syncs deliver records at least once: when a sync is retried, records sent after its last
checkpoint are added again. Syncs with deduplication replace documents by their primary key, so
retried records don't create duplicates. A primary key of `1` and of `"1"` refer to the same
document.

When a stream is overwritten or refreshed, the existing index is kept along with its settings,
and the documents of earlier syncs are deleted once the stream has been synced completely, which
the destination learns from the stream statuses sent by Airbyte. A sync that fails part way
through leaves the earlier documents in place. Deleting earlier documents makes the
`_airbyte_generation_id` attribute filterable, which causes Meilisearch to re-index the documents
of the index once. On Airbyte versions that don't provide generations, an overwrite deletes all
documents of the index at the start of the sync instead.

Two streams can't be written to the same index. Streams whose index names would be the same once
their characters are replaced, such as `a.b` and `a_b`, make the sync fail.

## Getting started

### Requirements

To use the Meilisearch destination, you'll need a Meilisearch instance, version 1.6 or later. You
can learn about how to create one in the
[Meilisearch docs](https://www.meilisearch.com/docs/learn/getting_started/installation), or use
[Meilisearch Cloud](https://www.meilisearch.com/cloud).

### Setup guide

- **Host**: the URL at which Meilisearch can be reached, including the protocol. A local instance
  is at `http://localhost:7700` by default. For Meilisearch Cloud, use the project URL.
- **API Key**: an API key allowed the `indexes.*`, `documents.*`, `settings.*`, `tasks.get` and
  `version` actions, such as the default admin API key. See
  [securing your project](https://www.meilisearch.com/docs/learn/security/basic_security) in the
  Meilisearch docs. Leave it blank only if your instance runs without a master key.
- **Batch Size** (optional): the maximum number of documents sent in a single request.

### Upgrading to 2.0.0

Version 2.0.0 is a rewrite of the connector, and changes the names of some indexes and the IDs of
documents. See the [migration guide](./meilisearch-migrations.md) before upgrading.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------------------- |
| 2.0.0 | 2026-10-26 | [89754](https://github.com/airbytehq/airbyte/pull/89754) | Rewrite the connector: deduplication and CDC deletes, namespaces, refreshes, waiting for indexing before checkpointing, and retries |
| 1.0.25 | 2025-05-10 | [59837](https://github.com/airbytehq/airbyte/pull/59837) | Update dependencies |
| 1.0.24 | 2025-05-03 | [59302](https://github.com/airbytehq/airbyte/pull/59302) | Update dependencies |
| 1.0.23 | 2025-04-26 | [58742](https://github.com/airbytehq/airbyte/pull/58742) | Update dependencies |
| 1.0.22 | 2025-04-12 | [57603](https://github.com/airbytehq/airbyte/pull/57603) | Update dependencies |
| 1.0.21 | 2025-04-05 | [57137](https://github.com/airbytehq/airbyte/pull/57137) | Update dependencies |
| 1.0.20 | 2025-03-29 | [56616](https://github.com/airbytehq/airbyte/pull/56616) | Update dependencies |
| 1.0.19 | 2025-03-22 | [56153](https://github.com/airbytehq/airbyte/pull/56153) | Update dependencies |
| 1.0.18 | 2025-03-08 | [55372](https://github.com/airbytehq/airbyte/pull/55372) | Update dependencies |
| 1.0.17 | 2025-03-01 | [54896](https://github.com/airbytehq/airbyte/pull/54896) | Update dependencies |
| 1.0.16 | 2025-02-22 | [54221](https://github.com/airbytehq/airbyte/pull/54221) | Update dependencies |
| 1.0.15 | 2025-02-15 | [53896](https://github.com/airbytehq/airbyte/pull/53896) | Update dependencies |
| 1.0.14 | 2025-02-01 | [52876](https://github.com/airbytehq/airbyte/pull/52876) | Update dependencies |
| 1.0.13 | 2025-01-25 | [52206](https://github.com/airbytehq/airbyte/pull/52206) | Update dependencies |
| 1.0.12 | 2025-01-11 | [51270](https://github.com/airbytehq/airbyte/pull/51270) | Update dependencies |
| 1.0.11 | 2025-01-04 | [50909](https://github.com/airbytehq/airbyte/pull/50909) | Update dependencies |
| 1.0.10 | 2024-12-28 | [50460](https://github.com/airbytehq/airbyte/pull/50460) | Update dependencies |
| 1.0.9 | 2024-12-21 | [50196](https://github.com/airbytehq/airbyte/pull/50196) | Update dependencies |
| 1.0.8 | 2024-12-14 | [49550](https://github.com/airbytehq/airbyte/pull/49550) | Update dependencies |
| 1.0.7 | 2024-12-11 | [49021](https://github.com/airbytehq/airbyte/pull/49021) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.0.6 | 2024-11-04 | [48207](https://github.com/airbytehq/airbyte/pull/48207) | Update dependencies |
| 1.0.5 | 2024-10-29 | [47889](https://github.com/airbytehq/airbyte/pull/47889) | Update dependencies |
| 1.0.4 | 2024-10-28 | [47646](https://github.com/airbytehq/airbyte/pull/47646) | Update dependencies |
| 1.0.3   | 2024-07-08 | [#TODO](https://github.com/airbytehq/airbyte/pull/TODO) | Switching to Poetry and base image                                   |
| 1.0.2   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector                                   |
| 1.0.1   | 2023-12-19 | [27692](https://github.com/airbytehq/airbyte/pull/27692)  | Fix incomplete data indexing                           |
| 1.0.0   | 2022-10-26 | [18036](https://github.com/airbytehq/airbyte/pull/18036)  | Migrate MeiliSearch to Python CDK                      |
| 0.2.13  | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)  | Updated stacktrace format for any trace message errors |
| 0.2.12  | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)  | Add `-XX:+ExitOnOutOfMemoryError` JVM option           |
| 0.2.11  | 2021-12-28 | [9156](https://github.com/airbytehq/airbyte/pull/9156)    | Update connector fields title/description              |

</details>
