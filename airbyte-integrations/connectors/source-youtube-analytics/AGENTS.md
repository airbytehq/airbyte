> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-youtube-analytics: Unique Connector Behaviors

## 1. Three-Level Job → Report → CSV Download Model

Each report stream starts by listing jobs through the YouTube Reporting API's `/v1/jobs` endpoint. `JobRequester` filters the response to the job whose `reportTypeId` matches that stream. If none exists, it creates a reporting job named `Airbyte reporting job` and lists jobs again. This means a source read can write to YouTube by creating a job.

The `report` stream lists files from `/jobs/{id}/reports` for each matching job. Each report stream then downloads the listed file using its `downloadUrl`. `CustomDecoder` uses `csv.DictReader`, so CSV values arrive as strings. The report streams' record selector sets `schema_normalization: Default`, which casts each value to the type its schema declares; a value that cannot be cast, such as an empty cell in an integer column, stays a string. An `AddFields` transformation also casts `date` to an integer.

The `jobs`, `report`, and `report_types` streams follow YouTube's `nextPageToken` through `next_page_token_paginator`. On the first page, `JobRequester._job_exists` checks for a matching job and keeps reading pages until it finds one or runs out, so a match on a later page does not create a duplicate job. If no page matches, it creates the job and lists the first page again. Either way, the paginator then requests the later pages again, so the later listing pages are requested twice whenever the match is not on the first page or no page matches.

Only report downloads handle a 404. The download requester puts an `action: IGNORE` filter for 404 ahead of the shared error handler, so a report file YouTube has already removed (most likely after its retention period) is skipped with a log message and the rest of the sync continues. That file's rows are not synced, and a later sync cannot recover them. A 404 on a listing endpoint still fails the sync.

**Why this matters:** The first read of a report stream can create a YouTube job, and data rows come from downloaded CSV files rather than the job or report listing responses. Emitted value types follow the stream schemas, so changing a schema type changes what destinations receive. A missing report file is skipped rather than failing the sync, so a sync can succeed with rows missing.

## 2. Incremental Cursor Lives on the Parent `report` Stream

The parent `report` stream tracks `createTime` and sends it to YouTube as `createdAfter`. Its global substream cursor and the child streams' incremental dependency let each report stream download only files created since the prior sync. Child report streams retain their own `date` cursor in `%Y%m%d` format; `date` is a CSV column and part of each child's primary key.

YouTube can re-issue a report with corrected data for an earlier day. That file has a newer `createTime` even though its data `date` is unchanged, so the parent cursor picks up the correction and the child primary key identifies its original day. The optional `testing_period` setting is not part of the source spec; when supplied, it narrows the parent's start time for tests.

**Why this matters:** Moving the parent cursor to a report's data date would miss corrected files for days already synced. Keep the parent `createTime` cursor separate from each child's `date` cursor.

## 3. Shared Quota and Per-Stream Request Fan-Out

The source applies a moving-window budget of 60 requests per minute to all API requests. Each selected report stream independently lists jobs, may create a job if none matches, lists reports for that job, and downloads each report file. Selecting more report streams therefore increases both API calls and downloaded files.

Report files download in parallel. `concurrency_level` reads the optional `num_workers` setting (default 2, maximum 4). All workers share the same 60-requests-per-minute budget, so more workers reach that budget and YouTube's own limits sooner without raising either one.

On Airbyte Cloud, the YouTube API quota belongs to Airbyte's Google Cloud project and is shared across Cloud connections. On Open Source, requests use the quota of the user's Google Cloud project. A response identifying `FreeQuotaRequestsPerDayPerProject` is treated as daily quota exhaustion: the source fails with `Daily YouTube API project quota is exhausted.` as a `transient_error` without an immediate request retry. Other 429 responses are marked `RATE_LIMITED` and retried after a constant 30-second backoff. The `api_budget` also lists 429 under `status_codes_for_ratelimit_hit`, so on the current CDK a 429 fills the shared 60-requests-per-minute window too. The retry then waits for the 30-second backoff and for that window to clear, about a minute in total, and every stream pauses, not only the one that got the 429. Unit tests pinned to an older CDK (7.23.8 in `unit_tests/poetry.lock`) only show the 30-second wait. Retries stop after the default `max_retries` (5) and `max_time` (600 seconds). Responses whose JSON `error.code` is in the 5xx range are retried.

