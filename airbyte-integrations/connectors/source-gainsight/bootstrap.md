# Gainsight

This page contains the setup guide and reference information for the [Gainsight-PX-API](https://gainsightpx.docs.apiary.io/) source connector from [Gainsight](https://support.gainsight.com/PX/API_for_Developers)

## Prerequisites

Api key is mandate for this connector to work, It could be generated from the dashboard settings (ref - https://app.aptrinsic.com/settings/api-keys). 


## Implementation details

## Setup guide

### Step 1: Set up Gainsight-API connection

- Generate an API key (Example: 12345)
- Params (If specific info is needed)
- Available params
    - api_key: The aptrinsic api_key

## Step 2: Generate schema for the endpoint

### Custom schema is generated and tested with different IDs

## Step 3: Spec, Secrets, and connector yaml files are configured with reference to the Airbyte documentation.

## In a nutshell:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
5. Enter your config params if needed. (Optional)
6. Click **Set up source**.

 * We use only GET methods, towards the API endpoints which is straightforward