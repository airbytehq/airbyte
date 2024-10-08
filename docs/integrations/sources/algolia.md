# Algolia
This page contains the setup guide and reference information for the [Algolia](https://dashboard.algolia.com/) source connector.

## Documentation reference:
Visit `https://www.algolia.com/doc/rest-api/search/` for API documentation

## Authentication setup
`Source-algolia` uses API keys and application id for its authentication,
Visit `https://dashboard.algolia.com/account/overview` for getting credentials and application id.
Visit `https://www.algolia.com/doc/rest-api/search/#section/Authentication` for more about authentication.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `application_id` | `string` | Application ID. The application ID for your application found in settings |  |
| `search_query` | `string` | Indexes Search query. Search query to be used with indexes_query stream with format defined in `https://www.algolia.com/doc/rest-api/search/#tag/Search/operation/searchSingleIndex` | hitsPerPage=2&amp;getRankingInfo=1 |
| `start_date` | `string` | Start date.  |  |
| `object_id` | `string` | Object ID. Object ID within index for search queries | ecommerce-sample-data-9999996 |

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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-16 | [45605](https://github.com/airbytehq/airbyte/pull/45605) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>