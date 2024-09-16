# Algolia
Website: https://dashboard.algolia.com/
API Docs: https://www.algolia.com/doc/rest-api/search/
Auth Docs: https://www.algolia.com/doc/rest-api/search/#section/Authentication 
API Keys page: https://dashboard.algolia.com/account/overview

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `application_id` | `string` | Application ID. The application ID for your application found in settings |  |
| `search_query` | `string` | Indexes Search query. Search query to be used with indexes_query stream with format defined in `https://www.algolia.com/doc/rest-api/search/#tag/Search/operation/searchSingleIndex` | hitsPerPage=2&amp;getRankingInfo=1 |
| `start_date` | `string` | Start date.  |  |
| `object_id` | `string` | Object ID. Object ID within index for search queries | ecommerce-sample-data-9999996 |
| `indexes_rules_search_query` | `string` | Indexes Rules Search query. Search query to be used with indexes_rules stream with format defined in `https://www.algolia.com/doc/rest-api/search/#tag/Rules/operation/searchRules` | anchoring=contains |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| indices | name | DefaultPaginator | ✅ |  ✅  |
| indexes_query |  | No pagination | ✅ |  ❌  |
| available_languages |  | No pagination | ✅ |  ❌  |
| logs | sha1 | No pagination | ✅ |  ✅  |
| indexes_settings |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-16 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>