# Reddit Ads
This PR adds a new connector for source Reddit Ads (source-reddit-ads)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `account_id` | `string` | account_id.  |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ad_account | id.business_id.name | DefaultPaginator | ✅ |  ❌  |
| businesses |  | DefaultPaginator | ✅ |  ❌  |
| ad_groups |  | DefaultPaginator | ✅ |  ❌  |
| ads |  | DefaultPaginator | ✅ |  ❌  |
| get_business |  | DefaultPaginator | ✅ |  ❌  |
| industries |  | DefaultPaginator | ✅ |  ❌  |
| my_businesses |  | DefaultPaginator | ✅ |  ❌  |
| campaigns |  | DefaultPaginator | ✅ |  ❌  |
| custom_audiences |  | DefaultPaginator | ✅ |  ❌  |
| lead_gen_forms |  | DefaultPaginator | ✅ |  ❌  |
| me | id | DefaultPaginator | ✅ |  ❌  |
| posts |  | DefaultPaginator | ✅ |  ❌  |
| carriers |  | DefaultPaginator | ✅ |  ❌  |
| communities |  | DefaultPaginator | ✅ |  ❌  |
| search |  | DefaultPaginator | ✅ |  ❌  |
| suggestions |  | DefaultPaginator | ✅ |  ❌  |
| devices |  | No pagination | ✅ |  ❌  |
| geolocations |  | DefaultPaginator | ✅ |  ❌  |
| interests |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-21 | | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
