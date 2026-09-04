# Contributing to source-greenhouse

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Harvest v3 stream behavior

This connector uses Greenhouse Harvest v3 with a single OAuth Authorization Code authentication branch. The `OAuthAuthenticator` uses the `refresh_token` grant, HTTP Basic authentication, `expires_at` with `token_expiry_date_format`, and `refresh_token_updater` to persist each rotated refresh token. The `advanced_auth` predicate must remain `[credentials, auth_type]` with `predicate_value: Client`. The `credentials` `oneOf` shape is deliberately retained so a `ClientCredentials` branch can be added additively in a follow-up. Connections idle longer than the approximately 24-hour refresh-token lifetime require manual reauthentication. Cursor follow-up requests use the opaque URL from the `Link` header and must not repeat first-request-only parameters such as `per_page`, date filters, parent filters, or static filters. The legacy `applied_at` watermark is discarded during the 1.0.0 upgrade so `applications` backfills once on the new `updated_at` cursor.
All streams use the v3 cursor paginator with a first-page `per_page` value of 500 (the v3 maximum; the server default is 100).

v3 invariants a future edit must not break:

- A request carrying `cursor` must carry **no other query parameter**. Anything else returns `422 {"errors":["When passing a cursor, do not include other query params."]}`. This is why every first-page parameter is wrapped in `{{ ... if not next_page_token }}`.
- Five streams have grouped substream routers: `demographics_answers_answer_options`, `demographics_question_sets_questions`, `jobs_openings`, `activity_feed`, and `user_permissions`. All five use `GroupingPartitionRouter` with `partition_field: parent_id`; the partition value is a list joined with `,`. `group_size: 50` is pinned by the documented `maxItems: 50` on every `*_ids` filter - do not raise it. `job_posts` separately uses a `ListPartitionRouter` over `active` with `true` and `false` values.
- v3 paginates by primary key **descending**, not by cursor field. Every incremental first request must send a two-sided `gte|…|lte|…` window bounded by the slice end because state advances to the maximum observed record; do not reduce it to a lower-bound-only filter.
- `users` must send `show_service_accounts=true` on the first page; v3 hides integration service users by default.
- `/v3/demographic_questions` and `/v3/demographic_answer_options` expose no `created_at`/`updated_at` filter, which is why those streams are full refresh.
- Incremental streams use the optional `start_date` configuration value and default to all history when it is omitted.
- `job_ids` on `/v3/approval_flows` excludes `offer_candidate` flows.
- HTTP 401 responses must remain `REFRESH_TOKEN_THEN_RETRY`, and the API budget must model Greenhouse's fixed 30-second window with `X-RateLimit-Reset` and `X-RateLimit-Remaining`; do not switch it back to a moving window.

### Verifying v3 query-parameter behavior

Harvest v3's reference prose does not document the comparison-operator syntax for date filters, so treat the interactive request builder on the reference pages as the authoritative check. The two-sided window this connector sends was confirmed that way on [`GET /v3/user_emails`](https://harvestdocs.greenhouse.io/reference/get_v3-user-emails), which builds:

```
curl --request GET \
     --url 'https://harvest.greenhouse.io/v3/user_emails?updated_at=gte|2024-01-01T00%3A00%3A00Z|lte|2024-01-02T00%3A00%3A00Z' \
     --header 'accept: application/json'
```

That is, `updated_at=gte|{datetime}|lte|{datetime}`, with `|` separating operator and value, and it is the shape every cursor-field date filter here uses (`submitted_at` for `eeoc`). Do not rewrite it into repeated parameters, `updated_at[gte]`-style brackets, or a lower bound alone because the reference text does not mention it; build the request in the docs page first and match what it produces.

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
| rejection_reasons | top-level | none | none | full refresh |
| scorecards | top-level | updated_at | updated_at | incremental |
| sources | top-level | none | none | full refresh |
| users | top-level | updated_at | updated_at | incremental |
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
