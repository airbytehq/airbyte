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
| 0.0.1 | 2024-11-09 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
