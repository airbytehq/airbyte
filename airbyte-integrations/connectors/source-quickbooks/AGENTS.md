> NOTE: CLAUDE.md and CONTRIBUTING.md are symlinks to AGENTS.md; update AGENTS.md (not the symlinks) when changing these instructions.

# Contributing to source-quickbooks

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication

QuickBooks Online uses three-legged OAuth 2.0 against Intuit's identity service: the consent flow at `https://appcenter.intuit.com/connect/oauth2` returns an authorization code plus the `realmId` of the company the user selected, and the code is exchanged at `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer`.

The connector implements only the token half of that flow. `client_id`, `client_secret`, `refresh_token` and `realm_id` are user-entered, and `OAuthAuthenticator` exchanges the refresh token for access tokens. `refresh_token_updater` persists the rotated values back into the connection config, which matters more here than for most APIs: Intuit rotates the refresh token roughly every 24 hours and expires it after 100 days of disuse, so a connection whose replacement token is not persisted stops working within a day.

`realm_id` is a company identifier rather than a credential, but it keeps `airbyte_secret: true`. Existing configs persisted it into the secret store, and dropping the flag leaves the platform with a stored secret coordinate for a field it no longer hydrates, so un-secreting it needs a platform-side migration rather than a spec edit.

`access_token` and `token_expiry_date` are therefore **not** required inputs — the connector derives and maintains them. They remain in the spec because `refresh_token_updater` writes them there.

Cloud shows an "Authenticate" button driven by `spec.advanced_auth` and the platform's built-in `QuickbooksOAuthFlow`, which captures `realmId` from the consent redirect. Declarative OAuth (`oauth_connector_input_specification`) is deliberately not used: it can only extract fields from the token response, `realmId` arrives on the redirect query params instead, and the platform prefers the declarative flow whenever the spec declares one — adding it would silently drop `realm_id` from generated configs. That constraint, not inertia, is the justification for keeping the legacy `advanced_auth` shape.

## Incremental Stream Considerations

32 of the 34 streams are incremental with the same shape; `company_info` and `preferences` are full refresh (see below). QuickBooks exposes no cursor field at the top level of an entity: the modification timestamp lives at `MetaData.LastUpdatedTime`, so each stream hoists it to a synthesized top-level `airbyte_cursor` with `AddFields`, and the `DatetimeBasedCursor` uses that field.

Server-side filtering is done in the SQL-like query language rather than with request parameters:

```sql
SELECT * FROM Account
WHERE Metadata.LastUpdatedTime > '<slice start>' AND Metadata.LastUpdatedTime <= '<slice end>'
AND Active IN (true, false)
ORDER BY Metadata.LastUpdatedTime ASC
STARTPOSITION <n> MAXRESULTS <max_results>
```

The casing in that query (`Metadata`) reproduces the manifest verbatim and differs from the record field the cursor and schema use (`MetaData`). Both spellings predate `4.0.0` and incremental syncs work in production, so Intuit evidently resolves the query identifier case-insensitively — inference from behavior, not from Intuit's documentation. Do not normalize the query occurrences without a live API to verify against.

`step: P30D` windows the query, and `cursor_granularity: PT0S` with a `>` lower bound makes slices non-overlapping. `Active IN (true, false)` is required because QuickBooks otherwise returns only active records. Six streams are on entities that expose no `Active` field — `company_info`, `preferences`, `exchange_rates`, `reimburse_charges`, `attachables`, `credit_card_payments` — and Intuit rejects the clause with an `Invalid query` fault on those entities, so their queries omit it (verified against the sandbox query endpoint). `company_info` and `preferences` run full refresh instead: they are single-row entities, and `CompanyInfo`'s windowed query is unusable anyway — Intuit applies `>` against a stale internal timestamp and ignores `<=`, which would either drop the row or re-emit it once per slice. `ExchangeRate` expands to per-currency-pair-per-day rows, so `exchange_rates` is a large stream (~192k records for a 2023 sandbox start date).

Two things to know before changing this:

- The cursor is connector-synthesized. If a record ever arrives without `MetaData.LastUpdatedTime`, `airbyte_cursor` is null and the record's position in the ordering is undefined.
- The query's timestamp offsets are spliced textually (`stream_slice.end_time[:-2] + ":" + stream_slice.start_time[-2:]`), so the end bound borrows the start bound's UTC offset. This is correct only while both bounds carry the same offset, which they do today because `start_datetime`/`end_datetime` are both UTC.

## Deletions

The connector's canonical deletion pattern is the deletion-flag field on the primary stream — `Active: false` — not a dedicated `deleted_*` stream. The `Active IN (true, false)` clause in the stream query is what makes that flag arrive: QuickBooks filters inactive records out by default, so the flag would never reach the destination without the clause. The 6 streams on entities with no `Active` field (`company_info`, `preferences`, `exchange_rates`, `reimburse_charges`, `attachables`, `credit_card_payments`) omit the clause and have no soft-delete signal at all.

