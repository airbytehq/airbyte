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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-03 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
