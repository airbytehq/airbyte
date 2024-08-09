# Holiday API

This page contains the setup guide and reference information for the [Holiday API](https://holidayapi.com/docs) manifest-only source connector

## Prerequisites

API key (which is sent as request parameter) is mandate for this connector to work, It could be seen at dashboard (ref - https://holidayapi.com/dashboard). 

## Usage

- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` usinng `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.
Please refer to the manifest-only connector documentation for more details.

## Setup guide

### Step 1: Set up Holiday API connection

- Generate an Holiday-API API key via dashboard (ref - https://holidayapi.com/dashboard)
- Setup params (All params are required)
- Available params
    - api_key: The generated API key

## Step 2: Set up the Holiday API connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Holiday API connector and select **Holiday API** from the Source type dropdown.
4. Enter your `access_token, app_key, start_date and email`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `access_token, app_key, start_date and email`.
5. Click **Set up source**.

## Supported sync modes

The Holiday API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- holidays
- countries
- languages
- workdays

## API method example

GET https://holidayapi.com/v1/holidays?key=xxxxdxxx-xxxx-yyyy-aabc-xxxbxxxxxxxx&country=IN&year=2022

## Performance considerations

Holiday API [API reference](https://holidayapi.com/v1) has v1 at present. The connector as default uses v1.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2024-08-10 | [42133](https://github.com/airbytehq/airbyte/pull/42133)| Initial commit |