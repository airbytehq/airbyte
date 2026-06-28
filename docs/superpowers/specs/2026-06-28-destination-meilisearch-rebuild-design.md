# destination-meilisearch — Rebuild Design

**Date:** 2026-06-28
**Status:** Approved for planning
**Connector:** `airbyte-integrations/connectors/destination-meilisearch`

## Background

The Meilisearch destination is currently **archived and broken**. During archival
(PR #41023) the implementation files (`destination.py`, `writer.py`, `__init__.py`,
`spec.json`, tests) were deleted, leaving only `run.py`, `metadata.yaml`,
`pyproject.toml`, and `poetry.lock`. `run.py` still imports a `DestinationMeilisearch`
class that no longer exists, so the package does not import.

The pre-archival implementation also had design limitations relevant to this rebuild:

- Assigned every record a **random UUID** primary key (`_ab_pk`) → upsert and
  deduplication were impossible; records could only ever be appended.
- Used `add_documents` (full replace) exclusively → no partial updates.
- Supported only `overwrite` (delete + recreate index) and `append`. No append+dedup.
- Built on `airbyte-cdk < 3`.
- `pyproject.toml` defines a stray `destination-qdrant` script name.

## Goals

Rebuild the connector to support:

1. **Batch update** — configurable batch size, flush on threshold / state / stream end.
2. **Partial update** — merge fields into existing documents (`update_documents`),
   not just full replacement.
3. **Read/write** — `check` verifies both write and read scope of the API key; the
   connector performs primary-key-based upsert and deduplication.

## Non-Goals

- A Meilisearch **source** connector (read documents out of indexes).
- CDC hard-deletes (`_ab_cdc_deleted_at` handling).
- Namespaces.

## Meilisearch primitives

- **One index per stream.** Index uid = stream name with every character outside
  `[a-zA-Z0-9_-]` replaced by `_` (Meilisearch uid constraint).
- **`add_documents(docs, primary_key=...)`** — insert or **replace** the whole
  document on primary-key collision.
- **`update_documents(docs, primary_key=...)`** — insert or **merge** fields on
  collision. This is the "partial update" path.
- **`primaryKey` via query param** — passed on the document-add request. Meilisearch
  auto-creates the index and sets its primary key on the first add to an empty index.
  Passing it on subsequent batches is harmless as long as it stays consistent.
  **The primary key cannot be changed once documents exist.**
- **Document id constraint:** integer, or string of only `[a-zA-Z0-9_-]`.
- Writes are **async tasks**; each batch is followed by `wait_for_task` and the task
  status is checked — a failed task aborts the sync with a clear error.

## Key handling (Option B — use the natural primary key)

The Meilisearch index `primaryKey` is set to the stream's real primary-key field
whenever possible, so Meilisearch deduplicates/upserts natively on the actual key and
documents stay clean. Determined per stream:

| Stream's Airbyte primary key        | Index `primaryKey` | Document written as              |
| ----------------------------------- | ------------------ | -------------------------------- |
| Single, top-level field (`[["id"]]`)| that field (`id`)  | as-is                            |
| None (append / overwrite, no PK)    | synthetic `_ab_pk` | + injected random UUID           |
| Composite or nested (`[["a"],["b"]]`)| synthetic `_ab_pk`| + injected deterministic hash    |

The natural key is used directly for the common single-top-level-field case. The
synthetic `_ab_pk` fallback is used only when Meilisearch physically cannot use the
source key — it supports a single flat primary-key attribute only. The deterministic
hash (sha1 hex of the joined key-path values) keeps dedup working for composite/nested
keys; a random UUID is used when there is no key at all.

**Value constraint:** when using the natural key, values are passed through untouched
(sanitizing would silently break dedup). If a value violates Meilisearch's id rule, the
Meilisearch task fails and the error is surfaced. This constraint is documented in the
connector docs.

## Sync-mode behavior

