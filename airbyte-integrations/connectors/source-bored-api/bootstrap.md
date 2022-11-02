# Bored-API

The connector uses the v1 API documented here: https://www.boredapi.com/documentation. It is
straightforward HTTP REST API without authentication. 

## API key

Api key is not mandate for this connector to work, But a dummy API need to be passed for establishing the connection. Example: 12345
Just pass the dummy API key and optional parameters for establishing the connection.

## Implementation details

## Setup guide

### Step 1: Set up Bored-API connection

- Get a dummy API key (Example: 12345)
- Params (If specific info is needed)
- Available params
  - "key" Example: "5881028",
  - "type" Example: "recreational",
  - "participants" Example: "1",
  - "price" Example: "0.0",
  - "minprice" Exmaple: "0",
  - "maxprice" Example: "0.1",
  - "accessibility" Example: "1",
  - "minaccessibility" Example: "0",
  - "maxaccessibility" Example: "0.1"


## Step 2: Generate schema for the endpoint

### Custom schema is generated and tested with different keys

## Step 3: Spec, Secrets, and connector yaml files are configured with reference to the Airbyte documentation.

## In a nutshell:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your dummy `api_key`.
5. Enter your config params if needed. (Optional)
6. Click **Set up source**.

 * We use only GET methods, towards the webfonts endpoints which is straightforward