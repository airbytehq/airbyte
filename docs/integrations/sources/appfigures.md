# Appfigures
This page contains the setup guide and reference information for the [Appfigures](https://appfigures.com/) source connector.

## Documentation reference:
Visit `https://docs.appfigures.com/api/reference/v2/` for API documentation

## Authentication setup
Appfigures uses personal access token as API Key Authorization, Please visit `https://appfigures.com/account/apis` for getting your API tokens
Refer `https://docs.appfigures.com/api/reference/v2/authentication` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `search_store` | `string` | Search Store. The store which needs to be searched in streams | apple |
| `start_date` | `string` | Start date.  |  |
| `group_by` | `string` | Group by. Category term for grouping the search results | product |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| status | id | No pagination | ✅ |  ❌  |
| reports_sales |  | No pagination | ✅ |  ❌  |
| data_categories |  | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| usage |  | DefaultPaginator | ✅ |  ❌  |
| products_mine_search |  | DefaultPaginator | ✅ |  ❌  |
| reports_revenue |  | No pagination | ✅ |  ❌  |
| reports_subscriptions |  | No pagination | ✅ |  ❌  |
| reports_ads |  | No pagination | ✅ |  ❌  |
| reports_adspend |  | No pagination | ✅ |  ❌  |
| reports_ratings |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | -- | ---------------- |
| 0.0.1 | 2024-09-08 | [45332](https://github.com/airbytehq/airbyte/pull/45332) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>