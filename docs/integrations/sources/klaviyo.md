# Klaviyo

This page contains the setup guide and reference information for the Klaviyo source connector.

## Prerequisites

* Klaviyo Private API Key

## Setup guide
### Step 1: Set up Klaviyo

Please follow these [steps](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3) to obtain Private API Key for your account.

### Step 2: Set up the Klaviyo connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Klaviyo connector and select **Klaviyo** from the Source type dropdown.
4. Enter you private API key from Prerequisites
5. Enter the date you want your sync to start from
6. Submit the form

### For Airbyte Open Source:
1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
4. Enter you private API key from Prerequisites
5. Enter the date you want your sync to start from
6. Click **Set up source**

## Supported sync modes

The Klaviyo source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh | Overwrite
 - Full Refresh | Append
 - Incremental Sync | Append
 - Incremental Sync | Deduped History

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Campaigns](https://apidocs.klaviyo.com/reference/campaigns#get-campaigns)
* [Events](https://apidocs.klaviyo.com/reference/metrics#metrics-timeline)
* [GlobalExclusions](https://apidocs.klaviyo.com/reference/lists-segments#get-global-exclusions)
* [Lists](https://apidocs.klaviyo.com/reference/lists#get-lists-deprecated)
* [Metrics](https://apidocs.klaviyo.com/en/reference/get-metrics)

## Performance considerations

The connector is restricted by normal Klaviyo [requests limitation](https://apidocs.klaviyo.com/reference/api-overview#rate-limits).

The Klaviyo connector should not run into Klaviyo API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Data type map

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                                   |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------|
| `0.1.6` | 2022-07-20 | [14872](https://github.com/airbytehq/airbyte/issues/14872) | Increase test coverage                                                                    |
| `0.1.5` | 2022-07-12 | [14617](https://github.com/airbytehq/airbyte/issues/14617) | Set max\_retries = 10 for `lists` stream.                                                 |
| `0.1.4` | 2022-04-15 | [11723](https://github.com/airbytehq/airbyte/issues/11723) | Enhance klaviyo source for flows stream and update to events stream.                      |
| `0.1.3` | 2021-12-09 | [8592](https://github.com/airbytehq/airbyte/pull/8592)     | Improve performance, make Global Exclusions stream incremental and enable Metrics stream. |
| `0.1.2` | 2021-10-19 | [6952](https://github.com/airbytehq/airbyte/pull/6952)     | Update schema validation in SAT                                                           |
