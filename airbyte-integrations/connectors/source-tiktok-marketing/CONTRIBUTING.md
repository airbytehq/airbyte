# Contributing to source-tiktok-marketing

See the [Airbyte contribution guide](https://docs.airbyte.com/contributing-to-airbyte).
For implementation details and cautions, read [AGENTS.md](AGENTS.md).

Live tests use a production TikTok Ads advertiser. Sandbox authentication is no longer supported.

## Unique behaviors (summary)

## 1. Dual Advertiser ID Partition Routers

An optional advertiser ID limits a sync to one advertiser. Otherwise, the connector reads all accessible advertisers, batching advertiser details while reading other streams one advertiser at a time.

## 2. Empty Metric Values Returned as Dash Strings

TikTok represents missing report metrics with a dash. The connector converts these values to null so destinations receive consistent metric types.

## 3. Rate Limit Detection via Response Body Code

TikTok reports rate limits and some transient errors inside successful HTTP responses. The connector checks the API error code to decide whether to retry or fail.

## 4. Daily Report Window Splitting (40067)

When TikTok rejects an oversized daily report request, the connector splits the date window and retries. Hourly reports retain their one-day windows.

## 5. Smart+ Ads Missing modify_time Filter

Ads without a modification time are omitted because that field is required for incremental syncing. This can exclude Smart+ ads from the output.
