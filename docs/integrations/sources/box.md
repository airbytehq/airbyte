# Box
The Box Connector enables seamless data extraction from Box, allowing users to list, access, and synchronize files or folders from their Box cloud storage. This connector helps automate workflows by integrating Box data with other tools, ensuring efficient file management and analysis

## Authentication
Follow [this](https://developer.box.com/guides/authentication/client-credentials/) guide to complete authentication.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `user` | `number` | User.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events |  | DefaultPaginator | ✅ |  ❌  |
| sign_templates | id | DefaultPaginator | ✅ |  ❌  |
| collections | id | DefaultPaginator | ✅ |  ❌  |
| collection_items | id | DefaultPaginator | ✅ |  ❌  |
| sign_request | id | DefaultPaginator | ✅ |  ❌  |
| admin_logs | event_id | DefaultPaginator | ✅ |  ❌  |
| files | id | DefaultPaginator | ✅ |  ❌  |
| file_collaborations | id | DefaultPaginator | ✅ |  ❌  |
| file_comments | id | DefaultPaginator | ✅ |  ❌  |
| file_tasks | id | No pagination | ✅ |  ❌  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| folder_collaborations | id | DefaultPaginator | ✅ |  ❌  |
| recent_items | id | DefaultPaginator | ✅ |  ❌  |
| trashed_items | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-02-08 | [53399](https://github.com/airbytehq/airbyte/pull/53399) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52888](https://github.com/airbytehq/airbyte/pull/52888) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52167](https://github.com/airbytehq/airbyte/pull/52167) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51757](https://github.com/airbytehq/airbyte/pull/51757) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51291](https://github.com/airbytehq/airbyte/pull/51291) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50497](https://github.com/airbytehq/airbyte/pull/50497) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50209](https://github.com/airbytehq/airbyte/pull/50209) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49580](https://github.com/airbytehq/airbyte/pull/49580) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49276](https://github.com/airbytehq/airbyte/pull/49276) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48933](https://github.com/airbytehq/airbyte/pull/48933) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-24 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
