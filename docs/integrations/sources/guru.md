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
| 0.0.10 | 2025-01-11 | [51188](https://github.com/airbytehq/airbyte/pull/51188) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50622](https://github.com/airbytehq/airbyte/pull/50622) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50118](https://github.com/airbytehq/airbyte/pull/50118) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49622](https://github.com/airbytehq/airbyte/pull/49622) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49271](https://github.com/airbytehq/airbyte/pull/49271) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48903](https://github.com/airbytehq/airbyte/pull/48903) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48152](https://github.com/airbytehq/airbyte/pull/48152) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47830](https://github.com/airbytehq/airbyte/pull/47830) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47665](https://github.com/airbytehq/airbyte/pull/47665) | Update dependencies |
| 0.0.1 | 2024-08-31 | [45066](https://github.com/airbytehq/airbyte/pull/45066) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
