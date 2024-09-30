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
| 0.0.1 | 2024-09-03 | [45102](https://github.com/airbytehq/airbyte/pull/45102) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>