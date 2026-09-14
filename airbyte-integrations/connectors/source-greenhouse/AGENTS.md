# source-greenhouse: Unique Connector Behaviors

## 1. Partner-Application OAuth With Single-Use Rotating Refresh Tokens

Greenhouse Harvest v3 is reached through OAuth 2.0 Authorization Code issued to Airbyte's registered [Greenhouse partner application](https://harvestdocs.greenhouse.io/docs/harvest-partner-oauth). Greenhouse issues Authorization Code credentials only to integration partners, so customers never supply a `client_id`/`client_secret`: the platform fills `credentials.client_id` and `credentials.client_secret` from the instance-wide OAuth parameters registered for this connector definition, via `complete_oauth_server_output_specification`, and the spec descriptions tell users not to request credentials from Greenhouse. Because those parameters only exist in Airbyte Cloud, the consent flow (and therefore the connector) is effectively Cloud-only. The consent URL requests every `harvest:*:list` scope the streams need; a missing scope or a non-Site-Admin authorizing user surfaces as a `403` config error on the affected stream, and `check` reads `users`, so `harvest:users:list` is required for setup to succeed at all.

The `OAuthAuthenticator` uses the `refresh_token` grant with HTTP Basic client authentication, parses `expires_at` with `token_expiry_date_format`, and persists each rotated refresh token through `refresh_token_updater` (`credentials.access_token`, `credentials.refresh_token`, `credentials.token_expiry_date`). Greenhouse refresh tokens are single-use and expire after approximately 24 hours without use, so a connection paused or failing for more than a day needs the consent flow re-run. Refresh failures are matched on the RFC 6749 `error` key (`invalid_grant`, `invalid_client`, `unauthorized_client`; status 400/401), which the CDK reports as a re-authenticate `config_error`; Greenhouse does not return the `{"message": ...}` shape shown in its docs for these cases. HTTP 401 on data requests is `REFRESH_TOKEN_THEN_RETRY`. The `advanced_auth` predicate must remain `[credentials, auth_type]` with `predicate_value: Client`, and the `credentials` `oneOf` shape is deliberately retained so a `ClientCredentials` branch can be added additively later.

**Why this matters:** Changing the refresh error key back to `message`, dropping `refresh_token_updater`, or reusing one refresh token in two places turns a routine expired-token event into an opaque system error or a permanently broken source. Editing the spec's `client_id`/`client_secret` fields or the `advanced_auth` predicate can break the Cloud override that injects Airbyte's partner credentials, and any new stream needs its scope added to the consent URL's `scope` list.

## 2. Cursor Follow-Up Requests Carry No Other Query Parameters

Harvest v3 paginates with opaque cursor URLs in the `Link` response header. A request carrying `cursor` must carry **no other query parameter**; anything else returns `422 {"errors":["When passing a cursor, do not include other query params."]}`. This is why every first-page parameter (`per_page`, date filters, parent-ID filters, static filters such as `custom_field_key` or `include_defaults`) is wrapped in `{{ ... if not next_page_token }}`. All streams send `per_page=500` on the first page, the v3 maximum (the server default is 100).

**Why this matters:** Adding a request parameter without the `if not next_page_token` guard breaks every stream on page two, and the failure only appears against accounts large enough to paginate.

## 3. Descending Primary-Key Pagination Forces Two-Sided Date Windows

v3 orders results by primary key **descending**, not by cursor field, and state advances to the maximum observed cursor value. Every incremental first request therefore sends a two-sided `updated_at=gte|{start}|lte|{end}` window bounded by the slice end (`submitted_at` for `eeoc`); a lower-bound-only filter would let late pages carry records newer than the state already emitted. Incremental streams take the optional `start_date` config value and default to all history when it is omitted. The legacy `applied_at` watermark on `applications` is discarded during the 1.0.0 upgrade (it maps to v3 `created_at`), so that stream backfills once on `updated_at`.

