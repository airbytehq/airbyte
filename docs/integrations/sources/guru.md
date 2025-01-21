# Guru

This page contains the setup guide and reference information for the [Guru](https://app.getguru.com/) source connector. 

## Prerequisites

To set up the Guru source connector, you'll need the [Guru Auth keys](https://developer.getguru.com/reference/authentication) with permissions to the resources Airbyte should be able to access.

## Set up the Greenhouse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Guru** from the Source type dropdown.
4. Enter the name for the Greenhouse connector.
5. Enter your [**Guru API Key**](https://developer.getguru.com/reference/authentication) that you obtained from Greenhouse.
6. The `USERNAME` is your `email` and `PASSWORD` is `your api_key`
6. Click **Set up source**.


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |
| `team_id` | `string` | team_id. Team ID received through response of /teams streams, make sure about access to the team |  |
| `search_cards_query` | `string` | search_cards_query. Query for searching cards |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| teams | id | DefaultPaginator | ✅ |  ✅  |
| groups | id | DefaultPaginator | ✅ |  ✅  |
| group_collection_access |  | DefaultPaginator | ✅ |  ✅  |
| group_members |  | DefaultPaginator | ✅ |  ✅  |
| members | id | DefaultPaginator | ✅ |  ✅  |
| team_analytics |  | DefaultPaginator | ✅ |  ❌  |
| collections | id | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| folder_items | id | DefaultPaginator | ✅ |  ❌  |
| folders_parent |  | DefaultPaginator | ✅ |  ❌  |
| search_cardmgr | id | DefaultPaginator | ✅ |  ✅  |
| tag_categories |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-08-31 | [45066](https://github.com/airbytehq/airbyte/pull/45066) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>