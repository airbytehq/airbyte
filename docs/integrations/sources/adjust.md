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

| Version | Date       | Pull Request                                             | Subject          |
| ------- | ---------- | -------------------------------------------------------- | ---------------- |
| 0.1.2 | 2024-06-06 | [39287](https://github.com/airbytehq/airbyte/pull/39287) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38373](https://github.com/airbytehq/airbyte/pull/38373) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-08-26 | [16051](https://github.com/airbytehq/airbyte/pull/16051) | Initial version. |

</details>
