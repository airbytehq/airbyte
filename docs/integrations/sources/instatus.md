# Instatus

This page contains the setup guide and reference information for the Instatus source connector.

## Prerequisites

To set up Metabase you need:

- `api_key` - Requests to Instatus API must provide an API token.

## Setup guide

### Step 1: Set up Instatus account

### Step 2: Generate an API key

You can get your API key from [User settings](https://dashboard.instatus.com/developer)
Make sure that you are an owner of the pages you want to sync because if you are not this data will be skipped.

### Step 2: Set up the Instatus connector in Airbyte

## Supported sync modes

The Instatus source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)

## Supported Streams

- [Status pages](https://instatus.com/help/api/status-pages)
- [Components](https://instatus.com/help/api/components)
- [Incidents](https://instatus.com/help/api/incidents)
- [Incident updates](https://instatus.com/help/api/incident-updates)
- [Maintenances](https://instatus.com/help/api/maintenances)
- [Maintenance updates](https://instatus.com/help/api/maintenance-updates)
- [Templates](https://instatus.com/help/api/templates)
- [Team](https://instatus.com/help/api/teammates)
- [Subscribers](https://instatus.com/help/api/subscribers)
- [Metrics](https://instatus.com/help/api/metrics)
- [User](https://instatus.com/help/api/user-profile)
- [Public data](https://instatus.com/help/api/public-data)

## Tutorials

### Data type mapping

| Integration Type    | Airbyte Type | Notes |
| :------------------ | :----------- | :---- |
| `string`            | `string`     |       |
| `integer`, `number` | `number`     |       |
| `array`             | `array`      |       |
| `object`            | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| SSL connection    | Yes                  |
| Namespaces        | No                   |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------- |
| 0.1.14 | 2024-08-17 | [44241](https://github.com/airbytehq/airbyte/pull/44241) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43747](https://github.com/airbytehq/airbyte/pull/43747) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43495](https://github.com/airbytehq/airbyte/pull/43495) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43135](https://github.com/airbytehq/airbyte/pull/43135) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42724](https://github.com/airbytehq/airbyte/pull/42724) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42208](https://github.com/airbytehq/airbyte/pull/42208) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41779](https://github.com/airbytehq/airbyte/pull/41779) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41549](https://github.com/airbytehq/airbyte/pull/41549) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41115](https://github.com/airbytehq/airbyte/pull/41115) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40872](https://github.com/airbytehq/airbyte/pull/40872) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40425](https://github.com/airbytehq/airbyte/pull/40425) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40179](https://github.com/airbytehq/airbyte/pull/40179) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39167](https://github.com/airbytehq/airbyte/pull/39167) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38506](https://github.com/airbytehq/airbyte/pull/38506) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2023-04-01 | [21008](https://github.com/airbytehq/airbyte/pull/21008) | Initial (alpha) release |

</details>
