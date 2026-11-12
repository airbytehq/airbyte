# Contributing to source-outreach

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors

### Pagination and page sizes

Every stream sends `sort=updatedAt` and follows the full URL in `links.next` until it is absent
([Pagination](https://developers.outreach.io/api/common-patterns/)).

- **Page size is 1000, the API maximum.** `page[size]=1001` returns `400 pageParameter.sizeInvalid`
  ("must be a number between 1 and 1000, inclusive").
- **`mailings` uses 100.** A page of 1000 returned 502 on large HTML bodies
  ([#54654](https://github.com/airbytehq/airbyte/pull/54654)).
- **`call_dispositions` and `call_purposes` are not paginated.** `/callDispositions` and `/callPurposes` ignore
  `page[size]`, return every row and send no `next` link. The paginator stays on them and stops after the first page.
- **The `page[after]` cursor is a keyset cursor.** Decoded, it holds the sort field and the last sort values
  (`{"sp":"updatedAt","sv":[...]}`), so paging continues from the last row read. A record that is updated during the
  read moves later in the sort order and is not skipped.

### Incremental sync

- Every stream is incremental on `updatedAt` and filters with `filter[updatedAt][gte]`. The filter includes the
  cursor value, so the last record of the previous sync is read again.
- State is saved as `%Y-%m-%dT%H:%M:%S.%_msZ`. `/callDispositions` and `/callPurposes` return `updatedAt` without
  milliseconds (`2021-07-08T18:39:55Z`), so each cursor lists both formats in `cursor_datetime_formats`. Without the
  second format the value fails to parse and the state stays at `start_date`.
- `is_data_feed: true` is set on every stream: a record older than the saved cursor is dropped and stops the read.

### Error handling

Outreach returns errors as `{"errors": [{"id", "title", "detail"}]}`
([Errors](https://developers.outreach.io/api/common-patterns/)).

| Status | Action | Source |
| :----- | :----- | :----- |
| 401 | Refresh the access token, then retry | Expired access token. Manifest filter |
| 403 | Fail as a configuration error. The message quotes `errors[0].detail`, which names the missing OAuth scope | `unauthorizedOauthScope`, seen on a live request with a token that lacks the scope. Manifest filter |
| 404 | Fail as a system error | `resourceNotFound`. No list endpoint documents a benign 404. CDK default |
| 422 | Fail as a system error | CDK default for an unmapped status |
| 429 | Wait until the time in `Retry-After`, then retry | `rateLimitExceeded`, [Rate limiting](https://developers.outreach.io/api/getting-started/#rate-limiting). CDK default action, manifest backoff |
| 503 | Retry with exponential backoff | `scheduledServerMaintenance`, [Maintenance](https://developers.outreach.io/api/getting-started/). CDK default action, manifest backoff |

The backoff strategies run in order:

1. `WaitUntilTimeFromHeader` on `Retry-After`. The docs make `Retry-After` an alias of `X-RateLimit-Reset`, which is a
   Unix epoch on live 200 and 400 responses; no live 429 has been captured. The strategy has no `min_wait`: with one set, it would return that value whenever the header is missing and
   the exponential strategy would never run.
2. `ExponentialBackoffStrategy` for everything else. A maintenance 503 sends an ISO-8601 `Retry-After`, which the
   first strategy cannot read, so it lands here.

### Rate limits and concurrency

- Outreach allows 10,000 requests per hour per user and sends `X-RateLimit-Remaining` and `X-RateLimit-Reset` (a Unix
  epoch) on every response ([Rate limiting](https://developers.outreach.io/api/getting-started/#rate-limiting)). Other
  apps authorized by the same user share the quota.
- The `api_budget` uses a `FixedWindowCallRatePolicy` of 10,000 calls and reads both headers. Each response moves the
  window's end to `X-RateLimit-Reset` and lowers the local count to `X-RateLimit-Remaining`, so when Outreach reports no
  calls left (a 429, or `X-RateLimit-Remaining: 0`), every worker waits until Outreach resets the quota and no longer.
- A `MovingWindowCallRatePolicy` was tried first. It ignores the reset time and, once told the quota is used up, holds
  every request for a full hour, even when Outreach resets in seconds.
- The CDK starts the fixed window ten days long until the first response sets its end, and it parses the reset header
  with `int()`. Both rely on Outreach sending an integer `X-RateLimit-Reset`, which it does on every live response
  seen so far.
- `maxSecondsBetweenMessages` is 7200, above the longest wait for a reset (one hour).
- `num_workers` (default 3, 2 to 10) sets how many streams are read at the same time. All workers share the budget.

### Schemas

- The API returns [JSON:API](https://jsonapi.org/) resources. The connector merges `attributes` into the record, keeps
  the top-level `id`, and replaces each relationship with the list of related ids.
- Field types come from the [OpenAPI spec](https://api.outreach.io/api/v2/schema/openapi.json). Fields the API returns
  but the spec does not list are typed from live values.

## Testing

- `unit_tests/mock_server/` has one test file per stream plus `test_error_handling.py` and `test_spec.py`. They need
  no Outreach account. Run them from `unit_tests/` with `poetry run pytest mock_server/ -vv`.
- The acceptance tests read the CI secret `SECRET_SOURCE-OUTREACH_CREDS`. Outreach issues a new refresh token with
  every access token and a refresh token stays active for 14 days
  ([Token availability](https://developers.outreach.io/api/getting-started/)). A local run that refreshes the token
  receives a refresh token the stored secret does not have, so prefer CI for credentialed runs.
- `sequence_states` is the only stream the test account cannot seed; its mock-server test is its only coverage.
