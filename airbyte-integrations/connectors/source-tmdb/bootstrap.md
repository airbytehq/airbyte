# TMDb

The connector uses the v3 API documented here: https://developers.themoviedb.org/3/getting-started/introduction. It is
straightforward HTTP REST API with API Authentication.

## API key

Api key is mandate for this connector to work. It could be generated using a free account at TMDb. Visit: https://www.themoviedb.org/settings/api

## Implementation details

## Setup guide

### Step 1: Set up TMDb connection

- Have an API key by generating personal API key (Example: 12345)
- A movie ID, or query could be configured in config.json (Not Mandate, Default movie \_id would be 550 and query would be marvel)
- See sample_config.json for more details

## Step 2: Generate schema for the endpoint

### Custom schema is generated and tested with different IDs

## Step 3: Spec, Secrets, and connector yaml files are configured with reference to the Airbyte documentation.

## In a nutshell:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter params `movie_id, query, language` (if needed).
5. Click **Set up source**.

- We use only GET methods, all streams are straightforward.
