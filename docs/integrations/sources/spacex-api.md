# SpaceX-API

This page contains the setup guide and reference information for the [SpaceX-API](https://github.com/r-spacex/SpaceX-API) source connector.

## Prerequisites

No prerequisites, but a dummy `api_key` is required as it enhances security in future builds. Please check the available routes at [SpaceX Routes](https://github.com/r-spacex/SpaceX-API/tree/master/routes).

## Setup guide

### Step 1: Register for SpaceX API key

1. Go to the [SpaceX-API](https://github.com/r-spacex/SpaceX-API) website.
2. Follow the instructions provided in the website's README to register for an API token.

### Step 2: Set up SpaceX connection

1. Once you have your API key, navigate to the Airbyte SpaceX API connector configuration screen.
2. In the **Configuration** section, enter your `api_key`.
3. If you need specific information, enter your `id` in the relevant field.

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

For more information about the SpaceX-API connector configuration, see [Spacex Api Spec](https://docs.airbyte.com/integrations/sources/spacex-api).