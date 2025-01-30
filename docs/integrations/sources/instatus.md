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
| 0.2.1 | 2025-01-25 | [52230](https://github.com/airbytehq/airbyte/pull/52230) | Update dependencies |
| 0.2.0 | 2025-01-14 | [47242](https://github.com/airbytehq/airbyte/pull/47242) | Migrate to manifest-only format |
| 0.1.29 | 2025-01-11 | [51197](https://github.com/airbytehq/airbyte/pull/51197) | Update dependencies |
| 0.1.28 | 2025-01-04 | [50887](https://github.com/airbytehq/airbyte/pull/50887) | Update dependencies |
| 0.1.27 | 2024-12-28 | [50609](https://github.com/airbytehq/airbyte/pull/50609) | Update dependencies |
| 0.1.26 | 2024-12-21 | [50076](https://github.com/airbytehq/airbyte/pull/50076) | Update dependencies |
| 0.1.25 | 2024-12-14 | [49268](https://github.com/airbytehq/airbyte/pull/49268) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.24 | 2024-12-12 | [49147](https://github.com/airbytehq/airbyte/pull/49147) | Update dependencies |
| 0.1.23 | 2024-10-28 | [47027](https://github.com/airbytehq/airbyte/pull/47027) | Update dependencies |
| 0.1.22 | 2024-10-12 | [46843](https://github.com/airbytehq/airbyte/pull/46843) | Update dependencies |
| 0.1.21 | 2024-10-05 | [46484](https://github.com/airbytehq/airbyte/pull/46484) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46115](https://github.com/airbytehq/airbyte/pull/46115) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45731](https://github.com/airbytehq/airbyte/pull/45731) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45514](https://github.com/airbytehq/airbyte/pull/45514) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45275](https://github.com/airbytehq/airbyte/pull/45275) | Update dependencies |
| 0.1.16 | 2024-08-31 | [44990](https://github.com/airbytehq/airbyte/pull/44990) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44634](https://github.com/airbytehq/airbyte/pull/44634) | Update dependencies |
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