**Why this matters:** Reducing the window to a lower bound alone, or rewriting the `gte|…|lte|…` syntax into bracketed or repeated parameters, silently drops records; see [Verifying v3 query-parameter behavior](#verifying-v3-query-parameter-behavior) before touching a date filter.

## 4. Grouped Substream Routers Pinned to 50 Parent IDs

Five child streams (`demographics_answers_answer_options`, `demographics_question_sets_questions`, `jobs_openings`, `activity_feed`, `user_permissions`) use `GroupingPartitionRouter` with `partition_field: parent_id` and pass the group as a comma-joined `*_ids` filter on the first page. `group_size: 50` is pinned by the documented `maxItems: 50` on every `*_ids` filter; do not raise it. Parents are always read over full history (`full_history_cursor`) regardless of `start_date`, so child coverage does not depend on the start date. `job_posts` separately uses a `ListPartitionRouter` over `active` with `true` and `false` so deleted posts are included.

**Why this matters:** Raising `group_size` produces `422` on every child request, and filtering parents by `start_date` would silently shrink the child streams.

## 5. Fixed-Window Rate Limit Budget With No Published Ceiling

Greenhouse [rate limits](https://harvestdocs.greenhouse.io/docs/api-rate-limiting) v3 in fixed 30-second windows, publishes no ceiling, and applies different allowances to custom and partner integrations. The `HTTPAPIBudget` uses a `FixedWindowCallRatePolicy` of 50 calls per `PT30S` (a deliberate undershoot of the only observed `X-RateLimit-Limit: 75`), reads `X-RateLimit-Reset`/`X-RateLimit-Remaining`, treats `429` as a hit, and backs off on `Retry-After`. All worker threads (`num_workers`, default 2, max 8) share this single budget.

**Why this matters:** Switching to a moving window or raising `call_limit` without an observed header value causes `429` storms that scale with concurrency; the rate limit is per account, not per thread.

## 6. Stream-Specific First-Page Parameters

- `users` sends `show_service_accounts=true`; v3 hides integration service users by default, and those records have no `primary_email`.
- `rejection_reasons` sends `include_defaults=true` to include Greenhouse's built-in reasons.
- `degrees`, `disciplines`, and `schools` read `/v3/custom_field_options` filtered by `custom_field_key` (`degree`, `discipline`, `school_name`); `custom_field_options` reads it unfiltered and is a superset sharing the same `id` primary key.
- `/v3/demographic_questions` and `/v3/demographic_answer_options` expose no `created_at`/`updated_at` filter, which is why those streams are full refresh.
- `job_ids` on `/v3/approval_flows` excludes `offer_candidate` flows.

**Why this matters:** These parameters are the only difference between several streams that share an endpoint; removing one changes record counts without producing an error.

## Verifying v3 query-parameter behavior

Harvest v3's reference prose does not document the comparison-operator syntax for date filters, so treat the interactive request builder on the reference pages as the authoritative check. The two-sided window this connector sends was confirmed that way on [`GET /v3/user_emails`](https://harvestdocs.greenhouse.io/reference/get_v3-user-emails), which builds:

```
curl --request GET \
     --url 'https://harvest.greenhouse.io/v3/user_emails?updated_at=gte|2024-01-01T00%3A00%3A00Z|lte|2024-01-02T00%3A00%3A00Z' \
     --header 'accept: application/json'
```

That is, `updated_at=gte|{datetime}|lte|{datetime}`, with `|` separating operator and value, and it is the shape every cursor-field date filter here uses (`submitted_at` for `eeoc`). Do not rewrite it into repeated parameters, `updated_at[gte]`-style brackets, or a lower bound alone because the reference text does not mention it; build the request in the docs page first and match what it produces.

## Stream reference

| Stream | Relationship | Cursor field | Request filter | Status |
|---|---|---|---|---|
| applications | top-level | updated_at | updated_at | incremental |
| candidates | top-level | updated_at | updated_at | incremental |
| close_reasons | top-level | none | none | full refresh |
| custom_fields | top-level | none | none | full refresh |
| custom_field_options | top-level | none | none | full refresh |
| degrees | top-level | none | custom_field_key=degree | full refresh |
| demographics_answers | top-level | updated_at | updated_at | incremental |
| demographics_answer_options | top-level | none | none | full refresh |
| demographics_questions | top-level | none | none | full refresh |
| demographics_answers_answer_options | child | none | demographic_question_ids | full refresh |
| demographics_question_sets | top-level | none | none | full refresh |
| demographics_question_sets_questions | child | none | demographic_question_set_ids | full refresh |
| departments | top-level | none | none | full refresh |
| jobs | top-level | updated_at | updated_at | incremental |
| jobs_openings | child | none | job_ids | full refresh |
| interviews | top-level | updated_at | updated_at | incremental |
| job_posts | top-level | updated_at | updated_at, active | incremental |
| job_stages | top-level | updated_at | updated_at | incremental |
| offers | top-level | updated_at | updated_at | incremental |
| rejection_reasons | top-level | none | include_defaults | full refresh |
| scorecards | top-level | updated_at | updated_at | incremental |
| sources | top-level | none | none | full refresh |
| users | top-level | updated_at | updated_at, show_service_accounts | incremental |
| activity_feed | child | none | candidate_ids | full refresh |
| approvals | top-level | none | none | full refresh |
| disciplines | top-level | none | custom_field_key=discipline | full refresh |
| schools | top-level | none | custom_field_key=school_name | full refresh |
| eeoc | top-level | submitted_at | submitted_at | incremental |
| email_templates | top-level | updated_at | updated_at | incremental |
| offices | top-level | none | none | full refresh |
| prospect_pools | top-level | none | none | full refresh |
| tags | top-level | none | none | full refresh |
| user_roles | top-level | none | none | full refresh |
| user_permissions | child | none | user_ids | full refresh |
