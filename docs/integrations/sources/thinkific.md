# Thinkific
Airbyte connector for Thinkific, allowing you to seamlessly sync data like users, course participants, and instructors from Thinkific to other platforms. It's designed to make managing and analyzing your online courses and communities even easier!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Thinkific API key for authentication. |  |
| `subdomain` | `string` | subdomain. The subdomain of your Thinkific URL (e.g., if your URL is example.thinkific.com, your subdomain is "example". |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| courses | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| promotions | id | DefaultPaginator | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| reviews | id | DefaultPaginator | ✅ |  ❌  |
| enrollments | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| instructors | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| coupons | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-02-01 | [53038](https://github.com/airbytehq/airbyte/pull/53038) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52416](https://github.com/airbytehq/airbyte/pull/52416) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51962](https://github.com/airbytehq/airbyte/pull/51962) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51452](https://github.com/airbytehq/airbyte/pull/51452) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50799](https://github.com/airbytehq/airbyte/pull/50799) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50338](https://github.com/airbytehq/airbyte/pull/50338) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49798](https://github.com/airbytehq/airbyte/pull/49798) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49377](https://github.com/airbytehq/airbyte/pull/49377) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48142](https://github.com/airbytehq/airbyte/pull/48142) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47525](https://github.com/airbytehq/airbyte/pull/47525) | Update dependencies |
| 0.0.1 | 2024-10-07 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
