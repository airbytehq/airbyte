# Reddit Ads
This PR adds a new connector for source Reddit Ads (source-reddit-ads)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |
| `account_id` | `string` | account_id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ad_account | id.business_id.name | No pagination | ✅ |  ❌  |
| businesses |  | DefaultPaginator | ✅ |  ❌  |
| ad_groups |  | DefaultPaginator | ✅ |  ❌  |
| ads |  | DefaultPaginator | ✅ |  ❌  |
| get_business |  | No pagination | ✅ |  ❌  |
| industries |  | No pagination | ✅ |  ❌  |
| my_businesses |  | DefaultPaginator | ✅ |  ❌  |
| campaigns |  | DefaultPaginator | ✅ |  ❌  |
| custom_audiences |  | DefaultPaginator | ✅ |  ❌  |
| lead_gen_forms |  | DefaultPaginator | ✅ |  ❌  |
| me | id | No pagination | ✅ |  ❌  |
| posts |  | DefaultPaginator | ✅ |  ❌  |
| carriers |  | DefaultPaginator | ✅ |  ❌  |
| communities |  | DefaultPaginator | ✅ |  ❌  |
| search |  | DefaultPaginator | ✅ |  ❌  |
| suggestions |  | DefaultPaginator | ✅ |  ❌  |
| devices |  | DefaultPaginator | ✅ |  ❌  |
| geolocations |  | No pagination | ✅ |  ❌  |
| interests |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-11 | [47213] (https://github.com/airbytehq/airbyte/pull/47213) | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
