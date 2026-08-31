> NOTE: CLAUDE.md and CONTRIBUTING.md are symlinks to AGENTS.md; update AGENTS.md (not the symlinks) when changing these instructions.

# Contributing to source-quickbooks

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication

QuickBooks Online uses three-legged OAuth 2.0 against Intuit's identity service: the consent flow at `https://appcenter.intuit.com/connect/oauth2` returns an authorization code plus the `realmId` of the company the user selected, and the code is exchanged at `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer`.

The connector implements only the token half of that flow. `client_id`, `client_secret`, `refresh_token` and `realm_id` are user-entered, and `OAuthAuthenticator` exchanges the refresh token for access tokens. `refresh_token_updater` persists the rotated values back into the connection config, which matters more here than for most APIs: Intuit rotates the refresh token roughly every 24 hours and expires it after 100 days of disuse, so a connection whose replacement token is not persisted stops working within a day.

`access_token` and `token_expiry_date` are therefore **not** required inputs — the connector derives and maintains them. They remain in the spec because `refresh_token_updater` writes them there.

There is no `oauth_connector_input_specification`, so Cloud shows no "Authenticate" button and users paste tokens from Intuit's OAuth 2.0 playground. Adding declarative OAuth requires capturing `realmId` from the consent redirect (not from the token response), which is why it is tracked separately rather than bundled with the error-handling work.

## Incremental Stream Considerations

All 28 streams are incremental with the same shape. QuickBooks exposes no cursor field at the top level of an entity: the modification timestamp lives at `MetaData.LastUpdatedTime`, so each stream hoists it to a synthesized top-level `airbyte_cursor` with `AddFields`, and the `DatetimeBasedCursor` uses that field.

Server-side filtering is done in the SQL-like query language rather than with request parameters:

```sql
SELECT * FROM Account
WHERE Metadata.LastUpdatedTime > '<slice start>' AND Metadata.LastUpdatedTime <= '<slice end>'
AND Active IN (true, false)
ORDER BY Metadata.LastUpdatedTime ASC
STARTPOSITION <n> MAXRESULTS <max_results>
```

`step: P30D` windows the query, and `cursor_granularity: PT0S` with a `>` lower bound makes slices non-overlapping. `Active IN (true, false)` is required because QuickBooks otherwise returns only active records.

Two things to know before changing this:

- The cursor is connector-synthesized. If a record ever arrives without `MetaData.LastUpdatedTime`, `airbyte_cursor` is null and the record's position in the ordering is undefined.
- The query's timestamp offsets are spliced textually (`stream_slice.end_time[:-2] + ":" + stream_slice.start_time[-2:]`), so the end bound borrows the start bound's UTC offset. This is correct only while both bounds carry the same offset, which they do today because `start_datetime`/`end_datetime` are both UTC.

## Deletions

QuickBooks soft-deletes by flipping `Active` to false, which the query captures — an updated `MetaData.LastUpdatedTime` brings the record through on the next incremental sync with `Active: false`.

