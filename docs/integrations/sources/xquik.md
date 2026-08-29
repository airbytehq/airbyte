# Xquik

The Xquik source replicates public X data into a destination supported by Airbyte. It supports Twitter advanced search queries, public user profiles, user timelines, and regional trends.

## Prerequisites

- An Xquik account with available credits.
- An API key created through the [Xquik authentication guide](https://docs.xquik.com/api-reference/authentication).

Store the API key as a secret. The connector sends it only in the `x-api-key` request header.

## Supported Streams

| Stream | Primary Key | Sync Mode | API Reference |
|--------|-------------|-----------|---------------|
| `tweets_search` | `id`, `search_query` | Full refresh, incremental | [Search tweets](https://docs.xquik.com/api-reference/x/search-tweets) |
| `user_profiles` | `id` | Full refresh | [Profile lookup](https://docs.xquik.com/api-reference/x/twitter-profile-lookup) |
| `user_tweets` | `id`, `source_username` | Full refresh | [User tweets](https://docs.xquik.com/api-reference/x/user-tweets) |
| `trends` | `woeid`, `name` | Full refresh | [Trends](https://docs.xquik.com/api-reference/x/trends) |

The `tweets_search` stream stores incremental state per search query. It sends `sinceTime` and `untilTime` on each sync and follows cursor pagination until the API reports no next page. Other streams follow cursor pagination where the API provides it.

## Setup

1. Open **Sources** in Airbyte.
2. Select **Xquik**.
3. Enter your Xquik API key.
4. Set an ISO 8601 UTC start date, such as `2026-01-01T00:00:00Z`.
5. Add at least one search query.
6. Optionally add usernames, user IDs, or regional WOEIDs.
7. Test and save the source.

Usernames must omit the leading `@`. The default WOEID `1` represents worldwide trends.

## Search Queries

Each configured query creates an independent partition and incremental cursor. Use X search operators to narrow the replicated dataset. Examples include:

- `"open source" lang:en`
- `from:airbytehq`
- `#dataengineering min_faves:100`

See the [search tweets API reference](https://docs.xquik.com/api-reference/x/search-tweets) for supported operators and request behavior.

## Usage Considerations

Xquik API reads consume account credits. Start with narrow queries, a recent start date, and conservative limits. Expand the source after validating destination volume. The API may return fewer rows than the configured limit.

When a cursor becomes unavailable, Xquik can require a fresh pagination run. Airbyte preserves the latest completed incremental state. Select a deduplicating destination sync mode to deduplicate records by the configured primary key.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-08-18 |  | Initial release |

</details>
