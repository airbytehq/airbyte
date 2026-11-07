# Adjust

This page guides you through setting up the [Adjust](https://www.adjust.com/) source connector. The connector syncs aggregated mobile measurement data from the [Adjust Report Service API](https://dev.adjust.com/en/api/rs-api/reports/).

## Prerequisites

- An Adjust API token. You can find your token on the **My profile** tab of your Adjust dashboard. See [Report service API authentication](https://dev.adjust.com/en/api/rs-api/authentication/). If your organization uses single sign-on (SSO), API tokens aren't available in the Adjust dashboard.
- The names of the metrics and dimensions you want to sync.

### List app-specific metrics

The **Metrics to ingest** field only offers a fixed set of standard metrics. Adjust also supports metrics that are specific to your apps, such as custom event metrics and cohort metrics, which you can enter in the **Additional metrics for ingestion** field. To find the available metric names, see the [Datascape metrics glossary](https://help.adjust.com/en/article/datascape-metrics-glossary).

To list the event slugs defined for your apps, query the [Events endpoint](https://dev.adjust.com/en/api/rs-api/events/). Replace `API_TOKEN` with your Adjust API token:

```sh
curl --header 'Authorization: Bearer API_TOKEN' 'https://automate.adjust.com/reports-service/events' | jq
```

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the **Set up the source** page, select **Adjust** from the **Source type** dropdown.
3. Enter a name for your new source.
4. For **API Token**, enter your Adjust API token.
5. For **Ingest Start Date**, enter the date to start syncing data from, in `YYYY-MM-DD` format. The connector assumes UTC.
6. For **Metrics to ingest**, select at least one metric.
7. (Optional) For **Additional metrics for ingestion**, enter the names of any app-specific or cohort metrics. The connector types these columns as numbers.
8. For **Dimensions**, select at least one dimension to group metrics by. The connector always adds the `day` dimension, so you don't need to select it.
9. (Optional) Turn on **Until Today** to stop each sync at the current time instead of requesting data through the following day.
10. Click **Set up source**.

## Supported sync modes

The Adjust source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append

The stream doesn't define a primary key, so Incremental - Append + Deduped isn't supported.

## Supported streams

The connector syncs a single stream, `AdjustReport`, from the Adjust [JSON report endpoint](https://dev.adjust.com/en/api/rs-api/reports/). Each record contains the metrics you selected, grouped by `day` and the dimensions you selected. The stream schema includes only the columns for your selected metrics and dimensions, plus `day`.

For incremental syncs, the connector uses `day` as the cursor and requests one day of data per API call.

## Limitations

- The Adjust Report Service API allows up to 50 requests per second per source IP address and returns `429 Too Many Requests` when you exceed this limit. See [Report service API rate limits](https://dev.adjust.com/en/api/rs-api/rate-limits/).
- Changing the selected metrics or dimensions changes the stream schema. Refresh the source schema in your connection after you change them.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|---------|------------| -------------------------------------------------------- |---------------------------------------------|
| 0.2.0 | 2026-11-03 | [90863](https://github.com/airbytehq/airbyte/pull/90863) | Upgrade to airbyte-cdk 7 and Python 3.13 base image |
| 0.1.33 | 2025-02-01 | [52916](https://github.com/airbytehq/airbyte/pull/52916) | Update dependencies |
| 0.1.32 | 2025-01-25 | [52196](https://github.com/airbytehq/airbyte/pull/52196) | Update dependencies |
| 0.1.31 | 2025-01-18 | [51733](https://github.com/airbytehq/airbyte/pull/51733) | Update dependencies |
| 0.1.30 | 2025-01-11 | [51272](https://github.com/airbytehq/airbyte/pull/51272) | Update dependencies |
| 0.1.29 | 2025-01-04 | [50901](https://github.com/airbytehq/airbyte/pull/50901) | Update dependencies |
| 0.1.28 | 2024-12-28 | [50439](https://github.com/airbytehq/airbyte/pull/50439) | Update dependencies |
| 0.1.27 | 2024-12-21 | [50151](https://github.com/airbytehq/airbyte/pull/50151) | Update dependencies |
| 0.1.26 | 2024-12-14 | [49030](https://github.com/airbytehq/airbyte/pull/49030) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.25 | 2024-10-28 | [47046](https://github.com/airbytehq/airbyte/pull/47046) | Update dependencies |
| 0.1.24 | 2024-10-12 | [46851](https://github.com/airbytehq/airbyte/pull/46851) | Update dependencies |
| 0.1.23 | 2024-10-05 | [46411](https://github.com/airbytehq/airbyte/pull/46411) | Update dependencies |
| 0.1.22 | 2024-09-28 | [46147](https://github.com/airbytehq/airbyte/pull/46147) | Update dependencies |
| 0.1.21 | 2024-09-21 | [45741](https://github.com/airbytehq/airbyte/pull/45741) | Update dependencies |
| 0.1.20 | 2024-09-14 | [45511](https://github.com/airbytehq/airbyte/pull/45511) | Update dependencies |
| 0.1.19 | 2024-09-07 | [45222](https://github.com/airbytehq/airbyte/pull/45222) | Update dependencies |
| 0.1.18 | 2024-08-31 | [44985](https://github.com/airbytehq/airbyte/pull/44985) | Update dependencies |
| 0.1.17 | 2024-08-24 | [44751](https://github.com/airbytehq/airbyte/pull/44751) | Update dependencies |
| 0.1.16 | 2024-08-17 | [44266](https://github.com/airbytehq/airbyte/pull/44266) | Update dependencies |
| 0.1.15 | 2024-08-12 | [43828](https://github.com/airbytehq/airbyte/pull/43828) | Update dependencies |
| 0.1.14 | 2024-08-10 | [43492](https://github.com/airbytehq/airbyte/pull/43492) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43055](https://github.com/airbytehq/airbyte/pull/43055) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42698](https://github.com/airbytehq/airbyte/pull/42698) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42155](https://github.com/airbytehq/airbyte/pull/42155) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41852](https://github.com/airbytehq/airbyte/pull/41852) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41055](https://github.com/airbytehq/airbyte/pull/41055) | Update datetime format |
| 0.1.8 | 2024-07-10 | [41460](https://github.com/airbytehq/airbyte/pull/41460) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41182](https://github.com/airbytehq/airbyte/pull/41182) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40947](https://github.com/airbytehq/airbyte/pull/40947) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40470](https://github.com/airbytehq/airbyte/pull/40470) | Update dependencies |
| 0.1.4 | 2024-06-24 | [39911](https://github.com/airbytehq/airbyte/pull/39911) | Migrate connector to low code |
| 0.1.3 | 2024-06-21 | [39923](https://github.com/airbytehq/airbyte/pull/39923) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39287](https://github.com/airbytehq/airbyte/pull/39287) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38373](https://github.com/airbytehq/airbyte/pull/38373) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-08-26 | [16051](https://github.com/airbytehq/airbyte/pull/16051) | Initial version. |

</details>
