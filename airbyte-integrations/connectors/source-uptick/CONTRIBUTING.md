# Contributing to source-uptick

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Overview

`source-uptick` is a manifest-only connector built on `source-declarative-manifest`; all behavior lives in `manifest.yaml` and there is no `components.py`. It exposes 55 streams: 54 read pinned JSON:API endpoints under `/api/v2.16/`, and `task_profitability` reads the intelligence report at `/api/v2/intelligencereports/profitability_by_task/` (a plain `results` array, not JSON:API).

## Authentication

A `SelectiveAuthenticator` on `credentials.auth_type` picks one of two `OAuthAuthenticator` definitions:

- `password` (`password_authenticator`): the OAuth 2.0 password grant against `{base_url}/api/oauth2/token/`. `client_id`/`client_secret` identify an OAuth application registered per tenant under **Control Panel > Uptick API**, and `username`/`password` identify the Uptick user. The [sample Postman collection](https://support.uptickhq.com/en/articles/6728183-uptick-api-sample-postman-collection) documents this grant and the refresh-token grant; the [Getting started](https://support.uptickhq.com/en/articles/6728442-uptick-api-getting-started) article covers only creating the application.
- `oauth2.0` (`oauth_authenticator`): the refresh-token grant against the derived `oauth_token_url` (see [OAuth host pinning](#oauth-host-pinning)) with a `refresh_token_updater` that writes the rotated `access_token`, `refresh_token`, and `token_expiry_date` back under `credentials` through a `CONNECTOR_CONFIG` control message. The tokens come from the authorization-code flow with PKCE (S256) declared in `spec.advanced_auth`: on Airbyte Cloud the **Authenticate with Uptick** button uses Airbyte's shared Uptick app (instance-wide OAuth params supply `client_id`/`client_secret`), and the consent URL requests only the read-only `read` scope. Every tenant has its own host (`<workspace>.onuptick.com`), so the consent and token URLs are built from the user's `base_url`, which the `advanced_auth` input pattern restricts to `^https://[a-z0-9-]+\.onuptick\.com/?$`.

Bad credentials surface on the token endpoint (`invalid_grant` for a wrong username/password or a rejected refresh token, `invalid_client` for a wrong client secret) and fail the token request itself as a `config_error` via the authenticator's `refresh_token_error_*` settings, before any stream request is issued. A 401 on a stream request (expired or revoked access token — Uptick returns the same body in every case) is handled with `REFRESH_TOKEN_THEN_RETRY`: the connector refreshes the token once and retries the request; a rejected refresh fails the sync with the authenticator's `config_error` (`Refresh token was rejected by the OAuth provider … Provider error: invalid_grant`), and a second 401 after the retry fails it with the CDK's `Refreshed OAuth access token is rejected by the API.` — the filter's `error_message` (`HTTP 401: Uptick rejected the access token.`) is recorded only in the internal message. The CDK bounds this to a single refresh per request (airbyte-python-cdk#1173, shipped in 7.30.1), so a rotated password causes at most one failed login per stream (55 per sync with every stream selected) instead of a retry loop. HTTP 403 is also a `config_error` (the user lacks permission for that endpoint).

### OAuth host pinning

`oauth_authenticator` does not build its `token_refresh_endpoint` from `base_url` directly. `config_normalization_rules` derives `oauth_token_url` at runtime: when `base_url` matches `^(https://[a-z0-9-]+\.onuptick\.com)/?$`, it is `<match>/api/oauth2/token/`; otherwise it is the sentinel `unsupported-oauth-host://base_url-must-be-https-workspace.onuptick.com`, which `requests` rejects before opening a socket, so `check` fails with the hint and the shared `client_secret` plus the user's refresh token never reach a foreign host. A companion step clears `credentials.token_expiry_date` on the same mismatch, so a still-valid stored access token is never sent as a Bearer either. The password authenticator reads `base_url` directly. However, `check` rejects a Base URL that does not normalize to `https://<workspace>.onuptick.com` before any request, using a `DpathValidator` on the derived `base_url_json` field. The field is double-JSON-encoded because `ValidateAdheresToSchema` runs `json.loads` on string values and interpolation strips one level of quoting. A typo such as `https://typo.onuptick.com` matches the pattern but still fails with a DNS error. Like `oauth_token_url`, `base_url_json` can be stored through a refresh `CONNECTOR_CONFIG` control message; both fields are recomputed and overwritten on the next run. Normalization always rewrites `base_url` to `https://<host>`, so plain-HTTP hosts are not reachable.

### Legacy config migration

`config_migrations` copies the pre-2.1.0 top-level `client_id`, `client_secret`, `username`, and `password` under `credentials` with `auth_type: password` when `username` is present and `credentials.auth_type` is not. It is copy-only: the top-level fields are kept (hidden in the spec; `client_id`, `client_secret`, and `password` stay `airbyte_secret`) so a config still validates on 2.0.x after a rollback. Values are copied as `string` to avoid Jinja literal-evaluating numeric passwords. The migrated config is emitted as a control message; a config that already has `credentials.auth_type` is left untouched.

A second migration removes legacy top-level fields that the connector no longer reads. It always removes `start_date` and `end_date`. It removes `oauth_access_token`, `oauth_token_expiry_date` and `client_refresh_token` only when `credentials.auth_type` is `password` or `oauth2.0`, so they are kept until the credentials migration has run. Migrations run in list order on the same config.

## Config normalization

`config_normalization_rules` runs five `ConfigAddFields` steps in memory at the start of each sync. The first normalizes `base_url`: it is trimmed, the scheme and any path are stripped, and it is prefixed with `https://`. The next two derive `oauth_token_url`, the fourth clears the OAuth expiry on a host mismatch, and the fifth derives `base_url_json`, as described under [OAuth host pinning](#oauth-host-pinning). The CDK does not persist these fields directly, but a successful OAuth refresh can emit the transformed config in its `CONNECTOR_CONFIG` control message. The fields are recomputed and overwritten on the next run. `metadata.yaml` sets `allowedHosts: ${base_url}`; the platform strips the scheme itself.

## Streams and pagination

All streams use `CursorPagination` with a `RequestPath` page token. Uptick documents limit-offset pagination as the default. On v2.16 the mode it serves depends on the client: in the test tenant, a generic `User-Agent` gets limit-offset (50 rows, `page[size]` ignored), while the connector's `User-Agent: Airbyte` already got cursor mode (observed 2026-10-21). To select Uptick's documented cursor mode regardless of that heuristic, each JSON:API request path carries the bare `?page[cursor]` flag because the CDK drops empty-valued request parameters and Uptick rejects non-empty initial cursor values. Each request also sends `page[size]=1000`, and subsequent pages follow `links.next`. Each of the 54 JSON:API streams requests a curated sparse fieldset (`fields[<Type>]`); 53 order by `ordering: -updated`, and `majorservices` orders by `id`. Requests use `page[size]=1000` as a deliberate choice to balance response size and request time with wide sparse fieldsets. Uptick recommends pinning a minor version (hence `v2.16`, since 2.0.0) and announces deprecations in its [API overview and patch notes](https://support.uptickhq.com/en/articles/6728314-uptick-api-overview-and-patch-notes). The declared JSON:API schemas include nullable `attributes` and `relationships` objects, which remain in emitted records. Uptick returns `""` for unset email and URL fields, so the schemas do not declare `format: email` or `format: uri`. The nullable resource `type` field is also declared on each stream that retains it. A `DpathFlattenFields` transformation copies every key of the JSON:API `attributes` object to the top level of the record without re-rendering the value; `AddFields` builds a scalar `<relationship>_id` column from each to-one `relationships` entry, and to-many relationships such as `tags` and `supporting_technicians` stay arrays. Five streams also drop the JSON:API `type` key with `RemoveFields`. Before 1.2.0, attributes were flattened with `AddFields` templates, which turned `"10.00"` into `"10.0"` and `null` into `"None"`; don't reintroduce that pattern. `task_profitability` sends no sparse fieldset or ordering (only the `updatedsince` cursor parameter), extracts `results`, and emits the report rows as-is.

### Vendor documentation

Each Uptick tenant exposes OpenAPI at `https://<workspace>.onuptick.com/api/openapi.json`. It covers roughly 30 of the connector's 55 stream paths, but does not include GET list-response schemas; `OPTIONS` requests provide metadata per endpoint.

## Incremental sync

Every stream except `majorservices` defines a `DatetimeBasedCursor` on `updated` (`%Y-%m-%dT%H:%M:%S.%f%z`) with a `2000-01-01` start date, filtering with the `updatedsince` query parameter. `majorservices` has no `updated` timestamp and is full refresh only since 2.0.0. Before 2.0.0, `servicegroups` and `accreditationtypes` ignored `updatedsince` and were filtered client-side (`is_client_side_incremental`); Uptick now applies the filter on those endpoints, and the client-side filter was removed in 2.0.0.

## Deletions

All 54 JSON:API streams pass `show_deleted: "true"`, but it only has an effect on Uptick's soft-delete resources: the 12 streams that also request the `deleted` field in their sparse fieldset, which expose a `deleted` timestamp column (`tasks`, `assets`, `creditnotes`, `creditnotelineitems`, `remarks`, `assettypes`, `assettypevariants`, `products`, `rounds`, `servicetasks`, `subtasks`, `promptquestions`). The other endpoints hard-delete and expose no `deleted` field (checked on a live tenant; Uptick's docs don't cover this), so deleted rows persist in the destination until a full refresh. `task_profitability` is a generated report and has no deleted state.

## Rate limiting

`api_budget` is a global `HTTPAPIBudget` (`MovingWindowCallRatePolicy`) whose limit comes from the `max_requests_per_minute` config field (default 60, range 1–600). Uptick publishes no numeric limit, so the default is a provisional ceiling chosen by Airbyte, not a measured value (vendor confirmation is an open item on the certification epic, airbyte-internal-issues#17263). The error handler honors `Retry-After` up to `max_waiting_time_in_seconds: 1800`; a header asking for 1800s or more fails the stream with a rate-limit error instead of waiting. Without the header it backs off exponentially, retries up to 5 times, and `maxSecondsBetweenMessages` is 3600.

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
