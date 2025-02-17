# Wikipedia Pageviews

This page contains the setup guide and reference information for the [Wikipedia Pageviews](https://wikimedia.org/api/rest_v1/#/Pageviews%20data) source connector.

## Prerequisites

None

## Setup guide

## Step 1: Set up the Courier connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Courier connector and select **Wikipedia Pageviews** from the Source type dropdown.
4. Enter your parameters.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your parameters.
4. Click **Set up source**.

## Supported sync modes

The Wikipedia Pageviews source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- per-article
- top

## Performance considerations

100 req/s per endpoint.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject        |
| :------ | :--------- | :-------------------------------------------------------- | :------------- |
| 0.2.10 | 2025-02-08 | [53587](https://github.com/airbytehq/airbyte/pull/53587) | Update dependencies |
| 0.2.9 | 2025-02-01 | [53103](https://github.com/airbytehq/airbyte/pull/53103) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52418](https://github.com/airbytehq/airbyte/pull/52418) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51968](https://github.com/airbytehq/airbyte/pull/51968) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51393](https://github.com/airbytehq/airbyte/pull/51393) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50807](https://github.com/airbytehq/airbyte/pull/50807) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50345](https://github.com/airbytehq/airbyte/pull/50345) | Update dependencies |
| 0.2.3 | 2024-12-14 | [49734](https://github.com/airbytehq/airbyte/pull/49734) | Update dependencies |
| 0.2.2 | 2024-12-12 | [47763](https://github.com/airbytehq/airbyte/pull/47763) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47618](https://github.com/airbytehq/airbyte/pull/47618) | Update dependencies |
| 0.2.0 | 2024-08-20 | [44460](https://github.com/airbytehq/airbyte/pull/44460) | Refactor connector to manifest-only format |
| 0.1.10 | 2024-08-17 | [44202](https://github.com/airbytehq/airbyte/pull/44202) | Update dependencies |
| 0.1.9 | 2024-08-12 | [43771](https://github.com/airbytehq/airbyte/pull/43771) | Update dependencies |
| 0.1.8 | 2024-08-10 | [43543](https://github.com/airbytehq/airbyte/pull/43543) | Update dependencies |
| 0.1.7 | 2024-08-03 | [43184](https://github.com/airbytehq/airbyte/pull/43184) | Update dependencies |
| 0.1.6 | 2024-07-27 | [42706](https://github.com/airbytehq/airbyte/pull/42706) | Update dependencies |
| 0.1.5 | 2024-07-20 | [42242](https://github.com/airbytehq/airbyte/pull/42242) | Update dependencies |
| 0.1.4 | 2024-07-13 | [41686](https://github.com/airbytehq/airbyte/pull/41686) | Update dependencies |
| 0.1.3 | 2024-07-10 | [41560](https://github.com/airbytehq/airbyte/pull/41560) | Update dependencies |
| 0.1.2 | 2024-07-09 | [41081](https://github.com/airbytehq/airbyte/pull/41081) | Update dependencies |
| 0.1.1 | 2024-05-31 | [38724](https://github.com/airbytehq/airbyte/pull/38724) | Make connector compatible with builder |
| 0.1.0   | 2022-10-31 | [#18343](https://github.com/airbytehq/airbyte/pull/18343) | Initial commit |

</details>
