# TMDb

This page contains the setup guide and reference information for the [Tmdb](https://developers.themoviedb.org/3/getting-started/introduction.) source connector.

## Prerequisites

To use the Tmdb source connector, you will need the following:

- A Tmdb account with a generated API key.
- A `movie_id` to target specific movies (if using movie streams).
- A `query` for search streams.
- A `language` expressed in ISO 639-1 scheme for required streams.

Please follow the steps below to obtain the necessary information.

## Generate an API key

1. Log in to your Tmdb account or create one [here](https://www.themoviedb.org/signup).
2. Navigate to your **Account Settings**.
3. Select **API** from the left-hand menu.
4. Under **Create API Key**, provide a brief description of your project in the **Description** field.
5. Click on **Generate API Key**.

Your API key will now be generated and displayed on the page. Copy it for use in the next step.

## Set up TMDb connection in Airbyte

Follow the steps below to set up the Tmdb connector in Airbyte:

1. Log in to your Airbyte account.
2. Navigate to the **Sources** tab and click on **+ New Source** in the top right corner.
3. On the **Set up a new source** page, enter a name for the connector and select **TMDb** as the **Source Type**.
4. In the **Configuration** section, enter the following data:
   - `api_key`: The API key generated in the first section.
   - `movie_id`: (Optional) Target movie ID for movie streams.
   - `query`: (Optional) Query for search streams.
   - `language`: (Optional) Language for filtering.
5. Click on **Test** to verify the connection.
6. Click on **Create** to save the connection.

You have now successfully set up the Tmdb connector in Airbyte.

## Supported sync modes

The Tmdb source connector supports the following [sync modes](https://docs.airbyte.io/integrations/sources/tmdb):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

The Tmdb source connector supports the following streams:

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
- Movies_recommendations
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

The following API method retrieves the alternative titles for a movie:

```
GET https://api.themoviedb.org/3/movie/{movie_id}/alternative_titles?api_key={api_key}
```

Please refer to the [Tmdb API reference](https://developers.themoviedb.org/3/getting-started/introduction) for further examples.

## Performance considerations

Tmdb's API reference has version 3 (v3) at present, and version 4 (v4) is currently under development. The connector currently uses v3 by default.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-27 | [Init](https://github.com/airbytehq/airbyte/pull/18561)| Initial commit |

For more information on how to set up Airbyte connectors, please refer to the [Airbyte documentation](https://docs.airbyte.io/).