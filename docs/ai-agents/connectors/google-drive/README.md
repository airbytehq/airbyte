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

```python
from airbyte_agent_google_drive import GoogleDriveConnector, GoogleDriveAuthConfig

connector = GoogleDriveConnector(
  auth_config=GoogleDriveAuthConfig(
    access_token="...",
    refresh_token="...",
    client_id="...",
    client_secret="..."
  )
)
result = await connector.files.list()
```


## Full documentation

This connector supports the following entities and actions.

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


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Google-Drive API reference](https://developers.google.com/workspace/drive/api/reference/rest/v3).

## Version information

- **Package version:** 0.1.0
- **Connector version:** 0.1.1
- **Generated with Connector SDK commit SHA:** a87e344611813eb215749ff982244659556b7b09