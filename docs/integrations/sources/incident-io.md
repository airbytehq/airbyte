# Incident.io

This is the Incident.io source connector which ingests data from the incident API.
The important streams are `incidents`, `follow-ups` and `severities`

## Prerequisites

An API key is required for authentication and using this connector. In order to obtain an API key, you must first create an Incident.io account.
You can create an account here https://incident.io/
Once you create an account and log in , you will find your API keys section in the settings sidebar under the `extends` heading. Make sure to provide all of the appropriate permissions.
You can find more about their API here https://api-docs.incident.io/

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Incdient.io** from the Source type dropdown.
3. Enter a name for your new source.
4. For **API Key**, enter your API key obtained in the previous step.
7. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.incident.io/settings/api-keys |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| actions | id | No pagination | ✅ |  ❌  |
| catalog_types | id | No pagination | ✅ |  ❌  |
| custom_fields | id | No pagination | ✅ |  ❌  |
| follow-ups | id | No pagination | ✅ |  ❌  |
| incident_roles | id | No pagination | ✅ |  ❌  |
| incident_timestamps | id | No pagination | ✅ |  ❌  |
| incident_updates | id | DefaultPaginator | ✅ |  ❌  |
| incident_statuses | id | No pagination | ✅ |  ❌  |
| workflows | id | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| severities | id | No pagination | ✅ |  ❌  |
| schedules | id | DefaultPaginator | ✅ |  ❌  |
| incidents | id | DefaultPaginator | ✅ |  ❌  |
| alerts | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date              | Pull Request | Subject        |
|---------|-------------------|--------------|----------------|
| 0.1.15 | 2025-12-09 | [70511](https://github.com/airbytehq/airbyte/pull/70511) | Update dependencies |
| 0.1.14 | 2025-11-25 | [70182](https://github.com/airbytehq/airbyte/pull/70182) | Update dependencies |
| 0.1.13 | 2025-11-18 | [69504](https://github.com/airbytehq/airbyte/pull/69504) | Update dependencies |
| 0.1.12 | 2025-10-29 | [68778](https://github.com/airbytehq/airbyte/pull/68778) | Update dependencies |
| 0.1.11 | 2025-10-21 | [68531](https://github.com/airbytehq/airbyte/pull/68531) | Update dependencies |
| 0.1.10 | 2025-10-14 | [67973](https://github.com/airbytehq/airbyte/pull/67973) | Update dependencies |
| 0.1.9 | 2025-10-07 | [67363](https://github.com/airbytehq/airbyte/pull/67363) | Update dependencies |
| 0.1.8 | 2025-09-30 | [66802](https://github.com/airbytehq/airbyte/pull/66802) | Update dependencies |
| 0.1.7 | 2025-09-09 | [66041](https://github.com/airbytehq/airbyte/pull/66041) | Update dependencies |
| 0.1.6 | 2025-09-05 | [65966](https://github.com/airbytehq/airbyte/pull/65966) | Update to CDK v7.0.0 |
| 0.1.5 | 2025-08-23 | [65332](https://github.com/airbytehq/airbyte/pull/65332) | Update dependencies |
| 0.1.4 | 2025-08-09 | [64591](https://github.com/airbytehq/airbyte/pull/64591) | Update dependencies |
| 0.1.3 | 2025-08-02 | [64299](https://github.com/airbytehq/airbyte/pull/64299) | Update dependencies |
| 0.1.2 | 2025-07-26 | [63825](https://github.com/airbytehq/airbyte/pull/63825) | Update dependencies |
| 0.1.1 | 2025-07-19 | [63480](https://github.com/airbytehq/airbyte/pull/63480) | Update dependencies |
| 0.1.0 | 2025-07-15 | [63304](https://github.com/airbytehq/airbyte/pull/63304) | Add new stream `alerts` |
| 0.0.29 | 2025-07-12 | [63128](https://github.com/airbytehq/airbyte/pull/63128) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62591](https://github.com/airbytehq/airbyte/pull/62591) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62168](https://github.com/airbytehq/airbyte/pull/62168) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61830](https://github.com/airbytehq/airbyte/pull/61830) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61149](https://github.com/airbytehq/airbyte/pull/61149) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60668](https://github.com/airbytehq/airbyte/pull/60668) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59803](https://github.com/airbytehq/airbyte/pull/59803) | Update dependencies |
| 0.0.22 | 2025-05-03 | [59231](https://github.com/airbytehq/airbyte/pull/59231) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58787](https://github.com/airbytehq/airbyte/pull/58787) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58204](https://github.com/airbytehq/airbyte/pull/58204) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57724](https://github.com/airbytehq/airbyte/pull/57724) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57094](https://github.com/airbytehq/airbyte/pull/57094) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56650](https://github.com/airbytehq/airbyte/pull/56650) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56006](https://github.com/airbytehq/airbyte/pull/56006) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55475](https://github.com/airbytehq/airbyte/pull/55475) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54780](https://github.com/airbytehq/airbyte/pull/54780) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54316](https://github.com/airbytehq/airbyte/pull/54316) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53844](https://github.com/airbytehq/airbyte/pull/53844) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53299](https://github.com/airbytehq/airbyte/pull/53299) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52718](https://github.com/airbytehq/airbyte/pull/52718) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52221](https://github.com/airbytehq/airbyte/pull/52221) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51782](https://github.com/airbytehq/airbyte/pull/51782) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51186](https://github.com/airbytehq/airbyte/pull/51186) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50648](https://github.com/airbytehq/airbyte/pull/50648) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50137](https://github.com/airbytehq/airbyte/pull/50137) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49218](https://github.com/airbytehq/airbyte/pull/49218) | Update dependencies |
| 0.0.3 | 2024-12-11 | [48989](https://github.com/airbytehq/airbyte/pull/48989) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [47842](https://github.com/airbytehq/airbyte/pull/47842) | Update dependencies |
| 0.0.1   | 2024-10-03 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
