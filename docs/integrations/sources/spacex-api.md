# SpaceX-API

This page contains the setup guide and reference information for the [SpaceX-API](https://github.com/r-spacex/SpaceX-API) source connector.

## Prerequisites

No prerequisites, but a dummy api_key is required as it enhances security in future build. Please check the available routes at [SpaceX Routes](https://github.com/r-spacex/SpaceX-API/tree/master/routes).

## Setup guide

### Step 1: Obtain a dummy API key

As a security measure, a dummy API key is required for the source connector setup. This key can be any random string value (e.g.: `12345`) to maintain compatibility with other API connectors.

### Step 2: Identifying a specific ID (optional)

If you want to retrieve data for a specific entity in the SpaceX-API, you need to use a valid identifier for that entity. For example, if you want data on a specific launch, you can obtain the launch ID from the API using a tool like [Postman](https://www.postman.com/) or directly in your browser by visiting `https://api.spacexdata.com/v5/launches`.

Make a note of the target ID for the desired entity, as it will be required in a later step.

### Step 3: Configure the SpaceX-API connector in Airbyte

1. Enter the following details in the connector configuration form:
    - Unique ID (optional): Provide the target ID for the specific entity, as noted in Step 2.
    - ListItem Configuration options for endpoints (optional): Provide possible values for an endpoint, such as `latest`, `upcoming`, or `past` for the `launches` endpoint. 

2. Enter your dummy `api_key` obtained in Step 1.

3. Click **Set up source** to complete the setup process.

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