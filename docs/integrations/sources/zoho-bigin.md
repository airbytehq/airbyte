# Zoho Bigin
 Zoho Bigin connector  enables seamless data sync between Zoho Bigin and other platforms. This connector automates CRM data integration, improving workflows and ensuring real-time access to customer insights across tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `data_center` | `string` | Data Center. The data center where the Bigin account's resources are hosted | com |
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| modules | id | No pagination | ✅ |  ❌  |
| organizations | id | No pagination | ✅ |  ❌  |
| roles | id | No pagination | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | No pagination | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| tasks |  | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-27 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
