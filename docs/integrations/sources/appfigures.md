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
| 0.0.15 | 2025-03-08 | [55384](https://github.com/airbytehq/airbyte/pull/55384) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54892](https://github.com/airbytehq/airbyte/pull/54892) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54216](https://github.com/airbytehq/airbyte/pull/54216) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53875](https://github.com/airbytehq/airbyte/pull/53875) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53443](https://github.com/airbytehq/airbyte/pull/53443) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52907](https://github.com/airbytehq/airbyte/pull/52907) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52180](https://github.com/airbytehq/airbyte/pull/52180) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51756](https://github.com/airbytehq/airbyte/pull/51756) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51231](https://github.com/airbytehq/airbyte/pull/51231) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50498](https://github.com/airbytehq/airbyte/pull/50498) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50223](https://github.com/airbytehq/airbyte/pull/50223) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49549](https://github.com/airbytehq/airbyte/pull/49549) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49003](https://github.com/airbytehq/airbyte/pull/49003) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47661](https://github.com/airbytehq/airbyte/pull/47661) | Update dependencies |
| 0.0.1 | 2024-09-08 | [45332](https://github.com/airbytehq/airbyte/pull/45332) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
