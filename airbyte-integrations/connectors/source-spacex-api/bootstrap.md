# SpaceX-API

The connector uses the v4 API documented here: https://github.com/r-spacex/SpaceX-API . It is
straightforward HTTP REST API with no authentication.

## Dummy API key

Api key is mandate for this connector to work as it could be used in future enhancements.
Just pass any dummy api key for establishing the connection. Example:123

## Implementation details

## Setup guide

### Step 1: Set up SpaceX connection

- Have a dummy API key (Example: 12345)
- A specific id (If specific info is needed)

## Step 2: Generate schema for the endpoint

### Custom schema is generated and tested with different IDs

## Step 3: Spec, Secrets, and connector yaml files are configured with reference to the Airbyte documentation.

## In a nutshell:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter your `id` if needed. (Optional)
5. Click **Set up source**.

- We use only GET methods, all endpoints are straightforward. We emit what we receive as HTTP response.
