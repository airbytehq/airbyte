# YouTube Data API

<HideInUI>

This page contains the setup guide and reference information for the [YouTube Data API](https://developers.google.com/youtube/v3) source connector.

</HideInUI>

This connector uses the [YouTube Data API v3](https://developers.google.com/youtube/v3) to sync data about your YouTube channels, including video details, channel metadata, and comments. For more detailed analytics and reporting data, use the [YouTube Analytics connector](https://docs.airbyte.com/integrations/sources/youtube-analytics).

## Prerequisites

- One or more YouTube Channel IDs you want to sync data from
<!-- env:oss -->
- (For Airbyte Open Source) A Google Cloud project with the YouTube Data API v3 enabled, and one of the following authentication methods from that project:
  - A Google API Key (public data only)
  - OAuth 2.0 credentials (Client ID, Client Secret, and Refresh Token)
<!-- /env:oss -->

## Setup guide

### Find your YouTube Channel IDs

1. Go to [YouTube](https://www.youtube.com/) and navigate to the channel you want to sync.
2. The Channel ID is in the URL: `https://www.youtube.com/channel/CHANNEL_ID`. Channel IDs start with `UC`. A handle URL such as `https://www.youtube.com/@handle` isn't a Channel ID.
3. Alternatively, you can find it in YouTube Studio under **Settings** > **Channel** > **Advanced settings**.

The connector fails the connection check if any Channel ID doesn't resolve to an existing channel, so verify each ID before you set up the source.

<!-- env:cloud -->

### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. Select **YouTube Data API** from the list.
4. Enter a name for your source.
5. Choose your authentication method:
   - For **OAuth 2.0**: Click **Sign in with Google** to authenticate your Google account.
   - For **API Key**: Enter your Google API key.
6. Enter one or more Channel IDs to sync data from.
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source

#### Create credentials

You can authenticate using either an API Key or OAuth 2.0.

**Option A: API Key (simpler setup, public data only)**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services** > **Library** and enable the YouTube Data API v3.
4. Go to **APIs & Services** > **Credentials**.
5. Click **Create Credentials** > **API key**.
6. Copy the generated API key.
7. (Recommended) Click **Restrict key** to limit the key's usage to the YouTube Data API v3.

**Option B: OAuth 2.0 (required for accessing private data)**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services** > **Library** and enable the YouTube Data API v3.
4. Go to **APIs & Services** > **Credentials**.
5. Click **Create Credentials** > **OAuth client ID**.
6. Configure the OAuth consent screen if prompted.
7. Copy the **Client ID** and **Client Secret**.
8. Use these credentials to obtain a refresh token. Refer to [Google's OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2) for detailed instructions.

#### Set up the connector

1. In Airbyte, go to **Sources** and click **+ New source**.
2. Select **YouTube Data API** from the list.
3. Enter a name for your source.
4. Choose your authentication method and enter the required credentials.
5. Enter one or more Channel IDs to sync data from.
6. Click **Set up source**.

<!-- /env:oss -->

## Supported sync modes

The YouTube Data API source connector supports the following sync modes:

- [Full Refresh - Overwrite](/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)

No stream supports incremental sync. Each sync re-reads all data for the configured channels, so the quota and pacing behavior described in [Limitations and considerations](#limitations-and-considerations) applies to every sync. If you use Full Refresh - Append, `video` and `channels` records differ between syncs because YouTube updates their statistics (view, like, comment, and subscriber counts) in place; deduplicate on the primary key in your destination if you only want the latest values.

## Supported streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
| --- | --- | --- | --- | --- |
| video | videoId | DefaultPaginator | Yes | No |
| videos | videoId | DefaultPaginator | Yes | No |
| channels | id | DefaultPaginator | Yes | No |
| comments | videoId, id | DefaultPaginator | Yes | No |
| channel_comments | channelId, id | DefaultPaginator | Yes | No |

### Stream descriptions

- **video**: Detailed information about videos from the specified channels, from [`videos.list`](https://developers.google.com/youtube/v3/docs/videos/list). This stream uses the `videos` parent stream to first discover video IDs, then fetches full video details for each. Data includes snippet information (title, description, thumbnails, publish date, tags, category, language settings), content details (duration, dimension, definition, caption availability, region restrictions), statistics (view count, like count, comment count), player information (embed HTML), and status (upload status, privacy status, license, embeddable, made for kids). Each record also includes a `datetime` field that the connector sets to the time it fetched the record. It isn't a YouTube timestamp; use it to tell snapshots apart in Full Refresh - Append mode.
- **videos**: The IDs of videos published by the specified channels, discovered with [`search.list`](https://developers.google.com/youtube/v3/docs/search/list) filtered to `type=video`. Each record contains only the search result's `id` object: `kind` (always `youtube#video`) and `videoId`, which is the primary key. The `video` and `comments` streams use this stream as their parent to identify which videos to fetch. YouTube returns at most 500 results per channel from this search, so channels with more than 500 videos are truncated in `videos`, `video`, and `comments`.
- **channels**: Information about the specified YouTube channels, from [`channels.list`](https://developers.google.com/youtube/v3/docs/channels/list). Data includes snippet information (title, description, custom URL, country, thumbnails), content details (related playlists), statistics (subscriber count, view count, video count), branding settings (channel keywords, trailer, default language), topic details (topic categories), status (privacy status, made for kids), localizations, and content owner details.
- **comments**: Comment threads on individual videos from the specified channels, from [`commentThreads.list`](https://developers.google.com/youtube/v3/docs/commentThreads/list) filtered by `videoId`. For each video discovered by the `videos` stream, this stream fetches the comment threads. Each record is one thread's `snippet`: the top-level comment is in `topLevelComment`, `totalReplyCount` gives the number of replies, and the connector copies the top-level comment's ID into a top-level `id` field to serve as part of the primary key. The replies themselves aren't included in the records. Videos with comments disabled and videos that no longer exist are skipped without failing the sync.
- **channel_comments**: All comment threads related to the specified channels, from `commentThreads.list` filtered by `allThreadsRelatedToChannelId`. This includes comments on the channel's videos and on the channel page itself, so it provides a broader view of channel engagement than the `comments` stream. Because it doesn't depend on the `videos` search, it isn't subject to the 500-video limit. Records have the same shape as `comments`, including the copied `id` field.

Comment records carry `publishedAt` and `updatedAt` timestamps only inside the nested `topLevelComment.snippet` object; there's no top-level timestamp field.

## YouTube API Services usage disclosure

This connector uses [YouTube API Services](https://developers.google.com/youtube/v3) to retrieve data from YouTube. By using this connector, you agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms).

YouTube API Services are provided by Google. For information about how Google handles data, review the [Google Privacy Policy](https://www.google.com/policies/privacy).

When using OAuth 2.0 authentication, this connector accesses authorized user data. You can revoke the connector's access to your Google account at any time through the [Google security settings page](https://myaccount.google.com/connections?filters=3,4&hl=en). To delete stored data that was previously synced, remove the relevant connection in your Airbyte workspace or delete the data from your configured destination.

## Limitations and considerations

### Quota and sync duration

The YouTube Data API enforces a daily [quota](https://developers.google.com/youtube/v3/getting-started#quota) per Google Cloud project. Google's documented default allocation is 100 `search.list` calls per day plus 10,000 quota units per day for all other endpoints; `channels.list`, `videos.list`, and `commentThreads.list` each cost 1 unit per request. Google notes that defaults are subject to change, and older projects may still have a single 10,000-unit pool in which each `search.list` call costs 100 units. Check the **Quotas** page for the YouTube Data API in the Google Cloud console to see what applies to your project. If you need more, [request a quota extension](https://support.google.com/youtube/contact/yt_api_form) from Google.

To stay within the default quota, the connector paces its own requests:

- At most 3 `search.list` requests per hour. The `videos` stream, and therefore the `video` and `comments` streams that depend on it, uses this endpoint. Each request returns up to 50 video IDs, so a channel with 500 videos needs 10 search requests and several hours of wall-clock time to enumerate.
- At most 90 requests per hour combined to the `channels`, `videos`, and `commentThreads` endpoints.

Because of this pacing, syncs for channels with many videos or comments take hours rather than minutes. This is expected, and the connector keeps the sync alive while it waits. If YouTube still returns a quota or rate-limit error (`quotaExceeded`, `dailyLimitExceeded`, `rateLimitExceeded`, `userRateLimitExceeded`, or HTTP 429), the connector retries with backoff instead of failing. Google resets the daily quota at midnight Pacific Time.

The pacing above applies to each Airbyte source separately, but Google meters quota per Google Cloud project. If several sources use API keys or OAuth clients from the same project, their requests add up against one quota and the pacing no longer guarantees you stay under it. Use a separate project for each source, or request more quota.

### Authentication

- API keys can only access public data. To access private data, you must use OAuth 2.0 authentication.
- When using OAuth 2.0, the connector requests the `youtube.force-ssl` scope, which provides read and write access to YouTube resources. This scope is required even though the connector only reads data.
- The connector does not support service account authentication because the YouTube Data API does not support this method for most operations.
- The connector fails with a configuration error, rather than retrying, when YouTube reports that the API key is invalid, the OAuth token is expired or revoked, the token lacks the `youtube.force-ssl` scope, the YouTube Data API v3 isn't enabled for the project, or a configured Channel ID doesn't exist. Fix the credentials or Channel IDs and run the sync again.

### Data coverage

- The `videos` stream returns at most 500 videos per channel because of a YouTube `search.list` limit. Channels with more videos are truncated in `videos`, `video`, and `comments`. `channels` and `channel_comments` aren't affected.
- The `comments` stream skips videos with comments disabled and deleted videos without producing records or errors.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 1.0.0 | 2026-09-10 | [85214](https://github.com/airbytehq/airbyte/pull/85214) | Breaking: promote connector to certified — declare primary keys and timestamp formats and restrict `videos` to video results (see the [migration guide](/integrations/sources/youtube-data-migrations)) |
| 0.0.66 | 2026-09-08 | [85721](https://github.com/airbytehq/airbyte/pull/85721) | Update dependencies |
| 0.0.65 | 2026-08-18 | [84813](https://github.com/airbytehq/airbyte/pull/84813) | Update dependencies |
| 0.0.64 | 2026-08-11 | [84181](https://github.com/airbytehq/airbyte/pull/84181) | Update dependencies |
| 0.0.63 | 2026-08-04 | [83693](https://github.com/airbytehq/airbyte/pull/83693) | Update dependencies |
| 0.0.62 | 2026-07-28 | [83186](https://github.com/airbytehq/airbyte/pull/83186) | Update dependencies |
| 0.0.61 | 2026-07-21 | [82663](https://github.com/airbytehq/airbyte/pull/82663) | Update dependencies |
| 0.0.60 | 2026-07-14 | [82070](https://github.com/airbytehq/airbyte/pull/82070) | Update dependencies |
| 0.0.59 | 2026-06-30 | [81317](https://github.com/airbytehq/airbyte/pull/81317) | Update dependencies |
| 0.0.58 | 2026-06-23 | [80730](https://github.com/airbytehq/airbyte/pull/80730) | Update dependencies |
| 0.0.57 | 2026-06-16 | [80123](https://github.com/airbytehq/airbyte/pull/80123) | Update dependencies |
| 0.0.56 | 2026-06-09 | [79580](https://github.com/airbytehq/airbyte/pull/79580) | Update dependencies |
| 0.0.55 | 2026-06-02 | [79000](https://github.com/airbytehq/airbyte/pull/79000) | Update dependencies |
| 0.0.54 | 2026-04-28 | [77496](https://github.com/airbytehq/airbyte/pull/77496) | Update dependencies |
| 0.0.53 | 2026-04-21 | [76818](https://github.com/airbytehq/airbyte/pull/76818) | Update dependencies |
| 0.0.52 | 2026-04-08 | [75185](https://github.com/airbytehq/airbyte/pull/75185) | Replace connector icon with updated YouTube logo |
| 0.0.51 | 2026-03-17 | [74392](https://github.com/airbytehq/airbyte/pull/74392) | Migrate to scopes object array format |
| 0.0.50 | 2026-03-17 | [74698](https://github.com/airbytehq/airbyte/pull/74698) | Update dependencies |
| 0.0.49 | 2026-03-03 | [73914](https://github.com/airbytehq/airbyte/pull/73914) | Update dependencies |
| 0.0.48 | 2026-02-17 | [73507](https://github.com/airbytehq/airbyte/pull/73507) | Update dependencies |
| 0.0.47 | 2026-02-10 | [73175](https://github.com/airbytehq/airbyte/pull/73175) | Update dependencies |
| 0.0.46 | 2026-01-27 | [72066](https://github.com/airbytehq/airbyte/pull/72066) | Update dependencies |
| 0.0.45 | 2026-01-14 | [70677](https://github.com/airbytehq/airbyte/pull/70677) | Update dependencies |
| 0.0.44 | 2026-01-05 | [71016](https://github.com/airbytehq/airbyte/pull/71016) | Fixed schemas |
| 0.0.43 | 2025-12-19 | [70971](https://github.com/airbytehq/airbyte/pull/70971) | Add acceptance tests |
| 0.0.42 | 2025-12-16 | [69315](https://github.com/airbytehq/airbyte/pull/69315) | Add OAuth 2.0 support |
| 0.0.41 | 2025-11-25 | [70079](https://github.com/airbytehq/airbyte/pull/70079) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69532](https://github.com/airbytehq/airbyte/pull/69532) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68942](https://github.com/airbytehq/airbyte/pull/68942) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68456](https://github.com/airbytehq/airbyte/pull/68456) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67987](https://github.com/airbytehq/airbyte/pull/67987) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67241](https://github.com/airbytehq/airbyte/pull/67241) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66846](https://github.com/airbytehq/airbyte/pull/66846) | Update dependencies |
| 0.0.34 | 2025-09-24 | [66475](https://github.com/airbytehq/airbyte/pull/66475) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65731](https://github.com/airbytehq/airbyte/pull/65731) | Update dependencies |
| 0.0.32 | 2025-08-24 | [65468](https://github.com/airbytehq/airbyte/pull/65468) | Update dependencies |
| 0.0.31 | 2025-08-10 | [64863](https://github.com/airbytehq/airbyte/pull/64863) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64386](https://github.com/airbytehq/airbyte/pull/64386) | Update dependencies |
| 0.0.29 | 2025-07-26 | [64056](https://github.com/airbytehq/airbyte/pull/64056) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63640](https://github.com/airbytehq/airbyte/pull/63640) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63216](https://github.com/airbytehq/airbyte/pull/63216) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62701](https://github.com/airbytehq/airbyte/pull/62701) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62233](https://github.com/airbytehq/airbyte/pull/62233) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61759](https://github.com/airbytehq/airbyte/pull/61759) | Update dependencies |
| 0.0.23 | 2025-06-15 | [61171](https://github.com/airbytehq/airbyte/pull/61171) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60786](https://github.com/airbytehq/airbyte/pull/60786) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59968](https://github.com/airbytehq/airbyte/pull/59968) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59566](https://github.com/airbytehq/airbyte/pull/59566) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58930](https://github.com/airbytehq/airbyte/pull/58930) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58550](https://github.com/airbytehq/airbyte/pull/58550) | Update dependencies |
| 0.0.17 | 2025-04-13 | [58052](https://github.com/airbytehq/airbyte/pull/58052) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57379](https://github.com/airbytehq/airbyte/pull/57379) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56821](https://github.com/airbytehq/airbyte/pull/56821) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56338](https://github.com/airbytehq/airbyte/pull/56338) | Update dependencies |
| 0.0.13 | 2025-03-09 | [55664](https://github.com/airbytehq/airbyte/pull/55664) | Update dependencies |
| 0.0.12 | 2025-03-01 | [55162](https://github.com/airbytehq/airbyte/pull/55162) | Update dependencies |
| 0.0.11 | 2025-02-23 | [54632](https://github.com/airbytehq/airbyte/pull/54632) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53087](https://github.com/airbytehq/airbyte/pull/53087) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52387](https://github.com/airbytehq/airbyte/pull/52387) | Update dependencies |
| 0.0.8 | 2025-01-18 | [52006](https://github.com/airbytehq/airbyte/pull/52006) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51380](https://github.com/airbytehq/airbyte/pull/51380) | Update dependencies |
| 0.0.6 | 2025-01-04 | [50753](https://github.com/airbytehq/airbyte/pull/50753) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50326](https://github.com/airbytehq/airbyte/pull/50326) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49756](https://github.com/airbytehq/airbyte/pull/49756) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49403](https://github.com/airbytehq/airbyte/pull/49403) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49125](https://github.com/airbytehq/airbyte/pull/49125) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1   | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder                                                                                      |

</details>
