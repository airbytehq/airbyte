# Prometheus

This page contains the setup guide and reference information for the Prometheus source connector.

## Prerequisites

- Prometheus endpoint
- Basic auth credentials for protected Prometheus instances
- Start date
- Step

## Setup guide

### Step 1: (Optional) Create a dedicated user

We recommend creating a dedicated user for better permission control and auditing. Prometheus provides an [authentication mechanism](https://prometheus.io/docs/guides/basic-auth/) but a reverse proxy can be used.

### Step 2: Set up the Prometheus connector in Airbyte

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Prometheus** from the Source type dropdown.
4. Enter a name for your source.
5. For the **base_url**, enter Prometheus endpoint URL.
6. Set the **Basic Auth Username** and **Basic Auth Password** credentials.
7. Enter **Start date** in YYYY-MM-DD format. The data added on and after this date will be replicated.
8. Enter the **Step** resolution. For example, "3600" will export one data point per hour per Prometheus series.

## Supported sync modes

The Prometheus source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

A stream will be created for each Prometheus metric. Your Prometheus instance might expose hundreds of metrics, but for most Airbyte users, only a bunch of them will be useful.

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                |
| :------ | :--------- | :------------------------------------------------------- | :--------------------- |
| 0.0.1   | 2023-07-29 | [27716](https://github.com/airbytehq/airbyte/pull/28840) | Initial implementation |