Hard deletes are **not** captured. Intuit exposes them only through the [change data capture](https://developer.intuit.com/app/developer/qbo/docs/develop/explore-the-quickbooks-online-api/change-data-capture) endpoint, which this connector does not read, so a hard-deleted record simply stops being returned and remains in the destination. There is no deletion flag for it.

## Error handling

All 28 streams share `definitions.error_handler`. Intuit returns errors as a `Fault` object carrying its own `errorCode` alongside the HTTP status, and the two disagree often enough that the filters check both. Filter order matters — the CDK returns the first match — so the `errorCode` filters must stay ahead of the status-code filters.

| Response | Action | Failure type | Rationale |
|---|---|---|---|
| `errorCode=003200` (`ApplicationAuthenticationFailed`) | FAIL | `config_error` | The app credentials themselves are rejected: wrong `client_id`/`client_secret`, or development keys used against production. Retrying cannot help. |
| `errorCode=003201` (`AuthorizationFailure`) | FAIL | `config_error` | The user has not authorized the app for this company, or authorization was revoked in Intuit's My Apps. |
| 401 | FAIL | `config_error` | The OAuth grant is expired or revoked. Intuit invalidates the refresh token after 100 days of disuse, and re-authentication is the only remedy — retrying with the same grant will not recover. |
| 403 | FAIL | `config_error` | The grant lacks the `com.intuit.quickbooks.accounting` scope for this company. |
| 404 | FAIL | `config_error` | Intuit does not recognize the configured `realm_id` (commonly a sandbox realm used against production, or vice versa). |
| 429, 500, 502, 503, 504 | RETRY | `transient_error` | Intuit's documented throttling response and server errors; `max_retries: 5` with `ExponentialBackoffStrategy` at factor 5. |
| Any other error response | FAIL (terminal) | `system_error` | CDK `DefaultErrorHandler` fallback. An explicit catch-all filter is deliberately omitted: `HttpResponseFilter` predicates are evaluated against every response, including HTTP 200s, so a literal catch-all would match successful responses. |

401 is classified as terminal rather than `REFRESH_TOKEN_THEN_RETRY` on purpose. `OAuthAuthenticator` already refreshes proactively from `token_expiry_date`, so a 401 reaching the error handler means the refresh itself is not fixing the problem — retrying it burns the rotation window instead of surfacing an actionable message.

The `error_message` strings are deterministic and interpolate nothing: they state the failure condition, and remediation lives in this document and the [connector docs](https://docs.airbyte.com/integrations/sources/quickbooks).

## Rate limits and concurrency

Intuit documents [throttling](https://developer.intuit.com/app/developer/qbo/docs/develop/troubleshooting/error-codes#rate-limits) at 500 requests per minute per realm and 40 concurrent requests per app, answered with HTTP 429. The connector declares no `api_budget` and no `concurrency_level`, so streams run sequentially and one request at a time — comfortably inside both limits, at the cost of sync duration on companies with long histories (28 streams × one request per 30-day window per page). `max_results` (default 200, max 1,000 per Intuit's query limits) is the lever that reduces page count.

## Config shape history

`4.0.0` flattened the config: `credentials.client_id` and siblings moved to the root. It shipped no config migration, so connections created before it stop loading rather than being upgraded — the breaking-change message asks users to repopulate the fields by hand. This cannot be repaired inside the manifest alone: the platform validates the config against the spec before any interpolation runs, so a legacy nested config fails on missing required root fields before a fallback expression such as `config.get('client_id') or config.credentials.client_id` would ever be evaluated. Fixing it needs a real config migration, which manifest-only connectors have no entrypoint hook for.

## Competitor parity (Fivetran)

Fivetran's [QuickBooks connector](https://fivetran.com/docs/connectors/applications/quickbooks) reads the same Accounting API. Verdicts use the certification vocabulary: `covered` / `covered-as-field` / `missing` / `out-of-scope`.

| Fivetran table | Verdict | Reason |
|---|---|---|
| `account`, `bill`, `bill_payment`, `budget`, `class`, `credit_memo`, `customer`, `department`, `deposit`, `employee`, `estimate`, `invoice`, `item`, `journal_entry`, `payment`, `payment_method`, `purchase`, `purchase_order`, `refund_receipt`, `sales_receipt`, `tax_agency`, `tax_code`, `tax_rate`, `term`, `time_activity`, `transfer`, `vendor`, `vendor_credit` | covered | The 28 streams of this connector map one-to-one onto these entities. |
| Line-item tables (`invoice_line`, `bill_line`, `journal_entry_line`, `estimate_line`, `credit_memo_line`, `deposit_line`, `purchase_line`, `purchase_order_line`, `refund_receipt_line`, `sales_receipt_line`, `vendor_credit_line`, `bill_payment_line`) | covered-as-field | Fivetran normalizes the entity's `Line[]` array into a child table; this connector ships the array as a nested field on the parent record. |
| Linked-transaction and tax-detail tables (`*_linked_txn`, `*_tax_line`, `*_custom_field`) | covered-as-field | Same normalization difference: `LinkedTxn[]`, `TxnTaxDetail`, `CustomField[]` are nested on the parent. |
| `company_info` | **missing** | The `CompanyInfo` entity is not synced. Small, single-row, and cheap to add; the most defensible parity gap to close first. |
| `preferences` | **missing** | The `Preferences` entity is not synced. |
| `attachable` | **missing** | Attachment metadata (`Attachable`) is not synced. |
| `exchange_rate` | **missing** | Multi-currency exchange rates are not synced; relevant only to companies with multi-currency enabled. |
| `recurring_transaction`, `reimburse_charge`, `tax_service` | **missing** | Lower-traffic entities not requested by users to date. |
| `credit_card_payment` | **missing** | Newer Intuit entity, not modelled by this connector. |
| Deleted records | **missing** | Fivetran reads Intuit's change-data-capture feed for hard deletes; this connector does not (see § Deletions). |
| `transaction_list` and other report endpoints | out-of-scope | Intuit report endpoints are a separate API surface with their own request model, not entity queries. |
