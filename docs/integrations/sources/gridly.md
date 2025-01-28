# Gridly

This page contains the setup guide and reference information for the Gridly source connector.

## Prerequisites

- Access to an active Gridly account
- API Key (requires Owner or Administrator access)

## Setup guide

### Find your API Key

1. Access your Gridly Dashboard
2. Select **[API]**. The API key will be shown in the API Quickstart panel.
2. Owner and Administrators can also go to their **Settings** and then **API Keys** to create company-level API keys with scoped privileges and accesses.

### Find the Grid ID

1. `Grid ID` is available in the URL when accessing the Grid in the UI. The Grid ID is the ID following `/grids/` in the URL.
2. `Branch ID` is by default the same as the `Grid ID` when the `Master` branch is selected. To fetch records on other branches, use `Branch ID` instead.

## Supported sync modes

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Supported Streams

- [Records](https://www.gridly.com/docs/api/#record)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                     |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------- |
| 0.1.28 | 2025-01-25 | [51796](https://github.com/airbytehq/airbyte/pull/51796) | Update dependencies |
| 0.1.27 | 2025-01-11 | [51195](https://github.com/airbytehq/airbyte/pull/51195) | Update dependencies |
| 0.1.26 | 2024-12-28 | [50663](https://github.com/airbytehq/airbyte/pull/50663) | Update dependencies |
| 0.1.25 | 2024-12-21 | [50085](https://github.com/airbytehq/airbyte/pull/50085) | Update dependencies |
| 0.1.24 | 2024-12-14 | [49000](https://github.com/airbytehq/airbyte/pull/49000) | Update dependencies |
| 0.1.23 | 2024-11-25 | [48675](https://github.com/airbytehq/airbyte/pull/48675) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.22 | 2024-10-28 | [47075](https://github.com/airbytehq/airbyte/pull/47075) | Update dependencies |
| 0.1.21 | 2024-10-12 | [46476](https://github.com/airbytehq/airbyte/pull/46476) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46122](https://github.com/airbytehq/airbyte/pull/46122) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45723](https://github.com/airbytehq/airbyte/pull/45723) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45529](https://github.com/airbytehq/airbyte/pull/45529) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45314](https://github.com/airbytehq/airbyte/pull/45314) | Update dependencies |
| 0.1.16 | 2024-08-31 | [44949](https://github.com/airbytehq/airbyte/pull/44949) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44750](https://github.com/airbytehq/airbyte/pull/44750) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44320](https://github.com/airbytehq/airbyte/pull/44320) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43668](https://github.com/airbytehq/airbyte/pull/43668) | Update dependencies |
| 0.1.12 | 2024-08-03 | [42662](https://github.com/airbytehq/airbyte/pull/42662) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42173](https://github.com/airbytehq/airbyte/pull/42173) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41768](https://github.com/airbytehq/airbyte/pull/41768) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41376](https://github.com/airbytehq/airbyte/pull/41376) | Update dependencies |
| 0.1.8 | 2024-07-09 | [41163](https://github.com/airbytehq/airbyte/pull/41163) | Update dependencies |
| 0.1.7 | 2024-07-06 | [40908](https://github.com/airbytehq/airbyte/pull/40908) | Update dependencies |
| 0.1.6 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.1.5 | 2024-06-25 | [40495](https://github.com/airbytehq/airbyte/pull/40495) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39982](https://github.com/airbytehq/airbyte/pull/39982) | Update dependencies |
| 0.1.3 | 2024-06-04 | [39051](https://github.com/airbytehq/airbyte/pull/39051) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-21 | [38542](https://github.com/airbytehq/airbyte/pull/38542) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-12-08 | [20048](https://github.com/airbytehq/airbyte/pull/20048) | Source Gridly: add icon and make grid_id parameter required |

</details>
