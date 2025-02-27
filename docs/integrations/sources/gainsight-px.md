# Gainsight-API

This page contains the setup guide and reference information for the [Gainsight-PX-API](https://gainsightpx.docs.apiary.io/) source connector from [Gainsight-PX](https://support.gainsight.com/PX/API_for_Developers)

## Prerequisites

Api key is mandate for this connector to work, It could be generated from the dashboard settings (ref - https://app.aptrinsic.com/settings/api-keys).

## Setup guide

### Step 1: Set up Gainsight-API connection

- Generate an API key (Example: 12345)
- Params (If specific info is needed)
- Available params
  - api_key: The aptrinsic api_key

## Step 2: Set up the Gainsight-APIs connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Gainsight-API connector and select **Gainsight-API** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter the params configuration if needed. Supported params are: query, orientation, size, color, locale, collection_id \
   video_id, photo_id
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter the params configuration if needed. Supported params are: query, orientation, size, color, locale, collection_id \
   video_id, photo_id
5. Click **Set up source**.

## Supported sync modes

The Gainsight-API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- accounts
- admin_attributes
- articles
- feature
- kcbot
- segments
- user_attributes
- users

## API method example

GET https://api.aptrinsic.com/v1/accounts

## Performance considerations

Gainsight-PX-API's [API reference](https://gainsightpx.docs.apiary.io/) has v1 at present. The connector as default uses v1.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                 |
| :------ | :--------- | :------------------------------------------------------- |:----------------------------------------|
| 0.2.13 | 2025-02-22 | [54408](https://github.com/airbytehq/airbyte/pull/54408) | Update dependencies |
| 0.2.12 | 2025-02-15 | [53719](https://github.com/airbytehq/airbyte/pull/53719) | Update dependencies |
| 0.2.11 | 2025-02-08 | [53311](https://github.com/airbytehq/airbyte/pull/53311) | Update dependencies |
| 0.2.10 | 2025-02-01 | [52847](https://github.com/airbytehq/airbyte/pull/52847) | Update dependencies |
| 0.2.9 | 2025-01-25 | [52362](https://github.com/airbytehq/airbyte/pull/52362) | Update dependencies |
| 0.2.8 | 2025-01-18 | [51703](https://github.com/airbytehq/airbyte/pull/51703) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51090](https://github.com/airbytehq/airbyte/pull/51090) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50511](https://github.com/airbytehq/airbyte/pull/50511) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50041](https://github.com/airbytehq/airbyte/pull/50041) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49533](https://github.com/airbytehq/airbyte/pull/49533) | Update dependencies |
| 0.2.3 | 2024-12-12 | [48195](https://github.com/airbytehq/airbyte/pull/48195) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47864](https://github.com/airbytehq/airbyte/pull/47864) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47626](https://github.com/airbytehq/airbyte/pull/47626) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44414](https://github.com/airbytehq/airbyte/pull/44414) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-17 | [44248](https://github.com/airbytehq/airbyte/pull/44248) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43902](https://github.com/airbytehq/airbyte/pull/43902) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43117](https://github.com/airbytehq/airbyte/pull/43117) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42732](https://github.com/airbytehq/airbyte/pull/42732) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42182](https://github.com/airbytehq/airbyte/pull/42182) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41928](https://github.com/airbytehq/airbyte/pull/41928) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41365](https://github.com/airbytehq/airbyte/pull/41365) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41075](https://github.com/airbytehq/airbyte/pull/41075) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40893](https://github.com/airbytehq/airbyte/pull/40893) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40352](https://github.com/airbytehq/airbyte/pull/40352) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39988](https://github.com/airbytehq/airbyte/pull/39988) | Update dependencies |
| 0.1.3 | 2024-06-04 | [38979](https://github.com/airbytehq/airbyte/pull/38979) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-28 | [38669](https://github.com/airbytehq/airbyte/pull/38669) | Make connector compatible with Builder |
| 0.1.1 | 2024-05-03 | [37593](https://github.com/airbytehq/airbyte/pull/37593) | Changed `last_records` to `last_record` |
| 0.1.0 | 2023-05-10 | [26998](https://github.com/airbytehq/airbyte/pull/26998) | Initial PR |

</details>
