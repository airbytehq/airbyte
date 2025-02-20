# TMDb

This page contains the setup guide and reference information for the [Tmdb](https://developers.themoviedb.org/3/getting-started/introduction.) source connector.

## Prerequisites

Api key and movie ID is mandate for this connector to work, It could be generated using a free account at TMDb. Visit: https://www.themoviedb.org/settings/api
Just pass the generated API key and Movie ID for establishing the connection.

## Setup guide

### Step 1: Set up TMDb connection

- Generate an API key (Example: 12345)
- Give a Movie ID, Query, Language (Target Movie, Query for search, Language filter)

## Step 2: Set up the TMDb connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Google-webfonts connector and select **TMDb** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter params `movie_id, query, language` (if needed).
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter params `movie_id, query, language` (if needed).
5. Click **Set up source**.

## Supported sync modes

The Google-webfonts source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- Certification_movie
- Certification_tv
- Changes_movie
- Changes_tv
- Changes_person
- Movies_alternative_titles
- Movies_changes
- Movies_credits
- Movies_details
- Movies_external_ids
- Movies_images
- Movies_keywords
- Movies_latest
- Movies_lists
- Movies_now_playing
- Movies_popular
- Movies_recommentations
- Movies_releases_dates
- Movies_reviews
- Movies_similar_movies
- Movies_top_rated
- Movies_translations
- Movies_upcoming
- Movies_videos
- Movies_watch_providers
- Trending
- Search_collections
- Search_companies
- Search_keywords
- Search_movies
- Search_multi
- Search_people
- Search_tv_shows

## API method example

GET https://api.themoviedb.org/3/movie/{movie_id}/alternative_titles?api_key={api_key}

## Performance considerations

TMDb's [API reference](https://developers.themoviedb.org/3/getting-started/introduction) has v3 at present and v4 is at development. The connector as default uses v3.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 1.1.12 | 2025-02-15 | [54032](https://github.com/airbytehq/airbyte/pull/54032) | Update dependencies |
| 1.1.11 | 2025-02-08 | [53550](https://github.com/airbytehq/airbyte/pull/53550) | Update dependencies |
| 1.1.10 | 2025-02-01 | [53097](https://github.com/airbytehq/airbyte/pull/53097) | Update dependencies |
| 1.1.9 | 2025-01-25 | [52460](https://github.com/airbytehq/airbyte/pull/52460) | Update dependencies |
| 1.1.8 | 2025-01-18 | [51982](https://github.com/airbytehq/airbyte/pull/51982) | Update dependencies |
| 1.1.7 | 2025-01-11 | [51419](https://github.com/airbytehq/airbyte/pull/51419) | Update dependencies |
| 1.1.6 | 2024-12-28 | [50778](https://github.com/airbytehq/airbyte/pull/50778) | Update dependencies |
| 1.1.5 | 2024-12-21 | [50323](https://github.com/airbytehq/airbyte/pull/50323) | Update dependencies |
| 1.1.4 | 2024-12-14 | [49800](https://github.com/airbytehq/airbyte/pull/49800) | Update dependencies |
| 1.1.3 | 2024-12-12 | [47938](https://github.com/airbytehq/airbyte/pull/47938) | Update dependencies |
| 1.1.2 | 2024-10-28 | [47676](https://github.com/airbytehq/airbyte/pull/47676) | Update dependencies |
| 1.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.1.0 | 2024-08-14 | [44057](https://github.com/airbytehq/airbyte/pull/44057) | Refactor connector to manifest-only format |
| 1.0.5 | 2024-08-12 | [43816](https://github.com/airbytehq/airbyte/pull/43816) | Update dependencies |
| 1.0.4 | 2024-08-10 | [43650](https://github.com/airbytehq/airbyte/pull/43650) | Update dependencies |
| 1.0.3 | 2024-08-03 | [43259](https://github.com/airbytehq/airbyte/pull/43259) | Update dependencies |
| 1.0.2 | 2024-07-27 | [42811](https://github.com/airbytehq/airbyte/pull/42811) | Update dependencies |
| 1.0.1 | 2024-07-20 | [42257](https://github.com/airbytehq/airbyte/pull/42257) | Update dependencies |
| 1.0.0 | 2024-07-15 | [39109](https://github.com/airbytehq/airbyte/pull/39109) | Make compatible with builder, fix schema |
| 0.1.7 | 2024-07-13 | [41511](https://github.com/airbytehq/airbyte/pull/41511) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41181](https://github.com/airbytehq/airbyte/pull/41181) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40959](https://github.com/airbytehq/airbyte/pull/40959) | Update dependencies |
| 0.1.4 | 2024-06-26 | [40273](https://github.com/airbytehq/airbyte/pull/40273) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40095](https://github.com/airbytehq/airbyte/pull/40095) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39305](https://github.com/airbytehq/airbyte/pull/39305) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38496](https://github.com/airbytehq/airbyte/pull/38496) | [autopull] base image + poetry + up_to_date |
|  0.1.0  | 2022-10-27 | [Init](https://github.com/airbytehq/airbyte/pull/18561)  | Initial commit |

</details>
