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

| Version | Date       | Pull Request                                            | Subject        |
| :------ | :--------- | :------------------------------------------------------ | :------------- |
| 0.1.0   | 2022-10-27 | [Init](https://github.com/airbytehq/airbyte/pull/18561) | Initial commit |
