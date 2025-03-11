# Thinkific Courses

Thinkific is a leading platform for creating, marketing, and selling courses, digital products, communities and learning experiences.
This connector retrives basic data information from courses.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `X-Auth-Subdomain` | `string` | subdomain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Courses |  | DefaultPaginator | ✅ |  ❌  |
| Courses Chapters |  | DefaultPaginator | ✅ |  ❌  |
| Contents |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-03-08 | [55630](https://github.com/airbytehq/airbyte/pull/55630) | Update dependencies |
| 0.0.2 | 2025-03-01 | [55089](https://github.com/airbytehq/airbyte/pull/55089) | Update dependencies |
| 0.0.1 | 2025-02-20 | | Initial release by [@gueroverde](https://github.com/gueroverde) via Connector Builder |

</details>