| Destination sync mode | Index `primaryKey`                  | Operation                                              |
| --------------------- | ----------------------------------- | ------------------------------------------------------ |
| `overwrite`           | natural if single top-level, else `_ab_pk` | `delete_index` (wait) then `add_documents(primary_key=...)` |
| `append`              | `_ab_pk` (random UUID per record)   | `add_documents(primary_key="_ab_pk")`                  |
| `append_dedup`        | natural if single top-level, else `_ab_pk` | `add_documents` (replace) **or** `update_documents` (merge), per `update_method` |

`overwrite` deletes the index first, which also resets the primary key so a changed
catalog key takes effect cleanly. `append`/`append_dedup` rely on the primaryKey being
set on the first add and left unchanged thereafter.

`update_method: merge` delivers partial update: only fields present in the incoming
record are written; other stored fields are preserved.

## Configuration (`spec.json`)

| Field           | Type   | Required | Default     | Notes                                                 |
| --------------- | ------ | -------- | ----------- | ----------------------------------------------------- |
| `host`          | string | yes      | —           | Meilisearch URL incl. protocol (e.g. `http://localhost:7700`). |
| `api_key`       | string | no       | —           | `airbyte_secret`. Empty if instance has no key.       |
| `batch_size`    | integer| no       | `1000`      | Records per Meilisearch task. Configurable batching.  |
| `update_method` | enum   | no       | `"replace"` | `replace` → `add_documents`; `merge` → `update_documents`. |

Supported destination sync modes: `overwrite`, `append`, `append_dedup`.

## Components

Small, single-purpose modules following the established Python-destination pattern
(chroma / qdrant / couchbase / elasticsearch):

- **`destination.py`** — `DestinationMeilisearch(Destination)`:
  - `spec` — load `spec.json`.
  - `check` — read/write verification (below).
  - `write` — build client; resolve each stream's index name, primaryKey field, and
    operation; for `overwrite` streams `delete_index` + wait; iterate messages:
    `RECORD` → route to the stream's `MeiliWriter`; `STATE` → flush all writers then
    re-emit the state message (checkpointing); other → log. Final flush at end.
- **`writer.py`** — `MeiliWriter`: owns one stream's buffer, the resolved
  `primary_key` field, the operation (`add` vs `update`), and `batch_size`. Computes
  the per-record id (natural pass-through, synthetic hash, or synthetic UUID), buffers
  records, flushes on threshold, and on flush calls
  `add_documents`/`update_documents(buffer, primary_key=...)`, then `wait_for_task` and
  checks task status.
- **`spec.json`** — configuration schema above.
- **`__init__.py`** — export `DestinationMeilisearch`.
- **`run.py`** / **`main.py`** — entrypoint; fix the current broken import.

## `check` — read AND write verification

1. Create a temporary index by `add_documents([{...}], primary_key="id")` (write).
2. `wait_for_task`; fail if the task failed.
3. Fetch the document back via `get_document` / `get_documents` (read).
4. `delete_index` (cleanup).
5. Return `SUCCEEDED`, or `FAILED` with the exception message on any error.

This confirms the API key has both write and read scope, not merely connectivity.

## Dependencies / metadata

- Rebuild on the current `airbyte-cdk` `Destination` base class.
- Bump the `meilisearch` Python SDK to a current release (exact pin verified at build).
- Fix the `destination-qdrant` → `destination-meilisearch` script name in `pyproject.toml`.
- Un-archive in `metadata.yaml` (`supportLevel`, `registryOverrides`), bump
  `dockerImageTag`.
- Update `docs/integrations/destinations/meilisearch.md`: changelog entry, and feature
  table (`Incremental - Append + Deduped` → Yes).

## Testing

- **Unit tests** (mocked `meilisearch.Client`):
  - id resolution: natural pass-through, deterministic hash for composite/nested,
    random UUID when no key.
  - index-name sanitization.
  - sync-mode → operation mapping (add vs update; delete on overwrite).
  - batch flush boundaries (threshold, state, stream end).
  - `update_method` selects `add_documents` vs `update_documents`.
- **Integration tests** (real Meilisearch via Docker):
  - `check` success and failure.
  - `overwrite`, `append`.
  - `append_dedup` with `replace`.
  - `append_dedup` with `merge` — assert fields absent from the second record survive.

## Open questions

None outstanding.
