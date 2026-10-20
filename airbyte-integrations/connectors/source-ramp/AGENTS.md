> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-ramp: Unique Connector Behaviors

This connector is manifest-only (`language:manifest-only`, `cdk:low-code`); everything below lives in
`manifest.yaml`. It reads Ramp's developer API at `https://api.ramp.com/developer/v1` (or
`https://demo-api.ramp.com` through the hidden `api_url` option, which is how CI reads the Ramp
sandbox). Ramp's [OpenAPI spec](https://docs.ramp.com/openapi/developer-api.json) is the most reliable
reference for fields, filters and scopes; the guide pages are rendered client-side.

## 1. One token request asks for every scope, and Ramp silently drops the ones the app lacks

Every stream logs in with the same `client_credentials` request to `POST /developer/v1/token`, and that
request asks for all 15 read scopes the connector uses. Ramp's
[authorization guide](https://docs.ramp.com/developer-api/v1/authorization) says an ungranted scope
fails the token request, but the sandbox does not behave that way: it issues a token for the subset of
scopes the app has and drops the rest (verified 2026-10-01: `transactions:read bills:write` returned a
token with only `transactions:read`). A missing scope therefore surfaces later, as a 403
`DEVELOPER_7100` on the first data call of the stream that needs it, and only that stream fails.

The token is not shared across streams. The CDK builds a separate session-token provider for every
stream's authenticator, so each selected stream logs in once per sync, and `vendor_contacts` logs in
twice because its parent `vendors` read has its own authenticator. The token lives 10 days
(`expiration_duration: PT240H`), so it never expires mid-sync.

**Why this matters:** Do not split the scope string per stream to "fix" a missing scope, and do not
drop scopes from the shared request to make the login pass for small apps: neither is needed, because
the login never fails on scope. If Ramp starts enforcing its documented `invalid_scope` behaviour, every
stream would fail at login for any app that lacks one of the 15 scopes. The live CI read would catch
that; mocked unit tests cannot.

## 2. Ramp's own error codes drive the error mapping, including a 404 for a bad token

Ramp returns errors as `{"error_v2": {"error_code": ..., "message": ...}}`
([error handling](https://docs.ramp.com/developer-api/v1/error-handling)). The shared error handler
maps them as follows, in this order:

| Response | Failure type | Message points the user to |
| --- | --- | --- |
| any status with `error_code` `DEVELOPER_7100` (missing scope) | `config_error` | grant the read scope Ramp names |
| any status with `error_code` `DEVELOPER_7002` (token no longer accepted) | `config_error` | check the app still exists and the secret was not rotated |
| `401` | `config_error` | re-enter the client ID and secret |
| `403` | `config_error` | the stream's `required_scope`, plus its `access_note` (`purchase_orders` adds "Ramp Plus only") |
| login `400` / `401` | `config_error` | re-copy the credentials; quotes Ramp's `error_v2.message` or the OAuth `error_description` |
| `429`, `5xx` | retried with `ExponentialBackoffStrategy` (factor 2), up to `max_retries: 5`; then the CDK default failure type | — |
| anything else | CDK default mapping | — |

`DEVELOPER_7002` arrives as a **404**, not a 401, so the error-code filters match on a `predicate` alone.
An `HttpResponseFilter` matches when the status is in `http_codes` **or** the predicate is true, so
adding `http_codes: [404]` next to that predicate would turn every 404 into a credentials error.
Requests are also throttled up front by an `api_budget` of 180 calls per 10 seconds, below Ramp's
published [200 per 10 seconds per IP](https://docs.ramp.com/developer-api/v1/rate-limiting).

**Why this matters:** A 404 from Ramp usually means a bad token, not a missing resource, so a generic
"404 means not found" handler on a shared requester would hide credential failures. `required_scope` and
`access_note` are per-stream `$parameters`; a new stream must set `required_scope`, or its 403 message
falls back to "the required read scope".

## 3. Several list endpoints hide records unless asked

Ramp's list endpoints apply filters by default that silently drop rows, and some return fields as null
unless an `include_*` flag is sent. The connector asks for everything:

| Stream | Ramp default | What the connector sends |
| --- | --- | --- |
| `transactions` | omits declined transactions | `state=ALL` |
| `transactions` | `merchant_data` is null | `include_merchant_data=true` |
| `reimbursements` | `direction` defaults to `BUSINESS_TO_USER` (repayments missing) | one partition per direction |
| `users` | unfiltered call omits `USER_SUSPENDED`; the `status` filter rejects the invite and onboarding statuses (422) | one unfiltered call plus one `status=USER_SUSPENDED` call |
| `funds` | omits terminated funds | partitions `is_terminated=false` and `true` |
| `bills` | omits archived (deleted) bills | partitions `is_archived=false` and `true` |
| `vendor_agreements`, `purchase_orders` | omit archived records | `include_archived=true` |
| `vendors` | `subsidiary` is null | `include_subsidiary=true` |
| `receipts` | `ocr` is null | `include_ocr_data=true` |

`vendors` still skips draft vendors and vendors waiting for approval; that is Ramp's default and the user
docs say so. `entities` does not send `include_custom_field_values`, because that flag needs the extra
`custom_records:read` scope; `custom_record_fields` is left out of the schema rather than declared as an
always-null field. `vendor_agreements` is listed with `POST /vendors/agreements`, so its filters and page
token go in the JSON body (`BodyPaginator`), not the query string.

**Why this matters:** Removing one of these parameters or partitions does not fail anything; the stream
just syncs fewer rows or more nulls. Check this table before simplifying a requester, and when adding a
stream, read the endpoint's parameters in the OpenAPI spec for a default filter or an `include_*` flag.

## 4. Deletions are replicated as a flag field on the primary stream

The connector's deletion pattern is a flag field on the primary stream, not dedicated `deleted_*`
streams. Because of the partitions in section 3, deleted or ended rows keep arriving with their final
state: `bills` with `archived_at`, `funds` terminated, `users` with `USER_INACTIVE` or `USER_SUSPENDED`,
and `vendor_agreements` and `purchase_orders` with their archived state.

Two gaps remain. `cards` never returns terminated cards (section 5). `reimbursements` has `DELETED` and
`CANCELED` states in Ramp's enum, but the sandbox has none, so whether the default list returns them is
unverified; if it does not, add a `state` partition the way `users` does.

**Why this matters:** A new stream over a resource that can be archived or terminated should read those
rows through the same flag, so downstream users find deletions the same way on every stream.

## 5. `cards` reads a legacy endpoint that Ramp no longer documents

`cards` reads `GET /developer/v1/cards`, which is not in Ramp's published spec; the spec lists only
`/cards/physical`, `/cards/virtual` and `/cards/vault`. The legacy endpoint still works, but never returns
terminated cards: `is_terminated=true` gives 0 rows, and they are missing from the unfiltered list too.
The documented endpoints are not drop-in replacements. `/cards/physical` needs
`include_terminated_only=true` together with `include_activated_only=false` (the first alone is a 400
`DEVELOPER_7076`) and has a different field set, and `/cards/virtual` returns only five fields. The user
docs explain how a terminated card disappears under Overwrite.

**Why this matters:** Moving `cards` to the documented endpoints is a breaking change, because fields
stop being populated for some rows and the record set changes. Do it only as a planned major release,
for example when Ramp removes the legacy route; it is tracked as a watch item, not a defect.

## 6. Only three streams are incremental, and `transactions` relies on an undocumented filter

`transactions` and `reimbursements` are incremental on `updated_at`, sent as `updated_after`.
`updated_after` is in Ramp's spec for `/reimbursements` but **not** for `/transactions`; the sandbox
honours it inclusively, and if Ramp ever ignores it the stream re-reads everything and emits duplicates
rather than losing records. `receipts` is incremental on `created_at` through `created_after`, because
receipts carry no `updated_at`. If Ramp matches a receipt to a transaction after the receipt was synced,
that receipt keeps `transaction_id: null` downstream; `transactions.receipts` always has the current
link.

Every other stream is full refresh. `bills`, `funds` and `purchase_orders` can only be filtered by
created date, and `vendors` accepts `from_updated_at` but its records carry no `updated_at` to use as a
cursor.

**Why this matters:** Do not make a stream incremental on `created_at` unless its records never change
after creation, or updates are lost. Watch Ramp's changelog for `updated_after` on `/transactions`.

## 7. `business_balance` has no primary key

`GET /developer/v1/business/balance` returns one object with the business's current limits and balances
and no identifier. The stream emits that single snapshot on every sync with no `primary_key`. A synthetic
key (for example a constant, or the sync time) would either collapse history or re-key every row, so
none is declared. Its billing dates are `MM/DD/YYYY` strings and are deliberately left without a `format`.

**Why this matters:** This is the connector's only keyless stream and is a documented exception to the
"every stream has a primary key" rule. Adding a key later changes dedup behaviour and is a breaking
change.

## 8. `vendor_contacts` skips vendors that return 404

`vendor_contacts` reads `GET /vendors/{vendor_id}/contacts` for every vendor from the parent read. A
vendor deleted between the parent page and its contacts call returns 404, so the stream wraps the shared
handler in a `CompositeErrorHandler` whose first handler ignores 404. The order matters for every other
error: the composite returns early only on actions such as success, retry or ignore, and on a failure it
moves on and returns the **last** handler's result. With the shared handler last, a 403 still gets its
scope message. A bad-token 404 (`DEVELOPER_7002`) is ignored here too, but the parent `vendors` read fails
on it first. The stream's key is `[vendor_id, id]`, with `vendor_id` added from the partition.

**Why this matters:** Moving the 404 filter into the shared handler would hide bad-token failures on
every stream (see section 2). Putting the 404 handler last would make its generic default mapping the
answer for every failure on this stream, losing the shared handler's actionable messages.
