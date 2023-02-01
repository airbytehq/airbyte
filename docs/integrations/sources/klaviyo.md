# Klaviyo

This page contains the setup guide and reference information for the Klaviyo source connector.

## Prerequisites

To set up the Klaviyo source connector, you'll need the [Klaviyo Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3).


## Set up the Klaviyo connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Klaviyo** from the Source type dropdown.
4. Enter the name for the Klaviyo connector.
5. For **Api Key**, enter the Klaviyo [Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3).
6. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. 
7. Click **Set up source**.

## Supported sync modes

The Klaviyo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

* [Campaigns](https://developers.klaviyo.com/en/v1-2/reference/get-campaigns#get-campaigns)
* [Events](https://developers.klaviyo.com/en/v1-2/reference/metrics-timeline)
* [GlobalExclusions](https://developers.klaviyo.com/en/v1-2/reference/get-global-exclusions)
* [Lists](https://developers.klaviyo.com/en/v1-2/reference/get-lists)
* [Metrics](https://developers.klaviyo.com/en/v1-2/reference/get-metrics)
* [Flows](https://developers.klaviyo.com/en/reference/get_flows)

## Performance considerations

The connector is restricted by Klaviyo [requests limitation](https://apidocs.klaviyo.com/reference/api-overview#rate-limits).

The Klaviyo connector should not run into Klaviyo API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

## Data type map

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version  | Date       | Pull Request                                               | Subject                                                                                   |
|:---------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------|
| `0.1.11` | 2023-01-27 | [22012](https://github.com/airbytehq/airbyte/pull/22012) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| `0.1.10` | 2022-09-29 | [17422](https://github.com/airbytehq/airbyte/issues/17422) | Update CDK dependency                                                                     |
| `0.1.9`  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/issues/17304) | Migrate to per-stream state.                                                              |                                                      
| `0.1.6`  | 2022-07-20 | [14872](https://github.com/airbytehq/airbyte/issues/14872) | Increase test coverage                                                                    |
| `0.1.5`  | 2022-07-12 | [14617](https://github.com/airbytehq/airbyte/issues/14617) | Set max\_retries = 10 for `lists` stream.                                                 |
| `0.1.4`  | 2022-04-15 | [11723](https://github.com/airbytehq/airbyte/issues/11723) | Enhance klaviyo source for flows stream and update to events stream.                      |
| `0.1.3`  | 2021-12-09 | [8592](https://github.com/airbytehq/airbyte/pull/8592)     | Improve performance, make Global Exclusions stream incremental and enable Metrics stream. |
| `0.1.2`  | 2021-10-19 | [6952](https://github.com/airbytehq/airbyte/pull/6952)     | Update schema validation in SAT                                                           |
