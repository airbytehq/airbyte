# Drip
Integrate seamlessly with Drip using this Airbyte connector, enabling smooth data sync for all your email marketing needs. Effortlessly connect and automate data flows to optimize your marketing strategies with ease

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://www.getdrip.com/user/edit |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| broadcasts | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| users | email | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| subscribers | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | custom_field_identifiers | DefaultPaginator | ✅ |  ❌  |
| conversions | id | DefaultPaginator | ✅ |  ❌  |
| events | account_id | DefaultPaginator | ✅ |  ❌  |
| tags | tags | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.13 | 2025-02-08 | [53355](https://github.com/airbytehq/airbyte/pull/53355) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52807](https://github.com/airbytehq/airbyte/pull/52807) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52375](https://github.com/airbytehq/airbyte/pull/52375) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51683](https://github.com/airbytehq/airbyte/pull/51683) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51132](https://github.com/airbytehq/airbyte/pull/51132) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50528](https://github.com/airbytehq/airbyte/pull/50528) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50042](https://github.com/airbytehq/airbyte/pull/50042) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49531](https://github.com/airbytehq/airbyte/pull/49531) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49204](https://github.com/airbytehq/airbyte/pull/49204) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48914](https://github.com/airbytehq/airbyte/pull/48914) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48311](https://github.com/airbytehq/airbyte/pull/48311) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47446](https://github.com/airbytehq/airbyte/pull/47446) | Update dependencies |
| 0.0.1 | 2024-10-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
