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
10. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
4. Enter your `api_key` - Datadog API key.
5. Enter your `application_key` - Datadog application key.
6. Enter your `query` - Optional. Type your query to filter records when collecting data from Logs and AuditLogs stream.
7. Enter your `limit` - Number of records to collect per request.
8. Enter your `start_date` - Optional. Start date to filter records when collecting data from Logs and AuditLogs stream.
9. Enter your `end_date` - Optional. End date to filter records when collecting data from Logs and AuditLogs stream.
10. Click **Set up source**.

## Supported sync modes

The Datadog source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

* [AuditLogs](https://docs.datadoghq.com/api/latest/audit/#search-audit-logs-events)
* [Dashboards](https://docs.datadoghq.com/api/latest/dashboards/#get-all-dashboards)
* [Downtimes](https://docs.datadoghq.com/api/latest/downtimes/#get-all-downtimes)
* [IncidentTeams](https://docs.datadoghq.com/api/latest/incident-teams/#get-a-list-of-all-incident-teams)
* [Incidents](https://docs.datadoghq.com/api/latest/incidents/#get-a-list-of-incidents)
* [Logs](https://docs.datadoghq.com/api/latest/logs/#search-logs)
* [Metrics](https://docs.datadoghq.com/api/latest/metrics/#get-a-list-of-metrics)
* [SyntheticTests](https://docs.datadoghq.com/api/latest/synthetics/#get-the-list-of-all-tests)
* [Users](https://docs.datadoghq.com/api/latest/users/#list-all-users)

## Changelog

| Version | Date       | Pull Request                                              | Subject             |
|:--------|:-----------|:----------------------------------------------------------|:--------------------|
| 0.1.1   | 2023-04-27 | [25562](https://github.com/airbytehq/airbyte/pull/25562)  | Update testing dependencies|
| 0.1.0   | 2022-10-18 | [18150](https://github.com/airbytehq/airbyte/pull/18150)  | New Source: Datadog |
