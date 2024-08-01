# Commcare

This page guides you through the process of setting up the Commcare source connector.

## Prerequisites

- Your Commcare API Key
- The Application ID you are interested in
- The start date to replicate records

## Set up the Commcare source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Commcare** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key**, enter your Commcare API Key.
6. Click **Set up source**.

## Supported sync modes

The Commcare source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Overwrite
- Incremental

## Supported Streams

The Commcare source connector supports the following streams:

- Application
- Case
- Form

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                   |
| ------- | ---------- | -------------------------------------------------------- | ------------------------- |
| 0.1.10 | 2024-07-27 | [42748](https://github.com/airbytehq/airbyte/pull/42748) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42184](https://github.com/airbytehq/airbyte/pull/42184) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41907](https://github.com/airbytehq/airbyte/pull/41907) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41512](https://github.com/airbytehq/airbyte/pull/41512) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40807](https://github.com/airbytehq/airbyte/pull/40807) | Update dependencies |
| 0.1.5 | 2024-06-26 | [40542](https://github.com/airbytehq/airbyte/pull/40542) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40325](https://github.com/airbytehq/airbyte/pull/40325) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40057](https://github.com/airbytehq/airbyte/pull/40057) | Update dependencies |
| 0.1.2 | 2024-06-04 | [39026](https://github.com/airbytehq/airbyte/pull/39026) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38519](https://github.com/airbytehq/airbyte/pull/38519) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-11-08 | [20220](https://github.com/airbytehq/airbyte/pull/20220) | Commcare Source Connector |

</details>
