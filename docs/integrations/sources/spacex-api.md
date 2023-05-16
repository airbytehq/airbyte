# SpaceX-API

This page contains the setup guide and reference information for the [SpaceX-API](https://github.com/r-spacex/SpaceX-API) source connector.

## Prerequisites

To set up the SpaceX-API connector, you need to have an API key. If you do not already have one, you can generate a dummy API key (Example: 12345) as it enhances security in future builds. 

Please check the available routes at [SpaceX Routes](https://github.com/r-spacex/SpaceX-API/tree/master/routes) to obtain the necessary information for the `id` property.

## Setup guide

### Step 1: Set up SpaceX connection

1. Obtain your dummy API key from the [SpaceX-API repository](https://github.com/r-spacex/SpaceX-API).
2. If you need specific information, check the available routes at [SpaceX Routes](https://github.com/r-spacex/SpaceX-API/tree/master/routes) and obtain the necessary `id`.
3. Record your API key and ID for use in the next step.

### Step 2: Set up the SpaceX-API connector in Airbyte

1. Navigate to the Airbyte Connector form. 
2. Enter the required `id` and `options` in the respective fields according to the provided Airbyte Connector spec.

    - The `id` field is optional and is used to specify a specific target source.
    - The `options` field is optional and specifies possible values for an endpoint. Example values for various endpoints are [available here](https://github.com/r-spacex/SpaceX-API/tree/master/docs). 

3. Enter the API key you obtained in Step 1 in the `api_key` field.
4. Click **Test connection** to ensure the connector is working correctly.
5. Click **Save** to finalize the setup.

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