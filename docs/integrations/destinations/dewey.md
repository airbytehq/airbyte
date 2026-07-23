# Dewey

This page contains the setup guide and reference information for the Dewey destination connector.

[Dewey](https://meetdewey.com) is a managed RAG service that ingests documents and runs the chunking, embedding, indexing, and retrieval pipeline server-side. The Dewey destination connector lets you sync any Airbyte source into a Dewey collection — Dewey handles embeddings; the connector does not require an embedding provider key.

:::info
For Airbyte issues, [open a GitHub issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug%2Carea%2Fconnectors%2Cneeds-triage&projects=&template=1-issue-connector.yaml). For Dewey API issues, see the [Dewey docs](https://meetdewey.com/docs).
:::

## Overview

Each Airbyte stream maps to a Dewey collection. For every record the destination uploads a small JSON document to Dewey, tagged with `airbyte_stream:<namespace>__<stream>` and `airbyte_pk:<primary_key>` so that overwrite and append-dedup syncs can locate prior versions for deletion. The record's primary key (or a configured `title_field`) becomes the Dewey document filename, and configurable subsets of the record are projected into the indexed body and into searchable Dewey metadata.

### Output schema

Each Airbyte record becomes one Dewey document inside the configured collection.

* The document's `tags` always include `airbyte_stream:<stream_id>`. When the stream has a primary key, an additional `airbyte_pk:<pk>` tag is added.
* The document's `metadata` always includes `_ab_stream`, `_ab_namespace`, and (when present) `_ab_pk`. Any fields named in `metadata_fields` are also lifted into the document metadata.
* The document's content is either the entire record serialized as JSON (default) or the projection selected by `text_fields`.

## Supported sync modes

| Sync mode                                                                                                             | Supported? |
| :-------------------------------------------------------------------------------------------------------------------- | :--------- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes        |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes        |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes        |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes        |

### How sync modes interact with your Dewey collections

The connector identifies its own documents by the `airbyte_stream:<namespace>__<stream>` tag it stamps on every upload. It will only ever delete documents that carry one of those tags — documents you uploaded through the Dewey UI, the Dewey API, or any other tool are never touched, even when they live in the same collection that Airbyte writes to.

| Sync mode | What happens at sync start | What happens during the sync |
| :-------- | :------------------------- | :--------------------------- |
| **Overwrite** | List every document in the target collection, filter to those tagged with the stream's `airbyte_stream:` tag, and batch-delete them. | Upload new records. |
| **Append** | Nothing. | Upload new records. |
| **Append + Deduped** | Nothing. | Before each batch flush, look up documents tagged with the same `airbyte_pk:<pk>` tags as the records about to be flushed and batch-delete them, so the upload effectively replaces the prior version. |

Dedup uses the airbyte stream's `primary_key` to construct the `airbyte_pk:` tag. Streams without a primary key fall back to append behavior.

Tag matching is case-insensitive on the Dewey side: tags are normalized to lowercase at storage time. The connector lowercases on the client side as well, so round-tripping mixed-case stream or PK values works correctly.

## Getting started

You need a Dewey project to use this connector.

1. Sign up for Dewey and create a project at [meetdewey.com](https://meetdewey.com).
2. Create a collection in the Dewey UI (or via `POST /v1/collections`) for each Airbyte stream you plan to sync. Note the collection ID.
3. Generate a project API key in the Dewey console — `dwy_test_...` for sandbox runs, `dwy_live_...` for production.

### Configure the destination in Airbyte

You will need:

* (Required) **API Key** — your `dwy_live_...` or `dwy_test_...` key. Stored as a secret.
* (Optional) **Base URL** — defaults to `https://api.meetdewey.com/v1`. Override only for self-hosted Dewey deployments.
* (Required) **Stream → Collection Mapping** — maps each Airbyte stream name to a Dewey collection ID. Use `<namespace>__<stream>` as the key when the source emits namespaced records. Streams not listed here are skipped unless **Auto-create Collections** is enabled.
* (Optional) **Auto-create Collections** — if enabled, any stream missing from the mapping is materialized as a new Dewey collection named `airbyte_<namespace>__<stream>` on first use. Existing Dewey collections are never modified or repurposed by this option — it only creates new ones for streams the connector hasn't seen before. Disable it (the default) when you want strict, explicit routing.
* (Optional) **Text Fields** — dot-path fields whose values become the indexed body of each document. Empty (default) uploads the entire record as JSON.
* (Optional) **Title Field** — dot-path field used as the Dewey filename. Falls back to the record's primary key, or a UUID if neither is set.
* (Optional) **Metadata Fields** — dot-path fields lifted into Dewey's per-document `metadata` for query-time filtering.
* (Optional) **Parallelize** — upload up to 8 documents concurrently.
* (Optional) **Flush Interval** — number of records buffered before each upload batch (default 100).

## Why this destination doesn't compute embeddings

Other vector destinations in Airbyte (`destination-pinecone`, `destination-weaviate`, `destination-chroma`, etc.) build on the `airbyte_cdk.destinations.vector_db_based` framework, which requires the user to configure an embedding provider (OpenAI, Cohere, …) and an `embedder + indexer + writer + document_processor` pipeline. That pattern fits raw vector stores where the client must compute embeddings before pushing vectors.

Dewey, like Vectara, is a managed RAG service: chunking, embedding, and indexing happen server-side, optionally with BYOK. So this destination follows the simpler `destination-vectara` pattern — a thin HTTP client that hands documents to Dewey and lets it run the pipeline. No embedding provider configuration is required (or accepted) by this connector. Configure embedding model, chunk size, and BYOK on the Dewey collection itself.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The namespace is included in the `_ab_stream` metadata and in every `airbyte_stream:` tag (e.g. `airbyte_stream:public__orders`).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                  |
| :------ | :--------- | :----------- | :----------------------- |
| 0.1.0   | 2026-05-04 | TBD          | Initial release          |

</details>
