# Blogger
Google Blogger is a free blogging platform by Google that allows users to create and manage their own blogs with ease. It offers customizable templates, user-friendly tools, and integration with other Google services, making it simple to publish content and reach a wide audience. 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| blogs | id | DefaultPaginator | ✅ |  ❌  |
| posts |  | DefaultPaginator | ✅ |  ❌  |
| pages | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-11 | [51242](https://github.com/airbytehq/airbyte/pull/51242) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50441](https://github.com/airbytehq/airbyte/pull/50441) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50162](https://github.com/airbytehq/airbyte/pull/50162) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49578](https://github.com/airbytehq/airbyte/pull/49578) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49012](https://github.com/airbytehq/airbyte/pull/49012) | Update dependencies |
| 0.0.1 | 2024-11-09 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
