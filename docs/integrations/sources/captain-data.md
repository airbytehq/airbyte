# Captain Data

This page contains the setup guide and reference information for the [Captain Data](https://docs.captaindata.co/#intro) source connector.

## Prerequisites

Api key and project UID are mandate for this connector to work, It could be generated from the dashboard settings (ref - https://app.captaindata.co/settings).

## Setup guide

### Step 1: Set up Captain Data connection

- Available params
  - api_key: The api_key
  - project_uid: The project UID

## Step 2: Set up the Captain Data connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Captain Data connector and select **Captain Data** from the Source type dropdown.
4. Enter your `api_key` and `project_uid`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key` and `project_uid`.
4. Click **Set up source**.

## Supported sync modes

The Captain Data source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- workspace
- workflows
- jobs
- job_results

## API method example

GET https://api.captaindata.co/v3/

## Performance considerations

Captain Data [API reference](https://docs.captaindata.co/#intro) has v3 at present. The connector as default uses v3.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                            | Subject                                     |
| :------ |:-----------| :------------------------------------------------------ |:--------------------------------------------|
| 0.2.16 | 2025-03-08 | [55396](https://github.com/airbytehq/airbyte/pull/55396) | Update dependencies |
| 0.2.15 | 2025-03-01 | [54834](https://github.com/airbytehq/airbyte/pull/54834) | Update dependencies |
| 0.2.14 | 2025-02-22 | [54232](https://github.com/airbytehq/airbyte/pull/54232) | Update dependencies |
| 0.2.13 | 2025-02-15 | [53900](https://github.com/airbytehq/airbyte/pull/53900) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53403](https://github.com/airbytehq/airbyte/pull/53403) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52892](https://github.com/airbytehq/airbyte/pull/52892) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52185](https://github.com/airbytehq/airbyte/pull/52185) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51741](https://github.com/airbytehq/airbyte/pull/51741) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51277](https://github.com/airbytehq/airbyte/pull/51277) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50475](https://github.com/airbytehq/airbyte/pull/50475) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50192](https://github.com/airbytehq/airbyte/pull/50192) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49569](https://github.com/airbytehq/airbyte/pull/49569) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49299](https://github.com/airbytehq/airbyte/pull/49299) | Update dependencies |
| 0.2.3 | 2024-12-11 | [48900](https://github.com/airbytehq/airbyte/pull/48900) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.2 | 2024-11-04 | [48177](https://github.com/airbytehq/airbyte/pull/48177) | Update dependencies |
| 0.2.1 | 2024-10-29 | [47769](https://github.com/airbytehq/airbyte/pull/47769) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44419](https://github.com/airbytehq/airbyte/pull/44419) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-17 | [44340](https://github.com/airbytehq/airbyte/pull/44340) | Update dependencies |
| 0.1.14 | 2024-08-12 | [43919](https://github.com/airbytehq/airbyte/pull/43919) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43531](https://github.com/airbytehq/airbyte/pull/43531) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43136](https://github.com/airbytehq/airbyte/pull/43136) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42717](https://github.com/airbytehq/airbyte/pull/42717) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42137](https://github.com/airbytehq/airbyte/pull/42137) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41751](https://github.com/airbytehq/airbyte/pull/41751) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41583](https://github.com/airbytehq/airbyte/pull/41583) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41321](https://github.com/airbytehq/airbyte/pull/41321) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40886](https://github.com/airbytehq/airbyte/pull/40886) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40486](https://github.com/airbytehq/airbyte/pull/40486) | Update dependencies |
| 0.1.4 | 2024-06-21 | [39929](https://github.com/airbytehq/airbyte/pull/39929) | Update dependencies |
| 0.1.3 | 2024-06-15 | [39508](https://github.com/airbytehq/airbyte/pull/39508) | Make connector compatible with Builder |
| 0.1.2 | 2024-06-04 | [38951](https://github.com/airbytehq/airbyte/pull/38951) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-20 | [38374](https://github.com/airbytehq/airbyte/pull/38374) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2023-04-15 | [Init](https://github.com/airbytehq/airbyte/pull/25230) | Initial commit                              |

</details>
