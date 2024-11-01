# Vercel
 Vercel connector  enables seamless data sync between Vercel projects and various destinations. This integration simplifies real-time deployments, analytics, and automated workflows by bridging data from Vercel to your destination.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `access_token` | `string` | Access Token. Access token to authenticate with the Vercel API. Create and manage tokens in your Vercel account settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| user |  | DefaultPaginator | ✅ |  ❌  |
| deployments | uid | DefaultPaginator | ✅ |  ✅  |
| checks |  | DefaultPaginator | ✅ |  ❌  |
| environments |  | DefaultPaginator | ✅ |  ❌  |
| auth_tokens | id | DefaultPaginator | ✅ |  ❌  |
| aliases | uid | DefaultPaginator | ✅ |  ✅  |
| deployment_events | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-22 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
