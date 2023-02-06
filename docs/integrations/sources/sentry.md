# Sentry

This page contains the setup guide and reference information for the Sentry source connector.

## Prerequisites

To set up the Sentry source connector, you'll need the Sentry [project name](https://docs.sentry.io/product/projects/), [authentication token](https://docs.sentry.io/api/auth/#auth-tokens), and [organization](https://docs.sentry.io/product/accounts/membership/).

## Set up the Sentry connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Sentry** from the Source type dropdown.
4. Enter the name for the Sentry connector.
5. For **Project**, enter the name of the [Sentry project](https://docs.sentry.io/product/projects/) you want to sync.
6. For **Host Name**, enter the host name of your self-hosted Sentry API Server. If your server isn't self-hosted, leave the field blank.
7. For **Authentication Tokens**, enter the [Sentry authentication token](https://docs.sentry.io/api/auth/#auth-tokens).
8. For **Organization**, enter the [Sentry Organization](https://docs.sentry.io/product/accounts/membership/) the groups belong to.
9. Click **Set up source**.

## Supported sync modes

The Sentry source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

* [Events](https://docs.sentry.io/api/events/list-a-projects-events/)
* [Issues](https://docs.sentry.io/api/events/list-a-projects-issues/)

## Data type map

| Integration Type    | Airbyte Type |
| :------------------ | :----------- |
| `string`            | `string`     |
| `integer`, `number` | `number`     |
| `array`             | `array`      |
| `object`            | `object`     |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------|
| 0.1.10  | 2023-01-27 | [22041](https://github.com/airbytehq/airbyte/pull/22041) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| 0.1.9   | 2022-12-20 | [21864](https://github.com/airbytehq/airbyte/pull/21864) | Add state persistence to incremental sync         |
| 0.1.8   | 2022-12-20 | [20709](https://github.com/airbytehq/airbyte/pull/20709) | Add incremental sync                              |
| 0.1.7   | 2022-09-30 | [17466](https://github.com/airbytehq/airbyte/pull/17466) | Migrate to per-stream states                      |
| 0.1.6   | 2022-08-29 | [16112](https://github.com/airbytehq/airbyte/pull/16112) | Revert back to the Python CDK                     |
| 0.1.5   | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime     |
| 0.1.4   | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime    |
| 0.1.3   | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator        |
| 0.1.2   | 2021-12-28 | [15345](https://github.com/airbytehq/airbyte/pull/15345) | Migrate to config-based framework                 |
| 0.1.1   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications |
| 0.1.0   | 2021-10-12 | [6975](https://github.com/airbytehq/airbyte/pull/6975)   | New Source: Sentry                                |