QuickBooks soft-deletes by flipping `Active` to false, which the query captures — an updated `MetaData.LastUpdatedTime` brings the record through on the next incremental sync with `Active: false`.

Hard deletes are **not** captured. Intuit exposes them only through the [change data capture](https://developer.intuit.com/app/developer/qbo/docs/develop/explore-the-quickbooks-online-api/change-data-capture) endpoint, which this connector does not read, so a hard-deleted record simply stops being returned and remains in the destination. There is no deletion flag for it.

## Error handling

All 34 streams share `definitions.error_handler`. Intuit returns errors as a `Fault` object carrying its own error code alongside the HTTP status, and the two disagree often enough that the filters check both. Filter order matters — the CDK returns the first match — so the fault-code filters must stay ahead of the status-code filters.

The fault code is matched with a `predicate` rather than `error_message_contains`, because the latter is compared against `JsonErrorMessageParser.parse_response_error_message()`, which only walks lowercase keys (`message`, `error`, `detail`, …). Intuit's payload is `{"Fault": {"Error": [{"Message": …, "code": "3200"}]}}`, so the parser returns `None` and no substring can ever match. The predicate reads `Fault.Error[0].code`, tolerates either capitalization and the zero-padded form (`003200`), and is guarded with `response is mapping` so it cannot match a successful response — `HttpResponseFilter` evaluates predicates against every response, including HTTP 200s.

| Response | Action | Failure type | Rationale |
| --- | --- | --- | --- |
| Fault code `3200` (`ApplicationAuthenticationFailed`) | FAIL | `config_error` | The app credentials themselves are rejected: wrong `client_id`/`client_secret`, or development keys used against production. Retrying cannot help. |
| Fault code `3201` (`AuthorizationFailure`) | FAIL | `config_error` | The user has not authorized the app for this company, or authorization was revoked in Intuit's My Apps. |
| 401 | FAIL | `config_error` | The OAuth grant is expired or revoked. Intuit invalidates the refresh token after 100 days of disuse, and re-authentication is the only remedy — retrying with the same grant will not recover. |
| 403 | FAIL | `config_error` | The grant lacks the `com.intuit.quickbooks.accounting` scope for this company. |
| 404 | FAIL | `config_error` | Intuit does not recognize the configured `realm_id` (commonly a sandbox realm used against production, or vice versa). |
| 429 | RATE_LIMITED | `transient_error` | Intuit's documented throttling response. `RATE_LIMITED` retries like `RETRY` but additionally emits a stream status of `RUNNING` with reason `RATE_LIMITED`, so throttling is visible in the sync UI instead of looking like a stalled stream. |
| 500, 502, 503, 504 | RETRY | `transient_error` | Intuit server errors; `max_retries: 5` with `ExponentialBackoffStrategy` at factor 5. |
| Any other error response | FAIL (terminal) | `system_error` | CDK `DefaultErrorHandler` fallback. An explicit catch-all filter is deliberately omitted: `HttpResponseFilter` predicates are evaluated against every response, including HTTP 200s, so a literal catch-all would match successful responses. |

The stream error handler only sees responses from the accounting API. A refresh token Intuit rejects at `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer` never reaches it, so every `OAuthAuthenticator` sets `refresh_token_error_status_codes: [400, 401]`, `refresh_token_error_key: error` and `refresh_token_error_values: [invalid_grant, invalid_client]`. That makes the CDK raise a `config_error` telling the user to re-authenticate instead of a generic authentication failure. Intuit answers a rotated, expired or already-used refresh token with `400 {"error": "invalid_grant"}`, and rejected app credentials with `invalid_client`. The authenticator is duplicated per stream in this manifest, so all 69 occurrences (34 stream definitions, 34 top-level streams, and `definitions.base_requester`) carry the same three fields.

401 is classified as terminal rather than `REFRESH_TOKEN_THEN_RETRY` on purpose. `OAuthAuthenticator` already refreshes proactively from `token_expiry_date`, so a 401 reaching the error handler means the refresh itself is not fixing the problem — retrying it burns the rotation window instead of surfacing an actionable message.

The `error_message` strings are deterministic and interpolate nothing: they state the failure condition, and remediation lives in this document and the [connector docs](https://docs.airbyte.com/integrations/sources/quickbooks).

## Rate limits and concurrency

Intuit documents [throttling](https://developer.intuit.com/app/developer/qbo/docs/develop/troubleshooting/error-codes#rate-limits) at 500 requests per minute and 10 requests per second per realm, plus 40 concurrent requests per app, answered with HTTP 429. The manifest declares all three: `api_budget` is a single `MovingWindowCallRatePolicy` carrying both rates (10 per sliding `PT1S` and 500 per sliding `PT1M`, listed in ascending order as the CDK requires) across all endpoints, and `concurrency_level` runs 4 streams at a time (`max_concurrency: 40`, matching Intuit's concurrent-request cap). A fixed-window policy must not be used here: the CDK seeds its window reset 10 days out and relies on `ratelimit-*` response headers to correct it, which Intuit does not send, so after 500 calls every worker would sleep for the rest of the window. Without an explicit `concurrency_level` the CDK's `ConcurrentDeclarativeSource` would still run 2 streams concurrently, so the declaration is what makes the limit deliberate rather than incidental. `max_results` (spec field **Page Size**, default 200, max 1,000 per Intuit's query limits) is the lever that reduces page count on companies with long histories (34 streams × one request per 30-day window per page). `company_info` and `preferences` omit `MAXRESULTS` entirely: they are single-row entities on `NoPagination`, so a page size is meaningless there.

## Config shape history

`4.0.0` flattened the config: `credentials.client_id` and siblings moved to the root. It shipped no config migration, so connections created before it stopped loading rather than being upgraded. `4.2.0` closes that gap with `spec.config_normalization_rules.config_migrations`: a `ConfigMigration` that lifts the six `credentials.*` fields to the root (`ConfigAddFields`, skipping absent optional ones) and drops `credentials` (`ConfigRemoveFields`). Each lifted value reads the root field first and falls back to the nested one, so a hybrid config that carries both shapes keeps its root values instead of being overwritten by a stale nested copy. A third transformation writes `auth_type: oauth2.0` whenever the field is absent: it is the `advanced_auth.predicate_key` and has no default, so pre-4.0.0 and hand-written configs would otherwise never match the OAuth predicate. The CDK applies migrations in the source constructor — before `check_config_against_spec` — rewrites the config file on disk, and emits a `CONNECTOR_CONFIG` control message so the platform persists the migrated config. A nested config therefore validates and syncs without manual repopulation.

## Acceptance tests

`basic_read` bypasses 25 of the 34 streams as `empty_streams`: the CI sandbox company only holds records for 9 of them. `integration_tests/expected_records.jsonl` is not wired into `acceptance-test-config.yml` (no `expect_records` block, `test_strictness_level` is not `high`) and its 85 records were captured in 2023 from a different sandbox company, which is why it holds records for streams the bypass list calls empty. Treat it as history, not as an assertion: a `high` strictness run needs a fresh capture against the current sandbox, not a revival of that file.

## Competitor parity (Fivetran)

Fivetran's [QuickBooks connector](https://fivetran.com/docs/connectors/applications/quickbooks) reads the same Accounting API. Verdicts use the certification vocabulary: `covered` / `covered-as-field` / `missing` / `out-of-scope`.

| Fivetran table | Verdict | Reason |
| --- | --- | --- |
| `account`, `bill`, `bill_payment`, `budget`, `class`, `credit_memo`, `customer`, `department`, `deposit`, `employee`, `estimate`, `invoice`, `item`, `journal_entry`, `payment`, `payment_method`, `purchase`, `purchase_order`, `refund_receipt`, `sales_receipt`, `tax_agency`, `tax_code`, `tax_rate`, `term`, `time_activity`, `transfer`, `vendor`, `vendor_credit` | covered | The 28 original streams of this connector map one-to-one onto these entities. |
| Line-item tables (`invoice_line`, `bill_line`, `journal_entry_line`, `estimate_line`, `credit_memo_line`, `deposit_line`, `purchase_line`, `purchase_order_line`, `refund_receipt_line`, `sales_receipt_line`, `vendor_credit_line`, `bill_payment_line`) | covered-as-field | Fivetran normalizes the entity's `Line[]` array into a child table; this connector ships the array as a nested field on the parent record. |
| Linked-transaction and tax-detail tables (`*_linked_txn`, `*_tax_line`, `*_custom_field`) | covered-as-field | Same normalization difference: `LinkedTxn[]`, `TxnTaxDetail`, `CustomField[]` are nested on the parent. |
| `company_info` | covered | Synced since 4.2.0 as the `company_info` stream. |
| `preferences` | covered | Synced since 4.2.0 as the `preferences` stream. |
| `attachable` | covered | Synced since 4.2.0 as the `attachables` stream. |
| `exchange_rate` | covered | Synced since 4.2.0 as the `exchange_rates` stream; relevant only to companies with multi-currency enabled. |
| `reimburse_charge` | covered | Synced since 4.2.0 as the `reimburse_charges` stream. |
| `credit_card_payment` | covered | Synced since 4.2.0 as the `credit_card_payments` stream (`CreditCardPaymentTxn` entity). |
| `recurring_transaction` | **missing** | Records carry no `MetaData.LastUpdatedTime` and the query response wraps each record per transaction type (`{"Bill": {...}}`), so the shared incremental shape does not fit. |
| `tax_service` | **missing** | The query endpoint rejects `TaxService` (`Invalid query`) — it is served by a separate tax API, not entity queries. |
| `tax_payment` | **missing** | The query endpoint rejects `TaxPayment` on this realm ("not supported for this region"). |
| Deleted records | **missing** | Fivetran reads Intuit's change-data-capture feed for hard deletes; this connector does not (see § Deletions). |
| `transaction_list` and other report endpoints | out-of-scope | Intuit report endpoints are a separate API surface with their own request model, not entity queries. |
