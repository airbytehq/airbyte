# source-linkedin-pages: Unique Connector Behaviors

## 1. Pinned LinkedIn API version

All requesters send the pinned `Linkedin-Version: 202610` header. LinkedIn publishes a new Marketing API version every month and supports each one for at least a year ([versioning and release history](https://learn.microsoft.com/en-us/linkedin/marketing/versioning)). A sunset version answers `426` with code `NONEXISTENT_VERSION` ([error responses, example 5](https://learn.microsoft.com/en-us/linkedin/marketing/error-responses#example-5-version-header-is-deprecated)); the shared error handler fails such a request at once with a message to upgrade the connector instead of retrying it. `unit_tests/test_api_version.py` enforces a single version value across requesters.

**Why this matters:** a version that is not bumped before its sunset fails every request on every connection. Version 1.1.25 failed `check` on all Cloud connections in October 2026 for this reason. Bump the header in every requester at least once a year and watch the sunset notices on the versioning page.

## 2. Time-bound statistics windows

`follower_statistics_time_bound`, `share_statistics_time_bound` and `page_statistics_time_bound` read statistics from 12 months ago up to 2 days before today, in UTC ([follower statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics), [share statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics), [page statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/page-statistics)). The cursor is `timeRangeEnd`, the epoch-millisecond end of the last bucket LinkedIn returned, which LinkedIn always floors to midnight UTC. LinkedIn validates the window by granularity (verified live on 2026-10-26 with version `202610`):

- `DAY`: windows shorter than 24 hours are rejected with `400 Invalid timeIntervals parameter` (airbytehq/airbyte#80199). The window ends at midnight UTC 2 days ago, so a sync that runs again on the same day requests nothing and keeps its state.
- `page_statistics_time_bound`: LinkedIn's page statistics reference does not state the 12-month and 2-day limits, so the stream reuses the follower and share windows. Live it behaves the same for `DAY` (start inclusive, end exclusive).
- Zero-length buckets: for `MONTH`, LinkedIn can append a bucket whose start equals its end at the window boundary (seen live on page and follower statistics on 2026-10-27). A record filter on all three streams drops buckets whose start is not before their end, because such a row would duplicate the next month's date.
- `MONTH`: a window that ends inside the month it starts in (for example October 1 to October 24) is rejected with `400`, while any window that ends on a month boundary is accepted. The window ends on the first day of the month that contains the day 2 days ago, so only complete months are requested and each month arrives 2 days after it ends. The first sync can still emit a partial first month when the 12-month limit or the Start Date falls inside a month.

**Why this matters:** a window computed from the wall clock or ending mid-month fails every incremental sync after the first one. Any change to `start_datetime` or `end_datetime` must keep both rules, and the unit tests in `test_incremental_window.py` pin them for both granularities.

## 3. No API budget: LinkedIn does not publish its rate limits

LinkedIn's limits are set per application and per member, per endpoint and per day, reset at midnight UTC, and are visible only in each app's Developer Portal ([rate limits](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)). Only the Development-tier ceiling is published; Standard-tier limits vary by app and endpoint, so there is no number for an `api_budget` to match and the connector has none. A `429` is retried with backoff up to `max_retries`, then the sync fails as a transient error.

**Why this matters:** an `api_budget` sized to a guessed number would either throttle every connection for nothing or fail to prevent the `429` it was meant to avoid. Daily quotas cannot be waited out within one sync, so do not raise `max_retries` to chase them.

## 4. Cursorless full-refresh streams

`organization_lookup` returns the organization's profile, and `follower_statistics`, `share_statistics`, `page_statistics` and `total_follower_count` each return one lifetime aggregate per organization. Without `timeIntervals` the statistics endpoints return lifetime totals with no time dimension, and a single profile record gains nothing from a cursor, so these streams stay full refresh. The time-bound streams call the same statistics endpoints with `timeIntervals`.

**Why this matters:** a cursor on these streams would only drop updates: the lifetime totals change in place without any field that marks the change.

## 5. Posts pagination follows LinkedIn's next link

The posts finder (`q=author`) can return fewer posts than `count` while more posts follow: LinkedIn says you may "receive less than the `count` number of results in a page, when there are more posts available in the subsequent paginated requests", and only the `next` entry in `paging.links` marks that more pages exist ([find posts by authors](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api#find-posts-by-authors)). `posts_paginator` therefore keeps requesting `start + count` until no `next` link is returned. The finder takes no time filter, so every sync pages through all posts, newest first by `lastModifiedAt`, and the client-side cursor drops posts modified before the state or the Start Date. A blank Start Date falls back to LinkedIn's launch date, 2003-05-05, not a date relative to now: the cursor also filters full-refresh syncs, so a rolling default would drop older posts from every full refresh. LinkedIn does not return deleted posts, so incremental syncs never remove them from a destination. Offsets also shift when a newer post is deleted while a sync pages through the list, which can skip one older post until the next stream refresh.

**Why this matters:** `OffsetIncrement` stops at the first short page and silently drops every later post, along with its comments and reactions. Keep the `next`-link stop condition; `test_posts_follow_the_next_link_after_a_short_page` pins it.

## 6. Comments, reactions and post statistics send requests per post on every sync

`post_comments` (`/socialActions/{post URN}/comments`) and `post_reactions` (`/reactions/(entity:{post URN})?q=entity`) are full-refresh substreams of `posts` ([comments](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/comments-api#get-comments-on-shares), [reactions](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/reactions-api#get-reactions-on-a-share)). Each sync sends at least one request per stream for every post modified since the Start Date. Only first-level comments are read; replies need a separate call per comment. The post URN is URL-encoded and the reactions key keeps its literal parentheses. A post deleted between the parent and child reads answers `404`, which `child_error_handler` ignores. Reading comments needs `r_organization_social_feed`: a live read on 2026-10-27 with a token holding only `r_organization_social` got `403` on the comments endpoint, while posts and reactions answered `200`. LinkedIn grants the `_feed` scopes with the Community Management API product, so the `403` message names both scopes.

`post_statistics` reads lifetime statistics per post from `/organizationalEntityShareStatistics` with Rest.li 2.0 list syntax: `shares=List({encoded URN})` for `urn:li:share` and `ugcPosts=List({encoded URN})` for `urn:li:ugcPost`, picked by the URN type, because the wrong parameter answers `400` ([specific shares](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics#retrieve-statistics-for-specific-shares)). LinkedIn serves no time-bound statistics for specific posts and leaves out posts with no impressions or actions, so a post without activity has no row.

The endpoints take no time filter, so a cursor would save no requests, and only a full refresh removes deleted comments and reactions from a destination. With a blank Start Date they cover every post the page has authored.

**Why this matters:** request volume grows with the post count, at least two requests per post per sync, against daily quotas that start at 500 requests per app and 100 per member on the Development tier ([increasing access](https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access)). `incremental_dependency` stays `false`: LinkedIn does not document that a new comment or reaction moves a post's `lastModifiedAt`, so re-reading only changed posts would miss activity on older ones.

## Error handling (vendor mapping)

Connector-specific mappings and the vendor pages behind them ([error handling](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/error-handling), [error responses](https://learn.microsoft.com/en-us/linkedin/marketing/error-responses)). Statuses not listed fall back to the CDK default mapping.

| Response | Handling | Reason |
| --- | --- | --- |
| `400` with `Invalid timeIntervals` on the time-bound streams | Fail, system error | The connector builds the window, so the user cannot fix it (section 2). |
| `401` | Fail, config error asking to re-authenticate | Expired or revoked access token. |
| `403` | Fail, config error naming the scopes and the `ADMINISTRATOR` role | Missing scope or role; `post_comments` needs `r_organization_social_feed` (section 6). |
| `404` on organization and statistics streams | Fail, config error naming the Organization ID | LinkedIn answers `404` for an inactive or wrong organization ([organization lookup errors](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api#api-error-details)). |
| `404` on `post_comments` and `post_reactions` | Ignore and log the URL | The post was deleted between the parent and the child read. |
| `426` | Fail, system error asking to upgrade the source | Retired `Linkedin-Version` ([example 5](https://learn.microsoft.com/en-us/linkedin/marketing/error-responses#example-5-version-header-is-deprecated)). |
| `429`, `500`, `502`, `503`, `504` | Retry up to 5 times with backoff (`Retry-After` when sent, otherwise exponential) | Daily quota or a temporary server error ([rate limits](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)). |
| `400 invalid_grant` from the token endpoint | Config error from the CDK ("Refresh token was rejected") | Expired or revoked refresh token (verified live on 2026-10-27). |

