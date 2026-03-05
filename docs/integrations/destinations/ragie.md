
# Ragie

## Overview

The **Ragie destination connector** lets you send data from any Airbyte source into [Ragie.ai](https://www.ragie.ai), a platform for semantic search, vector storage, and AI-powered document retrieval.

This connector transforms your records into documents and ingests them into Ragie’s vector index using its API. It supports advanced options like metadata mapping, document naming, and deduplication via external IDs.

---

## Features

- Extracts vector content from specified fields.
- Attaches custom or static metadata to each document.
- Assigns document names and external IDs.
- Supports partitioning into multiple datasets (indexes).

---

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Prerequisites

- A [Ragie.ai](https://www.ragie.ai) account.
- A valid **API Key** (from the [Ragie Dashboard](https://app.ragie.ai)).
- Know your desired data schema and field mappings.

---

## Setup Instructions

### 1. In Airbyte

Go to **Destinations → + New Destination → Ragie**.

### 2. Fill in the following fields:

| Field | Description | Required |
|-------|-------------|----------|
| **API Key** | Your secret Ragie API token. | ✅ Yes |
| **Content Fields** | List of field(s) from the record to use as the **main document content** (text). If empty, the whole record is used. Supports dot notation. | ⛔ Optional |
| **Metadata Fields** | Field(s) to include as metadata. Use dot notation for nested fields. | ⛔ Optional |
| **Partition Name** | Name of the partition/index in Ragie to write into. Defaults to system partition if empty. | ⛔ Optional |
| **Mode** | Ingestion mode: `'fast'` (default) or `'hi_res'`. | ✅ Yes |
| **Document Name Field** | Field to use as the document’s display name. Auto-generated if empty. | ⛔ Optional |
| **Static Metadata (JSON)** | JSON string of key-value pairs added to every document’s metadata. | ⛔ Optional |
| **External ID Field** | Field to use as unique document ID (`external_id`) for deduplication. Required for append+dedup mode. | ⛔ Optional |
| **API URL** | URL of Ragie API. Only change if using a private Ragie deployment. Defaults to `https://api.ragie.ai`. | ⛔ Optional |

---

## Sync Modes

| Mode | Behavior |
|------|----------|
| **Append** | Adds documents to Ragie. |
| **Overwrite** | Deletes existing documents in the partition before writing. |
| **Append + Dedup** | Uses `external_id_field` to upsert (insert or update) documents. |

---

## Example

### Incoming Record:
```json
{
  "ticket_id": "1234",
  "description": "The app crashes when I click save.",
  "user": {
    "id": "u_567",
    "email": "alice@example.com"
  }
}
````

### Configuration:

```json
{
  "content_fields": ["description"],
  "metadata_fields": ["user.id", "user.email"],
  "document_name_field": "ticket_id",
  "external_id_field": "ticket_id"
}
```

### Resulting Document in Ragie:

```json
{
  "external_id": "1234",
  "name": "1234",
  "content": "The app crashes when I click save.",
  "metadata": {
    "user.id": "u_567",
    "user.email": "alice@example.com"
  }
}
```

---

## Static Metadata

You can supply additional metadata to all documents by entering a valid JSON string:

**Example:**

```json
{"source": "airbyte", "env": "prod"}
```

This will be merged with each document’s metadata.

---

## Error Handling

* All fields are validated on connection.
* If invalid content or metadata fields are referenced, errors are logged.
* Connection checks validate API credentials and endpoint reachability.

---

## Limitations

* You must supply an `external_id_field` for deduplication to work.
* Only top-level arrays or objects are currently supported in content fields.
* Ragie currently supports a limited set of ingestion modes (`fast`, `hi_res`).

---

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

| Version | Changes                                                          |
| ------- | ---------------------------------------------------------------- |
| 0.1.0   | Initial release with overwrite/append support and field mapping. |

---
