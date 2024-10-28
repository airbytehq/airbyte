# Zoho Analytics
Zoho Analytics connector enables seamless data syncing from Zoho Analytics into data warehouses or BI tools. This connector automates OAuth authentication and ensures reliable data transfer, empowering businesses to streamline analytics workflows and gain deeper insights efficiently.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |
| `data_center` | `string` | Data Center.  |  |
| `org_id` | `number` | Org Id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | emailId | No pagination | ✅ |  ❌  |
| workspaces | workspaceId | No pagination | ✅ |  ❌  |
| organizations | orgId | No pagination | ✅ |  ❌  |
| views | viewId | No pagination | ✅ |  ❌  |
| dashboards | viewId | No pagination | ✅ |  ❌  |
| trash | viewId | No pagination | ✅ |  ❌  |
| workspace_users | emailId | No pagination | ✅ |  ❌  |
| folders | folderId | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-28 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
