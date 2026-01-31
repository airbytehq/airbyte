# Google-Drive agent connector

Google Drive is a cloud-based file storage and synchronization service that allows users
to store files, share content, and collaborate on documents. This connector provides
read-only access to files, shared drives, permissions, comments, replies, revisions,
and change tracking for data analysis and integration workflows.


## Example questions

The Google-Drive connector is optimized to handle prompts like these.

- List all files in my Google Drive
- Show me files modified in the last week
- Get details for file abc123
- Download file abc123 from my Drive
- Export Google Doc abc123 as PDF
- Export Google Sheet xyz789 as CSV
- Get the content of file abc123
- List all shared drives I have access to
- Get shared drive xyz789
- Show permissions for file abc123
- List comments on file abc123
- Get all replies to comment def456 on file abc123
- Show revision history for file abc123
- What changes have been made since my last sync?
- Get my Drive storage quota and user info
- List files in a specific folder

## Unsupported questions

The Google-Drive connector isn't currently able to handle prompts like these.

- Create a new file in Google Drive
- Upload a document to Drive
- Delete a file from Drive
- Update file permissions
- Add a comment to a file
- Move a file to a different folder

## Installation

```bash
uv pip install airbyte-agent-google-drive
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_google-drive import GoogleDriveConnector
from airbyte_agent_google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleDriveConnector.tool_utils
async def google-drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_google-drive import GoogleDriveConnector

connector = GoogleDriveConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleDriveConnector.tool_utils
async def google-drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Files | [List](./REFERENCE.md#files-list), [Get](./REFERENCE.md#files-get), [Download](./REFERENCE.md#files-download) |
| Files Export | [Download](./REFERENCE.md#files-export-download) |
| Drives | [List](./REFERENCE.md#drives-list), [Get](./REFERENCE.md#drives-get) |
| Permissions | [List](./REFERENCE.md#permissions-list), [Get](./REFERENCE.md#permissions-get) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get) |
| Replies | [List](./REFERENCE.md#replies-list), [Get](./REFERENCE.md#replies-get) |
| Revisions | [List](./REFERENCE.md#revisions-list), [Get](./REFERENCE.md#revisions-get) |
| Changes | [List](./REFERENCE.md#changes-list) |
| Changes Start Page Token | [Get](./REFERENCE.md#changes-start-page-token-get) |
| About | [Get](./REFERENCE.md#about-get) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Google-Drive API docs

See the official [Google-Drive API reference](https://developers.google.com/workspace/drive/api/reference/rest/v3).

## Version information

- **Package version:** 0.1.43
- **Connector version:** 0.1.3
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/google-drive/CHANGELOG.md)