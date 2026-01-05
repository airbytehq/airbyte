# YouTube Data API

<HideInUI>

This page contains the setup guide and reference information for the [YouTube Data API](https://developers.google.com/youtube/v3) source connector.

</HideInUI>

The YouTube Data API v3 provides access to YouTube data, such as videos, playlists, channels, comments, and simple stats. This connector is a simpler version of the YouTube connector. If you need more detailed reports from your channel, use the [YouTube Analytics Connector](https://docs.airbyte.com/integrations/sources/youtube-analytics).

## Prerequisites

- One or more YouTube Channel IDs you want to sync data from
<!-- env:oss -->
- (For Airbyte Open Source) One of the following authentication methods:
  - A Google API Key with the YouTube Data API v3 enabled
  - OAuth 2.0 credentials (Client ID, Client Secret, and Refresh Token)
<!-- /env:oss -->

## Setup guide

### Find your YouTube Channel IDs

1. Go to [YouTube](https://www.youtube.com/) and navigate to the channel you want to sync.
2. The Channel ID is in the URL: `https://www.youtube.com/channel/CHANNEL_ID`.
3. Alternatively, you can find it in YouTube Studio under **Settings** > **Channel** > **Advanced settings**.

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

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| video | videoId | DefaultPaginator | Yes | No |
| videos | | DefaultPaginator | Yes | No |
| channels | id | DefaultPaginator | Yes | No |
| comments | | DefaultPaginator | Yes | No |
| channel_comments | | DefaultPaginator | Yes | No |

### Stream descriptions

- **video**: Detailed information about videos from the specified channels. This stream uses the `videos` parent stream to first discover video IDs, then fetches full video details for each. Data includes snippet information (title, description, thumbnails, publish date, tags, category, language settings), content details (duration, dimension, definition, caption availability, region restrictions), statistics (view count, like count, comment count), player information (embed HTML), and status (upload status, privacy status, license, embeddable, made for kids).
- **videos**: A list of video IDs discovered by searching the specified channels. This stream is used internally by the `video` and `comments` streams to identify which videos to fetch data for.
- **channels**: Information about the specified YouTube channels. Data includes snippet information (title, description, custom URL, country, thumbnails), content details (related playlists), statistics (subscriber count, view count, video count), branding settings (channel keywords, trailer, default language), topic details (topic categories), status (privacy status, made for kids), localizations, and content owner details.
- **comments**: Comment threads on individual videos from the specified channels. For each video discovered in the channel, this stream fetches the top-level comments and their replies.
- **channel_comments**: All comment threads related to the specified channels, including comments on the channel's videos and comments that mention the channel. This provides a broader view of channel engagement than the `comments` stream.

## Limitations and considerations

- The YouTube Data API has [quota limits](https://developers.google.com/youtube/v3/getting-started#quota). Each API request costs a certain number of quota units, and the default quota is 10,000 units per day. The search endpoint used by the `videos` stream has a higher quota cost (100 units per request) compared to other endpoints.
- API keys can only access public data. To access private data, you must use OAuth 2.0 authentication.
- When using OAuth 2.0, the connector requests the `youtube.force-ssl` scope, which provides read and write access to YouTube resources. This scope is required even though the connector only reads data.
- The connector does not support service account authentication because the YouTube Data API does not support this method for most operations.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                                                                                                                |
|---------|------------|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.0.44  | 2025-12-17 | [71016](https://github.com/airbytehq/airbyte/pull/71016) | Fixed schemas |
| 0.0.43  | 2025-12-17 | [70971](https://github.com/airbytehq/airbyte/pull/70971) | Add acceptance tests |
| 0.0.42  | 2025-11-23 | [69315](https://github.com/airbytehq/airbyte/pull/69315) | Add OAuth 2.0 support                                                                                                                       |
| 0.0.41  | 2025-11-25 | [70079](https://github.com/airbytehq/airbyte/pull/70079) | Update dependencies|
| 0.0.40  | 2025-11-18 | [69532](https://github.com/airbytehq/airbyte/pull/69532) | Update dependencies|
| 0.0.39  | 2025-10-29 | [68942](https://github.com/airbytehq/airbyte/pull/68942) | Update dependencies|
| 0.0.38  | 2025-10-21 | [68456](https://github.com/airbytehq/airbyte/pull/68456) | Update dependencies|
| 0.0.37  | 2025-10-14 | [67987](https://github.com/airbytehq/airbyte/pull/67987) | Update dependencies|
| 0.0.36  | 2025-10-07 | [67241](https://github.com/airbytehq/airbyte/pull/67241) | Update dependencies|
| 0.0.35  | 2025-09-30 | [66846](https://github.com/airbytehq/airbyte/pull/66846) | Update dependencies|
| 0.0.34  | 2025-09-24 | [66475](https://github.com/airbytehq/airbyte/pull/66475) | Update dependencies|
| 0.0.33  | 2025-09-09 | [65731](https://github.com/airbytehq/airbyte/pull/65731) | Update dependencies|
| 0.0.32  | 2025-08-24 | [65468](https://github.com/airbytehq/airbyte/pull/65468) | Update dependencies|
| 0.0.31  | 2025-08-09 | [64863](https://github.com/airbytehq/airbyte/pull/64863) | Update dependencies|
| 0.0.30  | 2025-08-02 | [64386](https://github.com/airbytehq/airbyte/pull/64386) | Update dependencies|
| 0.0.29  | 2025-07-26 | [64056](https://github.com/airbytehq/airbyte/pull/64056) | Update dependencies|
| 0.0.28  | 2025-07-19 | [63640](https://github.com/airbytehq/airbyte/pull/63640) | Update dependencies|
| 0.0.27  | 2025-07-12 | [63216](https://github.com/airbytehq/airbyte/pull/63216) | Update dependencies|
| 0.0.26  | 2025-07-05 | [62701](https://github.com/airbytehq/airbyte/pull/62701) | Update dependencies|
| 0.0.25  | 2025-06-28 | [62233](https://github.com/airbytehq/airbyte/pull/62233) | Update dependencies|
| 0.0.24  | 2025-06-21 | [61759](https://github.com/airbytehq/airbyte/pull/61759) | Update dependencies|
| 0.0.23  | 2025-06-15 | [61171](https://github.com/airbytehq/airbyte/pull/61171) | Update dependencies|
| 0.0.22  | 2025-05-24 | [60786](https://github.com/airbytehq/airbyte/pull/60786) | Update dependencies|
| 0.0.21  | 2025-05-10 | [59968](https://github.com/airbytehq/airbyte/pull/59968) | Update dependencies|
| 0.0.20  | 2025-05-04 | [59566](https://github.com/airbytehq/airbyte/pull/59566) | Update dependencies|
| 0.0.19  | 2025-04-26 | [58930](https://github.com/airbytehq/airbyte/pull/58930) | Update dependencies|
| 0.0.18  | 2025-04-19 | [58550](https://github.com/airbytehq/airbyte/pull/58550) | Update dependencies|
| 0.0.17  | 2025-04-13 | [58052](https://github.com/airbytehq/airbyte/pull/58052) | Update dependencies|
| 0.0.16  | 2025-04-05 | [57379](https://github.com/airbytehq/airbyte/pull/57379) | Update dependencies|
| 0.0.15  | 2025-03-29 | [56821](https://github.com/airbytehq/airbyte/pull/56821) | Update dependencies|
| 0.0.14  | 2025-03-22 | [56338](https://github.com/airbytehq/airbyte/pull/56338) | Update dependencies|
| 0.0.13  | 2025-03-09 | [55664](https://github.com/airbytehq/airbyte/pull/55664) | Update dependencies|
| 0.0.12  | 2025-03-01 | [55162](https://github.com/airbytehq/airbyte/pull/55162) | Update dependencies|
| 0.0.11  | 2025-02-23 | [54632](https://github.com/airbytehq/airbyte/pull/54632) | Update dependencies|
| 0.0.10  | 2025-02-15 | [53087](https://github.com/airbytehq/airbyte/pull/53087) | Update dependencies|
| 0.0.9   | 2025-01-25 | [52387](https://github.com/airbytehq/airbyte/pull/52387) | Update dependencies|
| 0.0.8   | 2025-01-18 | [52006](https://github.com/airbytehq/airbyte/pull/52006) | Update dependencies|
| 0.0.7   | 2025-01-11 | [51380](https://github.com/airbytehq/airbyte/pull/51380) | Update dependencies|
| 0.0.6   | 2025-01-04 | [50753](https://github.com/airbytehq/airbyte/pull/50753) | Update dependencies|
| 0.0.5   | 2024-12-21 | [50326](https://github.com/airbytehq/airbyte/pull/50326) | Update dependencies|
| 0.0.4   | 2024-12-14 | [49756](https://github.com/airbytehq/airbyte/pull/49756) | Update dependencies|
| 0.0.3   | 2024-12-12 | [49403](https://github.com/airbytehq/airbyte/pull/49403) | Update dependencies|
| 0.0.2   | 2024-12-11 | [49125](https://github.com/airbytehq/airbyte/pull/49125) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1   | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder                                                                                      |

</details>
