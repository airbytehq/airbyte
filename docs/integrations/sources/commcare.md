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
| 0.1.31 | 2025-02-22 | [54424](https://github.com/airbytehq/airbyte/pull/54424) | Update dependencies |
| 0.1.30 | 2025-02-15 | [53749](https://github.com/airbytehq/airbyte/pull/53749) | Update dependencies |
| 0.1.29 | 2025-02-01 | [52845](https://github.com/airbytehq/airbyte/pull/52845) | Update dependencies |
| 0.1.28 | 2025-01-25 | [52319](https://github.com/airbytehq/airbyte/pull/52319) | Update dependencies |
| 0.1.27 | 2025-01-18 | [51097](https://github.com/airbytehq/airbyte/pull/51097) | Update dependencies |
| 0.1.26 | 2024-12-28 | [50509](https://github.com/airbytehq/airbyte/pull/50509) | Update dependencies |
| 0.1.25 | 2024-12-21 | [50064](https://github.com/airbytehq/airbyte/pull/50064) | Update dependencies |
| 0.1.24 | 2024-12-14 | [49172](https://github.com/airbytehq/airbyte/pull/49172) | Update dependencies |
| 0.1.23 | 2024-11-25 | [48645](https://github.com/airbytehq/airbyte/pull/48645) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.22 | 2024-10-29 | [47767](https://github.com/airbytehq/airbyte/pull/47767) | Update dependencies |
| 0.1.21 | 2024-10-28 | [46795](https://github.com/airbytehq/airbyte/pull/46795) | Update dependencies |
| 0.1.20 | 2024-10-05 | [46413](https://github.com/airbytehq/airbyte/pull/46413) | Update dependencies |
| 0.1.19 | 2024-09-28 | [46163](https://github.com/airbytehq/airbyte/pull/46163) | Update dependencies |
| 0.1.18 | 2024-09-21 | [45758](https://github.com/airbytehq/airbyte/pull/45758) | Update dependencies |
| 0.1.17 | 2024-09-14 | [45549](https://github.com/airbytehq/airbyte/pull/45549) | Update dependencies |
| 0.1.16 | 2024-09-07 | [45266](https://github.com/airbytehq/airbyte/pull/45266) | Update dependencies |
| 0.1.15 | 2024-08-31 | [45038](https://github.com/airbytehq/airbyte/pull/45038) | Update dependencies |
| 0.1.14 | 2024-08-24 | [44714](https://github.com/airbytehq/airbyte/pull/44714) | Update dependencies |
| 0.1.13 | 2024-08-17 | [44261](https://github.com/airbytehq/airbyte/pull/44261) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43590](https://github.com/airbytehq/airbyte/pull/43590) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43193](https://github.com/airbytehq/airbyte/pull/43193) | Update dependencies |
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
