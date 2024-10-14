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
| 0.0.1 | 2024-10-07 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
