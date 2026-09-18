# Contributing to source-uptick

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Overview

`source-uptick` is a manifest-only connector built on `source-declarative-manifest`; all behavior lives in `manifest.yaml` and there is no `components.py`. It exposes 55 streams: 54 read pinned JSON:API endpoints under `/api/v2.15/`, and `task_profitability` reads the intelligence report at `/api/v2/intelligencereports/profitability_by_task/` (a plain `results` array, not JSON:API).

## Authentication

The connector uses the OAuth 2.0 password grant against `{base_url}/api/oauth2/token/`: `client_id`/`client_secret` identify the OAuth application and `username`/`password` identify the Uptick user. Uptick (Django OAuth Toolkit) also exposes `{base_url}/api/oauth2/authorize/` for the authorization-code flow and returns rotating refresh tokens, but the connector currently implements only the password grant. OAuth applications are registered per tenant under **Control Panel > Uptick API** and every customer runs on their own host (`<tenant>.onuptick.com`), so Airbyte cannot ship a single shared Cloud OAuth app; a Cloud button would have to build the consent URL from the user's `base_url` (tracked separately in https://github.com/airbytehq/airbyte/pull/86464).

HTTP 401 fails fast as a `config_error` rather than refresh-and-retry — the authenticator already refreshes on `expires_in`, so a 401 means the credentials themselves are wrong. HTTP 403 is also a `config_error` (the user lacks permission for that endpoint).

## Config normalization

`base_url` is normalized in memory by a `ConfigAddFields` transformation: it is trimmed, the scheme and any path are stripped, and it is prefixed with `https://`. The stored config is not rewritten. `metadata.yaml` sets `allowedHosts: ${base_url}`; the platform strips the scheme itself.

## Streams and pagination

All streams paginate by following the `links.next` URL via `CursorPagination` with a `RequestPath` page token. Each of the 54 JSON:API streams requests a curated sparse fieldset (`fields[<Type>]`) and orders by `ordering: -updated`; `AddFields` transformations flatten the JSON:API `attributes` object into top-level columns and each to-one `relationships` entry into a scalar `<relationship>_id` column; to-many relationships such as `tags` and `supporting_technicians` stay arrays. `task_profitability` sends no sparse fieldset or ordering (only the `updatedsince` cursor parameter), extracts `results`, and emits the report rows as-is.

## Incremental sync

Every stream defines a `DatetimeBasedCursor` on `updated` (`%Y-%m-%dT%H:%M:%S.%f%z`) with a `2000-01-01` start date, filtering with the `updatedsince` query parameter.

## Deletions

All 54 JSON:API streams pass `show_deleted: "true"`, so Uptick includes deleted records in the response. Only the 12 streams that also request the `deleted` field in their sparse fieldset can surface deletions — they expose a `deleted` timestamp column (`tasks`, `assets`, `creditnotes`, `creditnotelineitems`, `remarks`, `assettypes`, `assettypevariants`, `products`, `rounds`, `servicetasks`, `subtasks`, `promptquestions`). On all other streams deletes are not detectable, so deleted rows persist in the destination until a full refresh. `task_profitability` is a generated report and has no deleted state.

## Rate limiting

`api_budget` is a global `HTTPAPIBudget` of 60 requests/minute (`MovingWindowCallRatePolicy`). This is a conservative placeholder — Uptick's published limit is not yet confirmed with the vendor, so treat it as a provisional ceiling, not a measured value. The error handler honors `Retry-After` capped at 1800s per wait, retries up to 5 times, and `maxSecondsBetweenMessages` is 3600.

## Permissions

`task_profitability` requires the Intelligence reports permission on the Uptick user account; `billingcontractlineitems` has also been observed failing with 403 in production.

## Local development

From the connector directory:

```bash
poe fetch-secrets                 # pull SECRET_SOURCE-UPTICK__CREDS into secrets/
poe test-integration-tests        # run the connector integration test suite
airbyte-cdk image build . --tag dev  # build the connector image locally
cd unit_tests && poetry install && poetry run pytest  # manifest unit tests
```
