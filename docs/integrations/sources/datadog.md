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
4. Proceed with remaining configuration below
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key` - Datadog API key.
<<<<<<< dlecocq/source-datadog-slo-history
4. Click **Set up source**.

### Configuration

1. Configure access by selecting your `site`, and entering `api_key`, `application_key`. Here is also where you can configure the maximum number of records to consume in a single REST request.
2. Configure incremental parameters, including the `start_date` and `end_date`. The start date represents the earliest time for which data will be collected, and `end_date` represents the latest. If the `end_date` is left blank, it will use `now`.
3. Configure optional `monitors` parameters if you intend to consume that stream. All parameters have the same meaning as in the DataDog [monitors endpoint](https://docs.datadoghq.com/api/latest/monitors/#get-all-monitor-details).
4. Configure optional `logs` parameters if you intend to consume that stream. All parameters have the same meaning as in the DataDog [logs endpoint](https://docs.datadoghq.com/api/latest/logs/#get-a-list-of-logs).
4. Configure optional `service level objectives` parameters if you intend to consume that stream _or_ if you intend to consume the `service level objectives history` stream. All parameters have the same meaning as in the DataDog [service level objectives endpoint](https://docs.datadoghq.com/api/latest/service-level-objectives/#get-all-slos).
5. Configure optional `service level objectives_history` parameters if you intend to consume that stream. The set of SLOs for which history is collected is determined by the `service level objectives` stream configuration. All parameters have the same meaning as in the DataDog [service level objectives history endpoint](https://docs.datadoghq.com/api/latest/service-level-objectives/#get-an-slos-history).
=======
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
>>>>>>> master

## Supported sync modes

The Datadog source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

<<<<<<< dlecocq/source-datadog-slo-history
* [AuditLogs](https://docs.datadoghq.com/api/latest/audit/#search-audit-logs-events)
* [Dashboards](https://docs.datadoghq.com/api/latest/dashboards/#get-all-dashboards)
* [Downtimes](https://docs.datadoghq.com/api/latest/downtimes/#get-all-downtimes)
* [IncidentTeams](https://docs.datadoghq.com/api/latest/incident-teams/#get-a-list-of-all-incident-teams)
* [Incidents](https://docs.datadoghq.com/api/latest/incidents/#get-a-list-of-incidents)
* [Logs](https://docs.datadoghq.com/api/latest/logs/#search-logs)
* [Metrics](https://docs.datadoghq.com/api/latest/metrics/#get-a-list-of-metrics)
* [Monitors](https://docs.datadoghq.com/api/latest/monitors/#get-all-monitor-details)
* [ServiceLevelObjectives](https://docs.datadoghq.com/api/latest/service-level-objectives/#get-all-slos)
* [ServiceLevelObjectivesHistory](https://docs.datadoghq.com/api/latest/service-level-objectives/#get-an-slos-history)
* [SyntheticTests](https://docs.datadoghq.com/api/latest/synthetics/#get-the-list-of-all-tests)
* [Users](https://docs.datadoghq.com/api/latest/users/#list-all-users)
* [Series](https://docs.datadoghq.com/api/latest/metrics/?code-lang=curl#query-timeseries-data-across-multiple-products)
=======
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
>>>>>>> master

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------- |
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