**Why this matters:** A daily quota failure on Cloud may be caused by another connection sharing Airbyte's project, and adding report streams increases the quota consumed by each sync.

## 4. Error Mapping Depends on the Response Path

A 401 from the YouTube Reporting API occurs after the OAuth refresh request succeeded, so it is not a refresh-token failure. Two 401 filters apply, both with `action: FAIL` and `failure_type: config_error`, and the first match wins:

- If the JSON `error.code` is 401 and the message contains `invalid authentication credentials`, the user sees `Google rejected the YouTube Reporting API credentials: <vendor message>` and is told to re-authenticate. This filter checks the code inside its `predicate` and sets no `http_codes`, because a filter matches on `http_codes` or `predicate`, not both.
- Any other 401 gets the no-channel message: the authorized account needs to own or manage a YouTube channel.

Every filter needs an `action` to apply. Without one, the CDK skips the filter and shows its generic text instead of `error_message`.

A 403 has `action: FAIL`, `failure_type: config_error`, and the message `The YouTube Reporting API denied access: <vendor message>.` When the body has no JSON message, the message falls back to `see the YouTube Reporting API error`. Vendor messages are truncated to 300 characters in both the 401 and 403 messages. `unit_tests/test_foundations.py` covers both 403 cases.

An invalid or revoked refresh token fails earlier at `oauth2.googleapis.com/token`, before the Reporting API error handler runs. The authenticator's `refresh_token_error_*` settings map a 400 with `error: invalid_grant` to a config error containing `Refresh token is invalid or expired` (`test_expired_refresh_token_tells_the_user_to_re_authenticate`).

For any successful HTTP response whose JSON body contains an `error` key, `JobRequester` raises `YouTube Reporting API Error (code …): …` as a `config_error`. This is separate from the HTTP response filters.

**Why this matters:** Rejected credentials, a missing channel, a 403, a refresh-token failure, a skipped 404 download, and an API error in a successful response each produce a different message and failure path. Changing a filter's order, `action`, or request stage can change what users see.

## 5. Content Owner Parameter and Static Extra Request Parameters

`ContentOwnerRequester` adds `onBehalfOfContentOwner` only when `content_owner_id` is set. It also merges the manifest's `extra_request_parameters` as static values; these values are not interpolated.

Do not rename `extra_request_parameters` to `request_parameters`. The factory forwards manifest keys that match a component's type hints, so a `request_parameters` field on this class would also receive any Jinja-templated `request_parameters` a stream declares later. `ContentOwnerRequester` merges values verbatim without interpolation, so such a template would reach YouTube as literal `{{ ... }}` text. No stream sets `request_parameters` today; the `report` stream sends `createdAfter` through its incremental `start_time_option`.

**Why this matters:** Keep content-owner context conditional and extra parameters static. Renaming the custom field would make any future templated request parameter reach the API uninterpolated.

## 6. Two Chained State Migrations

The migrations in the manifest run in order. `ReportsStateMigration` converts pre-1.1.0 Python state such as `{"date": 20251107}` into the low-code shape, keeping the child's `date` cursor and seeding `parent_state.report.state.date`. `ReportsCreateTimeStateMigration` then changes the parent's `date` cursor to `createTime` in the global cursor (`state`) and in every per-partition cursor (`states[].cursor`). If the parent has no cursor, it seeds one from the child cursor.

The new parent value can only move the cursor backward relative to the file's actual `createTime`: the old value represents a data day or earlier timestamp, while the report file is generated later. That can cause a one-time re-listing, but cannot skip a report. Legacy values that cannot be parsed, such as `99999999` in `unit_tests/test_state_migration.py`, are dropped from the parent cursor, so the stream falls back to its configured start time. `integration_tests/abnormal_state.json` uses the parseable future date `20991231`, which migrates to a 2099 `createTime` so the future-state acceptance test reads no records. The migration tests are in `unit_tests/test_state_migration.py`; end-to-end cursor and correction coverage is in `unit_tests/mock_server/test_incremental_reports.py`.

**Why this matters:** The migration order preserves both old state formats and per-partition cursors while moving incremental tracking to report creation time. Reordering or changing the conversions can cause unnecessary re-reads or make the source skip corrected report files.
