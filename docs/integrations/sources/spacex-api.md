# SpaceX-API

This page contains the setup guide and reference information for the [SpaceX-API](https://github.com/r-spacex/SpaceX-API) source connector.

## Prerequisites

No prerequisites, but a dummy api_key is required as it enhances security in future build. Please check the available routes at [SpaceX Routes](https://github.com/r-spacex/SpaceX-API/tree/master/routes).

## Setup Guide

This guide will help you configure the spacex-api Source connector in Airbyte.

### Prerequisites

Before proceeding with the setup, ensure that:

1. You have a basic understanding of the SpaceX API. Familiarize yourself with its documentation and usage [here](https://github.com/r-spacex/SpaceX-API).
2. You are aware of the available endpoints and their respective attributes. Explore the official SpaceX-API repository for a detailed list of endpoints and their parameters [here](https://github.com/r-spacex/SpaceX-API/tree/master/docs).


### Step 1: Enter the Unique ID (optional)

If you need to access specific data in the API, provide a unique ID in the "Unique ID for specific source target" input field. This is an optional field.

For example, if you need information for a specific launch, you can provide its unique ID, such as "5eb87d46ffd86e000604b391". Check the SpaceX-API documentation on how to obtain unique IDs for different endpoints.

### Step 2: Configuration Options (optional)

Under "Configuration options for endpoints", enter any desired endpoint options in the provided input field. This is also an optional field.

These options allow you to define parameters specific to the requested data. For example, you can configure the "launches" endpoint's optional parameters like "limit" or "offset" to narrow down the data you receive.

Some example values for endpoints can be:
- launches-latest
- upcoming
- past

Refer to the official [SpaceX-API documentation](https://github.com/r-spacex/SpaceX-API/tree/master/docs) for a detailed list of available parameters and their usage.

### Step 3: Save Connector Configuration

Once you have provided the required information for the connector, click on the "Save" button to store your configuration.

You have now successfully set up your spacex-api Source connector in Airbyte!

## Step 2: Set up the SpaceX-API connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the SpaceX-API connector and select **Spacex-API** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter your `id` if needed. (Optional)
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
5. Enter your `id` if needed. (Optional)
6. Click **Set up source**.

## Supported sync modes

The SpaceX-API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- Launches
- Capsules
- Company
- Crew
- Cores
- Dragons
- History
- Landpads
- Payloads
- Roadster
- Rockets
- Ships
- Starlink

## API method example

`GET https://api.spacexdata.com/v5/launches/latest`

## Performance considerations

The SpaceX API has both v4 and v5 for [launches](https://github.com/r-spacex/SpaceX-API/tree/master/docs/launches). The connector as default uses V4 as it has minimal bugs.

## Changelog

| Version | Date       | Pull Request                                           | Subject        |
| :------ | :--------- | :----------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-22 | [Init](https://github.com/airbytehq/airbyte/pull/18311) | Initial commit |
