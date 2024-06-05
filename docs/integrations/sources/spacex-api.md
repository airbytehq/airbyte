# SpaceX-API

This page contains the setup guide and reference information for the [SpaceX-API](https://github.com/r-spacex/SpaceX-API) source connector.

## Prerequisites

No prerequisites, but a dummy api_key is required as it enhances security in future build. Please check the available routes at [SpaceX Routes](https://github.com/r-spacex/SpaceX-API/tree/master/routes).

## Setup guide

### Step 1: Set up SpaceX connection

- Have a dummy API key (Example: 12345)
- A specific id (If specific info is needed)

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
4. Enter your `id` if needed. (Optional)
5. Click **Set up source**.

## Supported sync modes

The SpaceX-API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
|:------------------------------|:-----------|
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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------|
| 0.1.4 | 2024-06-04 | [38976](https://github.com/airbytehq/airbyte/pull/38976) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-30 | [38504](https://github.com/airbytehq/airbyte/pull/38504) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2024-05-28 | [38603](https://github.com/airbytehq/airbyte/pull/38603) | Make connector compatible with builder |
| 0.1.1 | 2023-11-08 | [32202](https://github.com/airbytehq/airbyte/pull/32202) | Adjust schemas to cover all fields in the records |
| 0.1.0   | 2022-10-22 | [Init](https://github.com/airbytehq/airbyte/pull/18311)  | Initial commit                                    |

</details>