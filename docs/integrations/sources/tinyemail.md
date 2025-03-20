# Tinyemail
Tinyemail is an email marketing tool.
We can extract data from campaigns and contacts streams using this connector.
[API Docs](https://docs.tinyemail.com/docs/tiny-email/tinyemail)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | No pagination | ✅ |  ❌  |
| sender_details | id | No pagination | ✅ |  ❌  |
| contact_members |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.14 | 2025-03-08 | [55617](https://github.com/airbytehq/airbyte/pull/55617) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55101](https://github.com/airbytehq/airbyte/pull/55101) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54541](https://github.com/airbytehq/airbyte/pull/54541) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54102](https://github.com/airbytehq/airbyte/pull/54102) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53527](https://github.com/airbytehq/airbyte/pull/53527) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53059](https://github.com/airbytehq/airbyte/pull/53059) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52443](https://github.com/airbytehq/airbyte/pull/52443) | Update dependencies |
| 0.0.7 | 2025-01-18 | [52016](https://github.com/airbytehq/airbyte/pull/52016) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51424](https://github.com/airbytehq/airbyte/pull/51424) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50815](https://github.com/airbytehq/airbyte/pull/50815) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50340](https://github.com/airbytehq/airbyte/pull/50340) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49779](https://github.com/airbytehq/airbyte/pull/49779) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49437](https://github.com/airbytehq/airbyte/pull/49437) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
