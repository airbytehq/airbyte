# TMDb

This page contains the setup guide and reference information for the [Tmdb](https://developers.themoviedb.org/3/getting-started/introduction) source connector.

## Prerequisites

Before setting up the TMDb connector, you need to create an account on TMDb and generate an API key. The API key will identify your account and enables you to access the TMDb API endpoints. 

Follow these steps to acquire your API key:

1. Visit [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).
2. Log in or create an account.
3. Agree to the Terms of Service by checking the box.
4. Click "Generate API Key".
5. Copy the API Key (for example, `123456789`) to use later when setting up the connector.

## Setup guide

Follow the steps below to set up the TMDb connector in Airbyte.

### Step 1: Set up TMDb connection

1. In Airbyte, go to the TMDb connector configuration screen.
2. Enter your TMDb API key in the `api_key` field.
3. Enter an optional `movie_id`, `query`, and `language`.
4. Click "Check connection" to confirm the connection to TMDb.

### Step 2: Set up the TMDb connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up a source page, enter a name for the TMDb connector and select **TMDb** from the Source type dropdown.
4. Enter your TMDb API key in the `api_key` field.
5. Enter an optional `movie_id`, `query`, and `language`.
6. Click **Test** to confirm the connection to TMDb.
7. Click **Create** to save the configuration.

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Go to the **Sources** tab and click **Create a new source**.
3. On the Create a new source page, enter a name for the TMDb connector.
4. Select **TMDb** from the dropdown menu.
5. Fill in the required credentials (e.g. API key)
6. Enter an optional `movie_id`, `query`, and `language`.
7. Click **Test** to confirm the connection to TMDb.
8. Click **Create** to save the configuration.

## Supported sync modes

The TMDb source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

The following tables describe the TMDb API streams supported in this connector. Some of these streams require additional parameters (e.g. query, movie_id, language).

| Stream Name                  | Description                                        |
| :---------------------------| :--------------------------------------------------|
| Certification_movie          | A list of supported certifications for movies.     |
| Certification_tv             | A list of supported certifications for TV shows.   |
| Changes_movie               | A list of movie ids that have been edited.          |
| Changes_tv                  | A list of TV ids that have been edited.             |
| Changes_person             | A list of person ids that have been edited.         |
| Movies_alternative_titles  | A list of alternative titles for a movie.           |
| Movies_changes              | Latest modifications for a movie.                   |
| Movies_credits              | Full cast and crew for a movie.                     |
| Movies_details              | All details for a movie.                            |
| Movies_external_ids         | External IDs for a movie.                           |
| Movies_images               | All image URLs for a movie.                         |
| Movies_keywords             | List of keywords for a movie.                       |
| Movies_latest               | The most recent movie.                              |
| Movies_lists                | A list of lists that the movie belongs to.          |
| Movies_now_playing         | A list of movies playing in theatres.               |
| Movies_popular              | A list of popular movies.                           |
| Movies_recommendations      | List of recommended movies for a given movie.       |
| Movies_releases_dates       | Release dates by country for a movie.               |
| Movies_reviews              | User reviews for a movie.                           |
| Movies_similar_movies       | Similar movies for a given movie.                   |
| Movies_top_rated            | A list of top rated movies.                         |
| Movies_translations         | Translations for all text related to a movie.       |
| Movies_upcoming             | A list of upcoming movies.                          |
| Movies_videos               | Movie trailers and videos.                          |
| Movies_watch_providers      | Where to watch a movie.                             |
| Trending                    | The daily trending objects.                         |
| Search_collections          | Search for collections.                             |
| Search_companies            | Search for companies.                               |
| Search_keywords             | Search for keywords.                                |
| Search_movies               | Search for movies.                                  |
| Search_multi                | Search across multiple endpoints.                   |
| Search_people               | Search for people.                                  |
| Search_tv_shows             | Search for TV shows.                                |

## API method example

The following sample API method retrieves alternative titles for a given movie id:

```
GET https://api.themoviedb.org/3/movie/{movie_id}/alternative_titles?api_key={api_key}
```

## Performance considerations

TMDb's [API reference](https://developers.themoviedb.org/3/getting-started/introduction) uses API v3 at present and is currently developing API v4. The TMDb connector uses v3 by default.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-27 | [Init](https://github.com/airbytehq/airbyte/pull/18561)| Initial commit |