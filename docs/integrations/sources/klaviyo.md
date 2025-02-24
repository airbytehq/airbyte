# Klaviyo

<HideInUI>

This page contains the setup guide and reference information for the [Klaviyo](https://www.klaviyo.com) source connector.

</HideInUI>

## Prerequisites

- Klaviyo [account](https://www.klaviyo.com)
- [Klaviyo Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3)

## Setup guide

### Step 1: Set up Klaviyo

1. Create a [Klaviyo account](https://www.klaviyo.com)
2. Create a [Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3). Make sure you selected all [scopes](https://help.klaviyo.com/hc/en-us/articles/7423954176283) corresponding to the streams you would like to replicate. You can find which scope is required for a specific stream by navigating to the relevant API documentation for the streams Airbyte supports.

### Step 2: Set up the Klaviyo connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Klaviyo from the Source type dropdown.
4. Enter a name for the Klaviyo connector.
5. For **Api Key**, enter the Klaviyo [Private API key](https://help.klaviyo.com/hc/en-us/articles/115005062267-How-to-Manage-Your-Account-s-API-Keys#your-private-api-keys3).
6. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. This field is optional - if not provided, all data will be replicated.
7. Click **Set up source**.

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Klaviyo from the Source type dropdown.
4. Enter a name for the Klaviyo connector.

## Supported sync modes

The Klaviyo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Campaigns](https://developers.klaviyo.com/en/v2023-06-15/reference/get_campaigns)
- [Campaigns Detailed](https://developers.klaviyo.com/en/v2023-06-15/reference/get_campaigns)
- [Email Templates](https://developers.klaviyo.com/en/reference/get_templates)
- [Events](https://developers.klaviyo.com/en/reference/get_events)
- [Events Detailed](https://developers.klaviyo.com/en/reference/get_event)
- [Flows](https://developers.klaviyo.com/en/reference/get_flows)
- [GlobalExclusions](https://developers.klaviyo.com/en/v2023-02-22/reference/get_profiles)
- [Lists](https://developers.klaviyo.com/en/reference/get_lists)
- [Lists Detailed](https://developers.klaviyo.com/en/reference/get_lists)
- [Metrics](https://developers.klaviyo.com/en/reference/get_metrics)
- [Profiles](https://developers.klaviyo.com/en/v2023-02-22/reference/get_profiles)

## Performance considerations

The connector is restricted by Klaviyo [requests limitation](https://apidocs.klaviyo.com/reference/api-overview#rate-limits).

The Klaviyo connector should not run into Klaviyo API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

The `Campaigns Detailed` stream contains fields `estimated_recipient_count` and `campaign_message` in addition to info from the `Campaigns` stream. Additional time is needed to fetch extra data.

The `Lists Detailed` stream contains field `profile_count` in addition to info from the `Lists` stream. Additional time is needed to fetch extra data due to Klaviyo API [limitation](https://developers.klaviyo.com/en/reference/get_list).

The `Events Detailed` stream contains field `name` for `metric` relationship - addition to [info](https://developers.klaviyo.com/en/reference/get_event).

The `Profiles` stream can experience transient API errors under heavy load. In order to mitigate this, you can use the "Disable Fetching Predictive Analytics" setting to improve the success rate of syncs.

:::warning
Using the "Disable Fetching Predictive Analytics" will stop records on the Profiles stream will no longer
contain the `predictive_analytics` field and workflows depending on this field will stop working.
:::

## Data type map

| Integration Type | Airbyte Type |
|:-----------------|:-------------|
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                                |
|:--------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.13.1 | 2025-02-22 | [54369](https://github.com/airbytehq/airbyte/pull/54369) | Update dependencies |
| 2.13.0 | 2025-02-18 | [51551](https://github.com/airbytehq/airbyte/pull/51551) | Upgrade to API v2024-10-15 |
| 2.12.1 | 2025-02-15 | [52710](https://github.com/airbytehq/airbyte/pull/52710) | Update dependencies |
| 2.12.0 | 2025-02-11 | [53223](https://github.com/airbytehq/airbyte/pull/53223) | Add API Budget |
| 2.11.11 | 2025-01-27 | [52563](https://github.com/airbytehq/airbyte/pull/52563) | Fix `lists_detailed` incremental sync |
| 2.11.10 | 2025-01-25 | [52285](https://github.com/airbytehq/airbyte/pull/52285) | Update dependencies |
| 2.11.9 | 2025-01-11 | [51198](https://github.com/airbytehq/airbyte/pull/51198) | Update dependencies |
| 2.11.8 | 2025-01-09 | [51010](https://github.com/airbytehq/airbyte/pull/51010) | Fix AirbyteMessage serialization with integers bigger than 64 bits |
| 2.11.7 | 2025-01-04 | [50893](https://github.com/airbytehq/airbyte/pull/50893) | Update dependencies |
| 2.11.6 | 2024-12-28 | [50653](https://github.com/airbytehq/airbyte/pull/50653) | Update dependencies |
| 2.11.5 | 2024-12-21 | [50088](https://github.com/airbytehq/airbyte/pull/50088) | Update dependencies |
| 2.11.4 | 2024-12-14 | [49250](https://github.com/airbytehq/airbyte/pull/49250) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.11.3 | 2024-12-12 | [49144](https://github.com/airbytehq/airbyte/pull/49144) | Update dependencies |
| 2.11.2 | 2024-12-02 | [48748](https://github.com/airbytehq/airbyte/pull/48748) | Bump CDK to evict non retriable requests to avoid high memory usage |
| 2.11.1 | 2024-11-26 | [48710](https://github.com/airbytehq/airbyte/pull/48710) | Retry on "Temporary failure in name resolution" |
| 2.11.0 | 2024-11-18 | [48452](https://github.com/airbytehq/airbyte/pull/48452) | Enable concurrency for syncs that don't have client-side filtering |
| 2.10.14 | 2024-11-07 | [48391](https://github.com/airbytehq/airbyte/pull/48391) | Remove custom datetime cursor dependency |
| 2.10.13 | 2024-11-05 | [48331](https://github.com/airbytehq/airbyte/pull/48331) | Update dependencies |
| 2.10.12 | 2024-10-29 | [47797](https://github.com/airbytehq/airbyte/pull/47797) | Update dependencies |
| 2.10.11 | 2024-10-28 | [47043](https://github.com/airbytehq/airbyte/pull/47043) | Update dependencies |
| 2.10.10 | 2024-10-14 | [46741](https://github.com/airbytehq/airbyte/pull/46741) | Add checkpointing to events stream to improve large syncs after clear data |
| 2.10.9 | 2024-10-12 | [46787](https://github.com/airbytehq/airbyte/pull/46787) | Update dependencies |
| 2.10.8 | 2024-10-05 | [46503](https://github.com/airbytehq/airbyte/pull/46503) | Update dependencies |
| 2.10.7 | 2024-09-28 | [46174](https://github.com/airbytehq/airbyte/pull/46174) | Update dependencies |
| 2.10.6 | 2024-09-21 | [45813](https://github.com/airbytehq/airbyte/pull/45813) | Update dependencies |
| 2.10.5 | 2024-09-14 | [45530](https://github.com/airbytehq/airbyte/pull/45530) | Update dependencies |
| 2.10.4 | 2024-09-07 | [45244](https://github.com/airbytehq/airbyte/pull/45244) | Update dependencies |
| 2.10.3 | 2024-08-31 | [45064](https://github.com/airbytehq/airbyte/pull/45064) | Update dependencies |
| 2.10.2 | 2024-08-30 | [44930](https://github.com/airbytehq/airbyte/pull/44930) | Fix typing in profiles stream for field `attributes.location.region` |
| 2.10.1 | 2024-08-24 | [44628](https://github.com/airbytehq/airbyte/pull/44628) | Update dependencies |
| 2.10.0 | 2024-08-18 | [44366](https://github.com/airbytehq/airbyte/pull/44366) | Add field[metrics] to events stream |
| 2.9.4 | 2024-08-17 | [44317](https://github.com/airbytehq/airbyte/pull/44317) | Update dependencies |
| 2.9.3 | 2024-08-12 | [43806](https://github.com/airbytehq/airbyte/pull/43806) | Update dependencies |
| 2.9.2 | 2024-08-10 | [43613](https://github.com/airbytehq/airbyte/pull/43613) | Update dependencies |
| 2.9.1 | 2024-08-03 | [43247](https://github.com/airbytehq/airbyte/pull/43247) | Update dependencies |
| 2.9.0 | 2024-08-01 | [42891](https://github.com/airbytehq/airbyte/pull/42891) | Migrate to CDK v4.X and remove custom BackoffStrategy implementation |
| 2.8.2 | 2024-07-31 | [42895](https://github.com/airbytehq/airbyte/pull/42895) | Add config option disable_fetching_predictive_analytics to prevent 503 Service Unavailable errors |
| 2.8.1 | 2024-07-27 | [42664](https://github.com/airbytehq/airbyte/pull/42664) | Update dependencies |
| 2.8.0 | 2024-07-19 | [42121](https://github.com/airbytehq/airbyte/pull/42121) | Migrate to CDK v3.9.0 |
| 2.7.8 | 2024-07-20 | [42185](https://github.com/airbytehq/airbyte/pull/42185) | Update dependencies |
| 2.7.7 | 2024-07-08 | [40608](https://github.com/airbytehq/airbyte/pull/40608) | Update the `events_detailed` stream to improve efficiency using the events API |
| 2.7.6 | 2024-07-13 | [41903](https://github.com/airbytehq/airbyte/pull/41903) | Update dependencies |
| 2.7.5 | 2024-07-10 | [41548](https://github.com/airbytehq/airbyte/pull/41548) | Update dependencies |
| 2.7.4 | 2024-07-09 | [41211](https://github.com/airbytehq/airbyte/pull/41211) | Update dependencies |
| 2.7.3 | 2024-07-06 | [40770](https://github.com/airbytehq/airbyte/pull/40770) | Update dependencies |
| 2.7.2 | 2024-06-26 | [40401](https://github.com/airbytehq/airbyte/pull/40401) | Update dependencies |
| 2.7.1 | 2024-06-22 | [40032](https://github.com/airbytehq/airbyte/pull/40032) | Update dependencies |
| 2.7.0 | 2024-06-08 | [39350](https://github.com/airbytehq/airbyte/pull/39350) | Add `events_detailed` stream |
| 2.6.4 | 2024-06-06 | [38879](https://github.com/airbytehq/airbyte/pull/38879) | Implement `CheckpointMixin` for handling state in Python streams |
| 2.6.3 | 2024-06-04 | [38935](https://github.com/airbytehq/airbyte/pull/38935) | [autopull] Upgrade base image to v1.2.1 |
| 2.6.2 | 2024-05-08 | [37789](https://github.com/airbytehq/airbyte/pull/37789) | Move stream schemas and spec to manifest |
| 2.6.1 | 2024-05-07 | [38010](https://github.com/airbytehq/airbyte/pull/38010) | Add error handler for `5XX` status codes |
| 2.6.0 | 2024-04-19 | [37370](https://github.com/airbytehq/airbyte/pull/37370) | Add streams `campaigns_detailed` and `lists_detailed` |
| 2.5.0 | 2024-04-15 | [36264](https://github.com/airbytehq/airbyte/pull/36264) | Migrate to low-code |
| 2.4.0 | 2024-04-11 | [36989](https://github.com/airbytehq/airbyte/pull/36989) | Update `Campaigns` schema |
| 2.3.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 2.2.0 | 2024-02-27 | [35637](https://github.com/airbytehq/airbyte/pull/35637) | Fix `predictive_analytics` field in stream `profiles` |
| 2.1.3 | 2024-02-15 | [35336](https://github.com/airbytehq/airbyte/pull/35336) | Added type transformer for the `profiles` stream. |
| 2.1.2 | 2024-02-09 | [35088](https://github.com/airbytehq/airbyte/pull/35088) | Manage dependencies with Poetry. |
| 2.1.1 | 2024-02-07 | [34998](https://github.com/airbytehq/airbyte/pull/34998) | Add missing fields to stream schemas |
| 2.1.0 | 2023-12-07 | [33237](https://github.com/airbytehq/airbyte/pull/33237) | Continue syncing streams even when one of the stream fails |
| 2.0.2 | 2023-12-05 | [33099](https://github.com/airbytehq/airbyte/pull/33099) | Fix filtering for archived records stream |
| 2.0.1 | 2023-11-08 | [32291](https://github.com/airbytehq/airbyte/pull/32291) | Add logic to have regular checkpointing schedule |
| 2.0.0 | 2023-11-03 | [32128](https://github.com/airbytehq/airbyte/pull/32128) | Use the latest API for streams `campaigns`, `email_templates`, `events`, `flows`, `global_exclusions`, `lists`, and `metrics` |
| 1.1.0 | 2023-10-23 | [31710](https://github.com/airbytehq/airbyte/pull/31710) | Make `start_date` config field optional |
| 1.0.0 | 2023-10-18 | [31565](https://github.com/airbytehq/airbyte/pull/31565) | Add new known fields for 'events' stream |
| 0.5.0 | 2023-10-19 | [31611](https://github.com/airbytehq/airbyte/pull/31611) | Add `date-time` format for `datetime` field in `Events` stream |
| 0.4.0 | 2023-10-18 | [31562](https://github.com/airbytehq/airbyte/pull/31562) | Add `archived` field to `Flows` stream |
| 0.3.3 | 2023-10-13 | [31379](https://github.com/airbytehq/airbyte/pull/31379) | Skip streams that the connector no longer has access to |
| 0.3.2 | 2023-06-20 | [27498](https://github.com/airbytehq/airbyte/pull/27498) | Do not store state in the future |
| 0.3.1 | 2023-06-08 | [27162](https://github.com/airbytehq/airbyte/pull/27162) | Anonymize check connection error message |
| 0.3.0 | 2023-02-18 | [23236](https://github.com/airbytehq/airbyte/pull/23236) | Add ` Email Templates` stream |
| 0.2.0   | 2023-03-13 | [22942](https://github.com/airbytehq/airbyte/pull/23968)   | Add `Profiles` stream                                                                                                                                                  |
| 0.1.13  | 2023-02-13 | [22942](https://github.com/airbytehq/airbyte/pull/22942)   | Specified date formatting in specification                                                                                                                             |
| 0.1.12  | 2023-01-30 | [22071](https://github.com/airbytehq/airbyte/pull/22071)   | Fix `Events` stream schema                                                                                                                                             |
| 0.1.11  | 2023-01-27 | [22012](https://github.com/airbytehq/airbyte/pull/22012)   | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                            |
| 0.1.10  | 2022-09-29 | [17422](https://github.com/airbytehq/airbyte/issues/17422) | Update CDK dependency                                                                                                                                                  |
| 0.1.9   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/issues/17304) | Migrate to per-stream state.                                                                                                                                           |
| 0.1.6   | 2022-07-20 | [14872](https://github.com/airbytehq/airbyte/issues/14872) | Increase test coverage                                                                                                                                                 |
| 0.1.5   | 2022-07-12 | [14617](https://github.com/airbytehq/airbyte/issues/14617) | Set max_retries = 10 for `lists` stream.                                                                                                                               |
| 0.1.4   | 2022-04-15 | [11723](https://github.com/airbytehq/airbyte/issues/11723) | Enhance klaviyo source for flows stream and update to events stream.                                                                                                   |
| 0.1.3   | 2021-12-09 | [8592](https://github.com/airbytehq/airbyte/pull/8592)     | Improve performance, make Global Exclusions stream incremental and enable Metrics stream.                                                                              |
| 0.1.2   | 2021-10-19 | [6952](https://github.com/airbytehq/airbyte/pull/6952)     | Update schema validation in SAT                                                                                                                                        |

</details>
