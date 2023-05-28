# TMDb

This page contains the setup guide and reference information for the [Tmdb](https://developers.themoviedb.org/3/getting-started/introduction.) source connector.

## Prerequisites

Api key and movie ID is mandate for this connector to work, It could be generated using a free account at TMDb. Visit: https://www.themoviedb.org/settings/api
Just pass the generated API key and Movie ID for establishing the connection.

## Setup Guide

### Step 1: Register for a TMDb account

To obtain an API key, you'll need a TMDb account. Visit [TMDb's website](https://www.themoviedb.org/signup) to sign up if you don't have an account yet.

### Step 2: Generate an API key

1. Log in to your TMDb account.
2. Navigate to your [TMDb settings page](https://www.themoviedb.org/settings/api).
3. Click the "Create" button on the API "Request an API Key" section.
4. Choose either "Developer" or "Private" for your API key depending on your use case, and fill in the required information.
5. After submitting the form, you'll receive an email from TMDb to confirm your email address. Click the link provided to confirm.
6. Upon confirmation, navigate back to the [API settings page](https://www.themoviedb.org/settings/api), and you should now see your API Key (v3 auth) under the "API Key" section. Copy this key, as you will need it for setting up the Airbyte connector.

### Step 3: Determine Movie ID, Query, and Language parameters

1. To find the Movie ID, search for a movie on the [TMDb website](https://www.themoviedb.org/). The movie ID is the numeric value in the URL after `/movie/`. For example, the URL https://www.themoviedb.org/movie/550 refers to the movie with ID `550`.
2. For the Query parameter, decide on a search term that best targets the movie or set of movies you want to obtain data for. For example, you can use `Marvel` for Marvel movies or `DC` for DC movies.
3. For the Language parameter, choose an appropriate language code using the [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code scheme. For example, use `en-US` for English (US) or `es-ES` for Spanish (Spain).

### Step 4: Configure the TMDb Source connector in Airbyte

1. In the TMDb Source connector settings, enter the API key obtained in Step 2 into the "Unique key for establishing connection" field.
2. Enter the desired Movie ID, Query, and Language parameters determined in Step 3 into their respective fields.

You've now successfully set up the TMDb Source connector in Airbyte.

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
4. Enter your `api_key`.
5. Enter params `movie_id, query, language` (if needed).
6. Click **Set up source**.

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

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-27 | [Init](https://github.com/airbytehq/airbyte/pull/18561)| Initial commit |
