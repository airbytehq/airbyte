> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-linkedin-pages: Unique Behaviors

## 1. Pinned LinkedIn API version

All requesters use the pinned `Linkedin-Version: 202610` header. LinkedIn sunsets API versions on an approximately 12-month cadence; a sunset version fails every request. Version `202610` is current, while version `202511` is scheduled to sunset on 2026-11-16. The 1.1.25 version caused fleet-wide check failures in October 2026; update the header in every requester when bumping it. `unit_tests/test_api_version.py` enforces a single version value. See [LinkedIn API versioning and release history](https://learn.microsoft.com/en-us/linkedin/marketing/versioning).

## 2. Time-bound statistics windows and cursors

`follower_statistics_time_bound` and `share_statistics_time_bound` are restricted to the previous 12 months through 2 days before today, in UTC. Their `DAY` intervals must start and end at midnight UTC; `timeRangeEnd` is LinkedIn's midnight epoch-millisecond cursor. Sub-24-hour windows can fail with `400 Invalid timeIntervals parameter` (airbytehq/airbyte#80199).

## 3. LinkedIn rate limits

Do not configure `api_budget`: LinkedIn's limits are per application, per day, reset at midnight UTC, and are not published as a fixed number ([rate-limit documentation](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)). The shared error handler retries `429` responses with backoff, capped by `max_retries`.

## 4. Lifetime aggregate streams

`organization_lookup`, `follower_statistics`, `share_statistics`, and `total_follower_count` are full-refresh streams. Each returns a single lifetime aggregate per organization and has no cursor.
