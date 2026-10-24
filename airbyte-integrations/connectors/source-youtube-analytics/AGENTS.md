> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-youtube-analytics: Unique Connector Behaviors

## 1. Three-Level Job → Report → CSV Download Model

Each report stream starts by listing jobs through the YouTube Reporting API's `/v1/jobs` endpoint. `JobRequester` filters the response to the job whose `reportTypeId` matches that stream. If none exists, it creates a reporting job named `Airbyte reporting job` and lists jobs again. This means a source read can write to YouTube by creating a job.

The `report` stream lists files from `/jobs/{id}/reports` for each matching job. Each report stream then downloads the listed file using its `downloadUrl`. `CustomDecoder` uses `csv.DictReader`, so CSV values arrive as strings; the only type conversion in the stream definitions casts `date` to an integer. The schemas declare numeric and integer fields, so schema-validation noise is expected until type coercion is implemented. Type coercion is planned, with no version commitment.

The `jobs` and `report` streams do not currently follow YouTube's `nextPageToken`, even though the API can return one. The `report_types` stream does paginate, but that does not paginate either report-listing stream.

**Why this matters:** The first read of a report stream can create a YouTube job, and data rows come from downloaded CSV files rather than the job or report listing responses. Do not assume all declared numeric fields have already been converted to numbers, or that listings include every page.

## 2. Incremental Cursor Lives on the Parent `report` Stream

The parent `report` stream tracks `createTime` and sends it to YouTube as `createdAfter`. Its global substream cursor and the child streams' incremental dependency let each report stream download only files created since the prior sync. Child report streams retain their own `date` cursor in `%Y%m%d` format; `date` is a CSV column and part of each child's primary key.

YouTube can re-issue a report with corrected data for an earlier day. That file has a newer `createTime` even though its data `date` is unchanged, so the parent cursor picks up the correction and the child primary key identifies its original day. The optional `testing_period` setting is not part of the source spec; when supplied, it narrows the parent's start time for tests.

**Why this matters:** Moving the parent cursor to a report's data date would miss corrected files for days already synced. Keep the parent `createTime` cursor separate from each child's `date` cursor.

## 3. Shared Quota and Per-Stream Request Fan-Out

The source applies a moving-window budget of 60 requests per minute to all API requests. Each selected report stream independently lists jobs, may create a job if none matches, lists reports for that job, and downloads each report file. Selecting more report streams therefore increases both API calls and downloaded files.

On Airbyte Cloud, the YouTube API quota belongs to Airbyte's Google Cloud project and is shared across Cloud connections. On Open Source, requests use the quota of the user's Google Cloud project. A response identifying `FreeQuotaRequestsPerDayPerProject` is treated as daily quota exhaustion: the source fails with `Daily YouTube API project quota is exhausted.` as a `transient_error` without an immediate request retry. Other 429 responses are marked `RATE_LIMITED` and retried after a constant 30-second backoff. Responses whose JSON `error.code` is in the 5xx range are retried.

**Why this matters:** A daily quota failure on Cloud may be caused by another connection sharing Airbyte's project, and adding report streams increases the quota consumed by each sync.

## 4. Error Mapping Depends on the Response Path

A 401 from the YouTube Reporting API occurs after the OAuth refresh request succeeded, so it is not a refresh-token failure. The 401 filter has `action: FAIL` and `failure_type: config_error`; its message explains that the authorized account needs to own or manage a YouTube channel. The `action` is required for the filter to be applied. An invalid or revoked refresh token fails earlier at `oauth2.googleapis.com/token`, before the Reporting API error handler runs.

The 403 filter declares an error message but has no `action`, so the CDK skips that filter. A throwaway `requests_mock` test against `reportTypes` returned `failure_type=config_error` with the generic message `HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource.` The 403 response's own message does not become the user-facing message.

For any successful HTTP response whose JSON body contains an `error` key, `JobRequester` raises `YouTube Reporting API Error (code …): …` as a `config_error`. This is separate from the HTTP response filters.

**Why this matters:** A 401, 403, refresh-token failure, and an API error in a successful response produce different messages and failure paths; changing a filter's `action` or request stage can change what users see.

## 5. Content Owner Parameter and Static Extra Request Parameters

`ContentOwnerRequester` adds `onBehalfOfContentOwner` only when `content_owner_id` is set. It also merges the manifest's `extra_request_parameters` as static values; these values are not interpolated.

The custom component deliberately calls this field `extra_request_parameters`, not `request_parameters`. The `report` stream uses `request_parameters` for a Jinja-templated `startTimeAtOrAfter` value, which the CDK interpolates. If the custom field were named `request_parameters`, the factory would pass that template to the component and it would be sent literally to YouTube.

**Why this matters:** Keep content-owner context conditional and extra parameters static. Renaming the custom field can cause every report request to send an uninterpolated template.

## 6. Two Chained State Migrations

The migrations in the manifest run in order. `ReportsStateMigration` converts pre-1.1.0 Python state such as `{"date": 20251107}` into the low-code shape, keeping the child's `date` cursor and seeding `parent_state.report.state.date`. `ReportsCreateTimeStateMigration` then changes the parent's `date` cursor to `createTime` in the global cursor (`state`) and in every per-partition cursor (`states[].cursor`). If the parent has no cursor, it seeds one from the child cursor.

The new parent value can only move the cursor backward relative to the file's actual `createTime`: the old value represents a data day or earlier timestamp, while the report file is generated later. That can cause a one-time re-listing, but cannot skip a report. Unparseable legacy values such as `99999999` in `integration_tests/abnormal_state.json` are dropped from the parent cursor, so the stream falls back to its configured start time. The migration tests are in `unit_tests/test_state_migration.py`; end-to-end cursor and correction coverage is in `unit_tests/mock_server/test_incremental_reports.py`.

**Why this matters:** The migration order preserves both old state formats and per-partition cursors while moving incremental tracking to report creation time. Reordering or changing the conversions can cause unnecessary re-reads or make the source skip corrected report files.
