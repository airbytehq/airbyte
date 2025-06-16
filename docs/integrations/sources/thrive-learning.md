# Thrive Learning
A Connector for Thrive Learning

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Tenant ID. Your website Tenant ID (eu-west-000000 please contact support for your tenant) |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Content | id | DefaultPaginator | ✅ |  ❌  |
| Users | id | DefaultPaginator | ✅ |  ❌  |
| Activities | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-06-14 | [61612](https://github.com/airbytehq/airbyte/pull/61612) | Update dependencies |
| 0.0.2 | 2025-05-25 | [60447](https://github.com/airbytehq/airbyte/pull/60447) | Update dependencies |
| 0.0.1 | 2025-05-16 | | Initial release by [@cjm-s](https://github.com/cjm-s) via Connector Builder |

</details>
