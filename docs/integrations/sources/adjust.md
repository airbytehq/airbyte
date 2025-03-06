# Adjust

This is a setup guide for the Adjust source connector which ingests data from the reports API.

## Prerequisites

An API token is required to get hold of reports from the Adjust reporting API. See the [Adjust API authentication help article](https://help.adjust.com/en/article/report-service-api-authentication) on how to obtain a key.

As Adjust allows you to setup custom events etc that are specific to your apps, only a subset of available metrics are made pre-selectable. To list all metrics that are available, query the filters data endpoint. Information about available metrics are available in the [Datascape metrics glossary](https://help.adjust.com/en/article/datascape-metrics-glossary).

### Full Metrics Listing

Take a look at the [filters data endpoint documentation](https://help.adjust.com/en/article/filters-data-endpoint) to see available filters. The example below shows how to obtain the events that are defined for your apps (replace the `API_KEY` with the key obtained in the previous step):

```sh
curl --header 'Authorization: Bearer API_KEY' 'https://dash.adjust.com/control-center/reports-service/filters_data?required_filters=event_metrics' | jq
```

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Adjust** from the Source type dropdown.
3. Enter a name for your new source.
4. For **API Token**, enter your API key obtained in the previous step.
5. For **Ingestion Start Date**, enter a date in YYYY-MM-DD format (UTC timezone is assumed). Data starting from this date will be replicated.
6. In the **Metrics to Ingest** field, select the metrics of interest to query.
7. Enter any additional, custom metrics, to query in the **Additional Metrics** box. Available metrics can be listed as described in the Prerequisites section. These selected metrics are assumed to be decimal values.
8. In the **Dimensions** field, select the dimensions to group metrics by.
9. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|---------|------------| -------------------------------------------------------- |---------------------------------------------|
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
