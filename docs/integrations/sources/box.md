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
| `file_id` | `number` | File Id.  |  |
| `folder_id` | `number` | Folder Id.  |  |
| `search_input` | `string` | Search Input.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events |  | DefaultPaginator | ✅ |  ❌  |
| sign_templates | id | DefaultPaginator | ✅ |  ❌  |
| collections | id | DefaultPaginator | ✅ |  ❌  |
| collection_items | id | DefaultPaginator | ✅ |  ❌  |
| sign_request | id | DefaultPaginator | ✅ |  ❌  |
| admin_logs | event_id | DefaultPaginator | ✅ |  ❌  |
| all_files_and_folders | id | DefaultPaginator | ✅ |  ❌  |
| pending_collaborations |  | DefaultPaginator | ✅ |  ❌  |
| file_collaborations | id | DefaultPaginator | ✅ |  ❌  |
| folder_collaborations | id | DefaultPaginator | ✅ |  ❌  |
| file_comments | id | DefaultPaginator | ✅ |  ❌  |
| recent_items | id | DefaultPaginator | ✅ |  ❌  |
| search | id | DefaultPaginator | ✅ |  ❌  |
| file_tasks | id | No pagination | ✅ |  ❌  |
| trashed_items | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-24 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
