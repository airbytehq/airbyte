# Datadog

This is a setup guide for the Datadog source connector which collects data from [its API](https://docs.datadoghq.com/api/latest/).

## Prerequisites

An API key is required as well as an API application key. See the [Datadog API and Application Keys section](https://docs.datadoghq.com/account_management/api-app-keys/) for more information.

## Setup guide

## Step 1: Set up the Datadog connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Datadog connector and select **Datadog** from the Source type dropdown.
4. Enter your `api_key` - Datadog API key.
5. Enter your `application_key` - Datadog application key.
6. Enter your `query` - Optional. Type your query to filter records when collecting data from Logs and AuditLogs stream.
7. Enter your `limit` - Number of records to collect per request.
8. Enter your `start_date` - Optional. Start date to filter records when collecting data from Logs and AuditLogs stream.
9. Enter your `end_date` - Optional. End date to filter records when collecting data from Logs and AuditLogs stream.
10. Enter your `queries` - Optional. Multiple queries resulting in multiple streams.
    1. Enter the `name`- Optional. Query Name.
    2. Select the `data_source` from dropdown - Optional. Supported data sources - metrics, cloud_cost, logs, rum.
    3. Enter the `query`- Optional. A classic query string. Example - `"kubernetes_state.node.count{*}"`, `"@type:resource @resource.status_code:>=400 @resource.type:(xhr OR fetch)"`
11. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key` - Datadog API key.
4. Enter your `application_key` - Datadog application key.
5. Enter your `query` - Optional. Type your query to filter records when collecting data from Logs and AuditLogs stream.
6. Enter your `limit` - Number of records to collect per request.
7. Enter your `start_date` - Optional. Start date to filter records when collecting data from Logs and AuditLogs stream.
8. Enter your `end_date` - Optional. End date to filter records when collecting data from Logs and AuditLogs stream.
9. Enter your `queries` - Optional. Multiple queries resulting in multiple streams.
   1. Enter the `name`- Required. Query Name.
   2. Select the `data_source` - Required. Supported data sources - metrics, cloud_cost, logs, rum.
   3. Enter the `query`- Required. A classic query string. Example - `"kubernetes_state.node.count{*}"`, `"@type:resource @resource.status_code:>=400 @resource.type:(xhr OR fetch)"`
10. Click **Set up source**.

## Supported sync modes

The Datadog source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

- [AuditLogs](https://docs.datadoghq.com/api/latest/audit/#search-audit-logs-events)
- [Dashboards](https://docs.datadoghq.com/api/latest/dashboards/#get-all-dashboards)
- [Downtimes](https://docs.datadoghq.com/api/latest/downtimes/#get-all-downtimes)
- [IncidentTeams](https://docs.datadoghq.com/api/latest/incident-teams/#get-a-list-of-all-incident-teams)
- [Incidents](https://docs.datadoghq.com/api/latest/incidents/#get-a-list-of-incidents)
- [Logs](https://docs.datadoghq.com/api/latest/logs/#search-logs)
- [Metrics](https://docs.datadoghq.com/api/latest/metrics/#get-a-list-of-metrics)
- [Monitors](https://docs.datadoghq.com/api/latest/monitors/#get-all-monitor-details)
- [ServiceLevelObjectives](https://docs.datadoghq.com/api/latest/service-level-objectives/#get-all-slos)
- [SyntheticTests](https://docs.datadoghq.com/api/latest/synthetics/#get-the-list-of-all-tests)
- [Users](https://docs.datadoghq.com/api/latest/users/#list-all-users)
- [Series](https://docs.datadoghq.com/api/latest/metrics/?code-lang=curl#query-timeseries-data-across-multiple-products)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                      |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------|
| 1.0.2 | 2024-08-31 | [44992](https://github.com/airbytehq/airbyte/pull/44992) | Update dependencies |
| 1.0.1 | 2024-08-24 | [44706](https://github.com/airbytehq/airbyte/pull/44706) | Update dependencies |
| 1.0.0 | 2024-08-19 | [44371](https://github.com/airbytehq/airbyte/pull/44371) | Update CDK version and dependencies, remove parameters and migrate to inline schemas |
| 0.4.15 | 2024-08-17 | [44313](https://github.com/airbytehq/airbyte/pull/44313) | Update dependencies |
| 0.4.14 | 2024-08-12 | [43741](https://github.com/airbytehq/airbyte/pull/43741) | Update dependencies |
| 0.4.13 | 2024-08-10 | [43555](https://github.com/airbytehq/airbyte/pull/43555) | Update dependencies |
| 0.4.12 | 2024-08-03 | [43141](https://github.com/airbytehq/airbyte/pull/43141) | Update dependencies |
| 0.4.11 | 2024-07-27 | [42776](https://github.com/airbytehq/airbyte/pull/42776) | Update dependencies |
| 0.4.10 | 2024-07-20 | [42341](https://github.com/airbytehq/airbyte/pull/42341) | Update dependencies |
| 0.4.9 | 2024-07-13 | [41783](https://github.com/airbytehq/airbyte/pull/41783) | Update dependencies |
| 0.4.8 | 2024-07-10 | [41416](https://github.com/airbytehq/airbyte/pull/41416) | Update dependencies |
| 0.4.7 | 2024-07-09 | [41168](https://github.com/airbytehq/airbyte/pull/41168) | Update dependencies |
| 0.4.6 | 2024-07-06 | [40985](https://github.com/airbytehq/airbyte/pull/40985) | Update dependencies |
| 0.4.5 | 2024-06-25 | [40306](https://github.com/airbytehq/airbyte/pull/40306) | Update dependencies |
| 0.4.4 | 2024-06-22 | [40063](https://github.com/airbytehq/airbyte/pull/40063) | Update dependencies |
| 0.4.3 | 2024-06-13 | [37590](https://github.com/airbytehq/airbyte/pull/37590) | Change `last_records` to `last_record` |
| 0.4.2 | 2024-06-04 | [39060](https://github.com/airbytehq/airbyte/pull/39060) | [autopull] Upgrade base image to v1.2.1 |
| 0.4.1 | 2024-05-20 | [38424](https://github.com/airbytehq/airbyte/pull/38424) | [autopull] base image + poetry + up_to_date |
| 0.4.0 | 2023-12-04 | [30999](https://github.com/airbytehq/airbyte/pull/30999) | Add `monitors` and `service_level_objectives` Streams |
| 0.3.0 | 2023-08-27 | [29885](https://github.com/airbytehq/airbyte/pull/29885) | Migrate to low code |
| 0.2.2 | 2023-07-10 | [28089](https://github.com/airbytehq/airbyte/pull/28089) | Additional stream and query details in response |
| 0.2.1 | 2023-06-28 | [26534](https://github.com/airbytehq/airbyte/pull/26534) | Support multiple query streams and pulling data from different datadog sites |
| 0.2.0 | 2023-06-28 | [27784](https://github.com/airbytehq/airbyte/pull/27784) | Add necessary fields to schemas |
| 0.1.1 | 2023-04-27 | [25562](https://github.com/airbytehq/airbyte/pull/25562) | Update testing dependencies |
| 0.1.0 | 2022-10-18 | [18150](https://github.com/airbytehq/airbyte/pull/18150) | New Source: Datadog |

</details>
