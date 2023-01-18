# Punk-API

The connector uses the v2 API documented here: https://punkapi.com/documentation/v2 . It is
straightforward HTTP REST API with API authentication. 

## API key

Api key is not required for this connector to work,But a dummy key need to be passed to enhance in next versions. Example:123
Just pass the dummy API key and optional parameter for establishing the connection. Example:123

## Implementation details

## Setup guide

### Step 1: Set up Punk-API connection

- Pass a dummy API key (Example: 12345)
- Params (Optional ID)

## Step 2: Generate schema for the endpoint

### Custom schema is generated and tested with different IDs

## Step 3: Spec, Secrets, and connector yaml files are configured with reference to the Airbyte documentation.

## In a nutshell:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
4. Enter your dummy `api_key`.
5. Enter the params configuration if needed: ID (Optional)
6. Click **Set up source**.

 * We use only GET methods, towards the beers endpoints which is straightforward