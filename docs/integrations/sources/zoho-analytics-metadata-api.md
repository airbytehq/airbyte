# Zoho Analytics Metadata API
Zoho Analytics Metadata api connector enables seamless data syncing from Zoho Analytics metadata into data warehouses or BI tools. This connector automates OAuth authentication and ensures reliable data transfer, empowering businesses to streamline analytics workflows and gain deeper insights efficiently.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `org_id` | `number` | Org Id.  |  |
| `data_center` | `string` | Data Center.  | `com` |
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |

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
| 0.0.9 | 2025-02-08 | [53600](https://github.com/airbytehq/airbyte/pull/53600) | Update dependencies |
| 0.0.8 | 2025-02-01 | [53118](https://github.com/airbytehq/airbyte/pull/53118) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52542](https://github.com/airbytehq/airbyte/pull/52542) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51930](https://github.com/airbytehq/airbyte/pull/51930) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51462](https://github.com/airbytehq/airbyte/pull/51462) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50837](https://github.com/airbytehq/airbyte/pull/50837) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50384](https://github.com/airbytehq/airbyte/pull/50384) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49450](https://github.com/airbytehq/airbyte/pull/49450) | Update dependencies |
| 0.0.1 | 2024-11-07 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
