# Contributing to source-uptick

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Overview

`source-uptick` is a manifest-only connector built on `source-declarative-manifest`; all behavior lives in `manifest.yaml` and there is no `components.py`. It exposes 55 streams: 54 read pinned JSON:API endpoints under `/api/v2.16/`, and `task_profitability` reads the intelligence report at `/api/v2/intelligencereports/profitability_by_task/` (a plain `results` array, not JSON:API).

## Authentication

A `SelectiveAuthenticator` on `credentials.auth_type` picks one of two `OAuthAuthenticator` definitions, both against `{base_url}/api/oauth2/token/`:

- `password` (`password_authenticator`): the OAuth 2.0 password grant. `client_id`/`client_secret` identify an OAuth application registered per tenant under **Control Panel > Uptick API**, and `username`/`password` identify the Uptick user. The [sample Postman collection](https://support.uptickhq.com/en/articles/6728183-uptick-api-sample-postman-collection) documents this grant and the refresh-token grant; the [Getting started](https://support.uptickhq.com/en/articles/6728442-uptick-api-getting-started) article covers only creating the application.
- `oauth2.0` (`oauth_authenticator`): the refresh-token grant with a `refresh_token_updater` that writes the rotated `access_token`, `refresh_token`, and `token_expiry_date` back under `credentials` through a `CONNECTOR_CONFIG` control message. The tokens come from the authorization-code flow with PKCE (S256) declared in `spec.advanced_auth`: on Airbyte Cloud the **Authenticate with Uptick** button uses Airbyte's shared Uptick app (instance-wide OAuth params supply `client_id`/`client_secret`), and the consent URL requests only the read-only `read` scope. Every tenant has its own host (`<workspace>.onuptick.com`), so the consent and token URLs are built from the user's `base_url`, which the `advanced_auth` input pattern restricts to `^https://[a-z0-9-]+\.onuptick\.com/?$`.

Bad credentials surface on the token endpoint (`invalid_grant` for a wrong username/password or a rejected refresh token, `invalid_client` for a wrong client secret) and fail the token request itself as a `config_error` via the authenticator's `refresh_token_error_*` settings, before any stream request is issued. A 401 on a stream request (expired or revoked access token — Uptick returns the same body in every case) is handled with `REFRESH_TOKEN_THEN_RETRY`: the connector refreshes the token once and retries the request; a rejected refresh or a second 401 after the retry fails the sync as a `config_error` (`HTTP 401: Uptick rejected the access token.`). The CDK bounds this to a single refresh per request (airbyte-python-cdk#1173, shipped in 7.30.1), so a rotated password causes at most one failed login per stream and cannot trigger Uptick's account lockout. HTTP 403 is also a `config_error` (the user lacks permission for that endpoint).

### OAuth host pinning

`oauth_authenticator` does not build its `token_refresh_endpoint` from `base_url` directly. `config_normalization_rules` derives `oauth_token_url` at runtime: when `base_url` matches `^(https://[a-z0-9-]+\.onuptick\.com)/?$`, it is `<match>/api/oauth2/token/`; otherwise it is the sentinel `unsupported-oauth-host://base_url-must-be-https-workspace.onuptick.com`, which `requests` rejects before opening a socket, so `check` fails with the hint and the shared `client_secret` plus the user's refresh token never reach a foreign host. A companion step clears `credentials.token_expiry_date` on the same mismatch, so a still-valid stored access token is never sent as a Bearer either. The field is recomputed on every run and is not written to the stored config (a successful refresh may persist it in the control message; the next run overwrites it). The password authenticator reads `base_url` directly and keeps working with self-hosted or `http://` test hosts.

### Legacy config migration

`config_migrations` copies the pre-2.1.0 top-level `client_id`, `client_secret`, `username`, and `password` under `credentials` with `auth_type: password` when `username` is present and `credentials.auth_type` is not. It is copy-only: the top-level fields are kept (hidden and `airbyte_secret` in the spec) so a config still validates on 2.0.x after a rollback. Values are copied as `string` to avoid Jinja literal-evaluating numeric passwords. The migrated config is emitted as a control message; a config that already has `credentials.auth_type` is left untouched.

## Config normalization

`config_normalization_rules` runs four `ConfigAddFields` steps in memory on every run; none of them is persisted. The first normalizes `base_url`: it is trimmed, the scheme and any path are stripped, and it is prefixed with `https://`. The other three derive `oauth_token_url` and clear the OAuth expiry on a host mismatch, as described under [OAuth host pinning](#oauth-host-pinning). `metadata.yaml` sets `allowedHosts: ${base_url}`; the platform strips the scheme itself.

## Streams and pagination

All streams paginate by following the `links.next` URL via `CursorPagination` with a `RequestPath` page token. Uptick's [API overview](https://support.uptickhq.com/en/articles/6728314-uptick-api-overview-and-patch-notes) recommends its cursor pagination mode (`page[cursor]`/`page[size]`) for data syncs; the connector instead follows whatever `links.next` the default (limit/offset) mode returns. Switching to cursor mode would be a behavior change. Uptick recommends pinning a minor version (hence `v2.16`, since 2.0.0) and announces deprecations in the same article. Each of the 54 JSON:API streams requests a curated sparse fieldset (`fields[<Type>]`) and orders by `ordering: -updated`. A `DpathFlattenFields` transformation copies every key of the JSON:API `attributes` object to the top level of the record without re-rendering the value and keeps the original `attributes` object; `AddFields` builds a scalar `<relationship>_id` column from each to-one `relationships` entry, and to-many relationships such as `tags` and `supporting_technicians` stay arrays. Five streams also drop the JSON:API `type` key with `RemoveFields`. Before 1.2.0, attributes were flattened with `AddFields` templates, which turned `"10.00"` into `10.0` and `null` into `"None"`; don't reintroduce that pattern. `task_profitability` sends no sparse fieldset or ordering (only the `updatedsince` cursor parameter), extracts `results`, and emits the report rows as-is.

## Incremental sync

Every stream except `majorservices` defines a `DatetimeBasedCursor` on `updated` (`%Y-%m-%dT%H:%M:%S.%f%z`) with a `2000-01-01` start date, filtering with the `updatedsince` query parameter. `majorservices` has no `updated` timestamp and is full refresh only since 2.0.0. Before 2.0.0, `servicegroups` and `accreditationtypes` ignored `updatedsince` and were filtered client-side (`is_client_side_incremental`); Uptick now applies the filter on those endpoints, and the client-side filter was removed in 2.0.0.

## Deletions

All 54 JSON:API streams pass `show_deleted: "true"`, but it only has an effect on Uptick's soft-delete resources: the 12 streams that also request the `deleted` field in their sparse fieldset, which expose a `deleted` timestamp column (`tasks`, `assets`, `creditnotes`, `creditnotelineitems`, `remarks`, `assettypes`, `assettypevariants`, `products`, `rounds`, `servicetasks`, `subtasks`, `promptquestions`). The other endpoints hard-delete and expose no `deleted` field (checked on a live tenant; Uptick's docs don't cover this), so deleted rows persist in the destination until a full refresh. `task_profitability` is a generated report and has no deleted state.

## Rate limiting

`api_budget` is a global `HTTPAPIBudget` (`MovingWindowCallRatePolicy`) whose limit comes from the `max_requests_per_minute` config field (default 60, range 1–600). Uptick publishes no numeric limit, so the default is a provisional ceiling chosen by Airbyte, not a measured value (vendor confirmation is tracked in airbyte-internal-issues#17268). The error handler honors `Retry-After` up to `max_waiting_time_in_seconds: 1800`; a header asking for 1800s or more fails the stream with a rate-limit error instead of waiting. Without the header it backs off exponentially, retries up to 5 times, and `maxSecondsBetweenMessages` is 3600.

## Permissions

Uptick doesn't publish a per-endpoint permission list. In production, `task_profitability` has returned 403 until the Uptick user was granted the Intelligence reports permission, and `billingcontractlineitems` has also been observed failing with 403.

## Local development

From the connector directory:

```bash
poe fetch-secrets                 # pull SECRET_SOURCE-UPTICK__CREDS into secrets/
poe test-integration-tests        # run the connector integration test suite
airbyte-cdk image build . --tag dev  # build the connector image locally
cd unit_tests && poetry install && poetry run pytest  # manifest unit tests
```
