# Appcues

This page guides you through setting up the Appcues source connector to sync data for the [Appcues](https://studio.appcues.com). 
Visit `https://api.appcues.com/v2/docs` for referencing API documentation.

## Prerequisite

To set up the Appcues source connector, you'll need your Appcues [`API Key` and `API secret`](https://studio.appcues.com/settings/keys).

## Set up the Appcues source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Appcues** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key** and **Secret Key**, enter the Appcues [API key and API secret key](https://studio.appcues.com/settings/keys).
6. For **Replication Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. Click **Set up source**.


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `account_id` | `string` | Account ID. Account ID of Appcues found in account settings page (https://studio.appcues.com/settings/account) |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| launchpads | id | No pagination | ✅ |  ✅  |
| flows | id | No pagination | ✅ |  ✅  |
| banners | id | No pagination | ✅ |  ✅  |
| checklists | id | No pagination | ✅ |  ✅  |
| pins | id | No pagination | ✅ |  ✅  |
| tags | id | No pagination | ✅ |  ✅  |
| segments | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | ----- | ---------------- |
| 0.0.9 | 2025-01-11 | [51260](https://github.com/airbytehq/airbyte/pull/51260) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50451](https://github.com/airbytehq/airbyte/pull/50451) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50174](https://github.com/airbytehq/airbyte/pull/50174) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49586](https://github.com/airbytehq/airbyte/pull/49586) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49277](https://github.com/airbytehq/airbyte/pull/49277) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48931](https://github.com/airbytehq/airbyte/pull/48931) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48267](https://github.com/airbytehq/airbyte/pull/48267) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47771](https://github.com/airbytehq/airbyte/pull/47771) | Update dependencies |
| 0.0.1 | 2024-09-03 | [45102](https://github.com/airbytehq/airbyte/pull/45102) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
