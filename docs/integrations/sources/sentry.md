# Sentry

This page contains the setup guide and reference information for the Sentry source connector.

## Prerequisites

You can find or create authentication tokens within [Sentry](https://sentry.io/settings/account/api/auth-tokens/).

## Setup guide
## Step 1: Set up the Sentry connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Sentry connector and select **Sentry** from the Source type dropdown.
4. Enter your `auth_token` - Sentry Authentication Token with the necessary permissions \(described below\).
4. Enter your `organization` - Organization Slug. You can check it at https://sentry.io/settings/$YOUR_ORG_HERE/.
4. Enter your `project` - The name of the Project you wanto sync. You can list it from https://sentry.io/settings/$YOUR_ORG_HERE/projects/.
4. Enter your `hostname` - Host name of Sentry API server. For self-hosted, specify your host name here. Otherwise, leave it empty. \(default: sentry.io\).
8. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
3. Enter your `auth_token` - Sentry Authentication Token with the necessary permissions \(described below\).
4. Enter your `organization` - Organization Slug. You can check it at https://sentry.io/settings/$YOUR_ORG_HERE/.
5. Enter your `project` - The name of the Project you wanto sync. You can list it from https://sentry.io/settings/$YOUR_ORG_HERE/projects/.
6. Enter your `hostname` - Host name of Sentry API server. For self-hosted, specify your host name here. Otherwise, leave it empty. \(default: sentry.io\).
7. Click **Set up source**.

## Supported sync modes

The Sentry source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

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
|:--------| :--------- | :------------------------------------------------------- |:--------------------------------------------------|
| 0.1.5   | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime     |
| 0.1.4   | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime    |
| 0.1.3   | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator        |
| 0.1.2   | 2021-12-28 | [15345](https://github.com/airbytehq/airbyte/pull/15345) | Migrate to config-based framework                 |
| 0.1.1   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628)   | Update fields in source-connectors specifications |
| 0.1.0   | 2021-10-12 | [6975](https://github.com/airbytehq/airbyte/pull/6975)   | New Source: Sentry                                |
