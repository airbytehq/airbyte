# JustSift
Airbyte connector for [JustSift](https://www.justsift.com/) can help you sync data from the JustSift API.

Sift empowers team members to discover and benefit from the massive knowledge base that is their entire workforce. If knowledge is power, Sift gives organizations superpowers.

As team members, we're empowered, collaborative, and excited to learn new things. Most of all, we look forward to you joining us as we continue building for the organization of tomorrow, today.
Wonderi

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use for accessing the Sift API. Obtain this token from your Sift account administrator. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| peoples | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-01 | [52738](https://github.com/airbytehq/airbyte/pull/52738) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52255](https://github.com/airbytehq/airbyte/pull/52255) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51790](https://github.com/airbytehq/airbyte/pull/51790) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51158](https://github.com/airbytehq/airbyte/pull/51158) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50611](https://github.com/airbytehq/airbyte/pull/50611) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50136](https://github.com/airbytehq/airbyte/pull/50136) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49648](https://github.com/airbytehq/airbyte/pull/49648) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49265](https://github.com/airbytehq/airbyte/pull/49265) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48975](https://github.com/airbytehq/airbyte/pull/48975) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-29 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
