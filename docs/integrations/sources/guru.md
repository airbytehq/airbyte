# Guru
New source: Guru
API Documentation: https://developer.getguru.com/reference/authentication
Website: https://app.getguru.com/

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

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-31 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>