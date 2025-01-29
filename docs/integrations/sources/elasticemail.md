# Elasticemail
Elasticemail is an email delivery and marketing platform.
Using this connector we extract data from streams such as campaigns , contacts , lists and statistics!
Docs : https://elasticemail.com/developers/api-documentation/rest-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `scope_type` | `string` | scope type.  |  |
| `from` | `string` | From.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | Name | DefaultPaginator | ✅ |  ❌  |
| contacts | Email | DefaultPaginator | ✅ |  ❌  |
| events |  | DefaultPaginator | ✅ |  ✅  |
| files |  | DefaultPaginator | ✅ |  ❌  |
| inboundroute |  | No pagination | ✅ |  ❌  |
| lists |  | DefaultPaginator | ✅ |  ❌  |
| segments |  | DefaultPaginator | ✅ |  ❌  |
| statistics |  | DefaultPaginator | ✅ |  ❌  |
| templates |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-25 | [52337](https://github.com/airbytehq/airbyte/pull/52337) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51651](https://github.com/airbytehq/airbyte/pull/51651) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51113](https://github.com/airbytehq/airbyte/pull/51113) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50588](https://github.com/airbytehq/airbyte/pull/50588) | Update dependencies |
| 0.0.4 | 2024-12-21 | [49989](https://github.com/airbytehq/airbyte/pull/49989) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49522](https://github.com/airbytehq/airbyte/pull/49522) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49195](https://github.com/airbytehq/airbyte/pull/49195) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
