# Squarespace
The Squarespace connector enables seamless integration with your Squarespace store, allowing you to sync data from various key endpoints

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://developers.squarespace.com/commerce-apis/authentication-and-permissions |  |
| `start_date` | `string` | Start date. Any data before this date will not be replicated. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| inventory | variantId | DefaultPaginator | ✅ |  ❌  |
| store_pages | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| profiles | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ✅  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-01-18 | [51969](https://github.com/airbytehq/airbyte/pull/51969) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51390](https://github.com/airbytehq/airbyte/pull/51390) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50788](https://github.com/airbytehq/airbyte/pull/50788) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50336](https://github.com/airbytehq/airbyte/pull/50336) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49781](https://github.com/airbytehq/airbyte/pull/49781) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49386](https://github.com/airbytehq/airbyte/pull/49386) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48233](https://github.com/airbytehq/airbyte/pull/48233) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47806](https://github.com/airbytehq/airbyte/pull/47806) | Update dependencies |
| 0.0.1 | 2024-10-10 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>
