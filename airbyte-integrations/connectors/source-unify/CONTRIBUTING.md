# Contributing to source-unify

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

This connector syncs data out of [Unify](https://unifygtm.com) using its
asynchronous [Bulk API](https://docs.unifygtm.com/developers/guides/request-data/bulk-api).
It is a manifest-only connector — all logic lives in `manifest.yaml` and runs on
the `source-declarative-manifest` base image.

## Async Bulk API lifecycle

Every Bulk stream is modeled with the CDK's [`AsyncRetriever`](https://docs.airbyte.com/connector-development/connector-builder-ui/async-streams),
whose three requesters map directly to the three Bulk API calls:

| Requester            | Call                                                | Purpose         |
| -------------------- | --------------------------------------------------- | --------------- |
| `creation_requester` | `POST {resource}/query-jobs`                        | Create the job  |
| `polling_requester`  | `GET {resource}/query-jobs/{job_id}`                | Poll the status |
| `download_requester` | `GET {resource}/query-jobs/{job_id}/results`        | Page the rows   |

`status_mapping` maps Unify's job statuses onto the CDK's `running` / `completed`
/ `failed` buckets. Unify has no timed-out status, so `timeout` is intentionally
empty and `polling_job_timeout` (config `poll_timeout_minutes`) is the only
timeout path. The download target is the `job_id` itself — Unify returns no
download URL.

## `$ref` is a shallow merge

The CDK's `$ref` does a shallow merge (it does not deep-merge nested mappings),
so each stream spells out its own full `request_body_json` rather than layering
onto a partial. Object resources (`company`, `person`, `opportunity`) post a
`query` with `select`/`sort_by`/`metadata`; `event` and the sequence streams
post a `filter`. When adding a stream, copy an existing one of the matching
shape rather than trying to compose partial bodies.

## Connection check

`check` uses the synchronous `object_definitions` stream — a single
`GET /data/v1/objects` (a `SimpleRetriever`, not a Bulk job). This validates the
API key with one cheap request instead of creating, polling, and downloading a
Bulk job just to test credentials. A bad key surfaces here as a `401`.
`CheckStream` requires the stream to be registered, so `object_definitions` also
appears in the catalog as a small full-refresh stream.

## Rate limits and concurrency

- Job creation is rate-limited (~100/day). Incremental cursors keep each job
  focused. `429`/`5xx` responses are retried (`max_retries: 5`); the
  `WaitTimeFromHeader` backoff strategy honors the API's `Retry-After` header on
  `429`s instead of falling back to exponential backoff.
- `concurrency_level` syncs up to `num_workers` streams in parallel (default
  `2`, ceiling `6` — one per stream), and `max_concurrent_async_job_count: 1`
  caps in-flight Bulk jobs per stream. Each parallel stream creates another job,
  so keep `num_workers` modest to stay under the job-creation rate limit.
- Jobs and their results expire 24h after creation; each sync downloads results
  immediately after the job finishes.

## Result format

The connector uses JSON paging (a stable, page-based envelope
`{total, page, page_size, data}`). For very large pages the API also supports
NDJSON (`Accept: application/x-ndjson`, up to `page_size=10000`) — switch the
`download_requester`'s `Accept` header and decoder to adopt it.
