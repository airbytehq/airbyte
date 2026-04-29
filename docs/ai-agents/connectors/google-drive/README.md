# Google-Drive

The Google-Drive agent connector is a Python package that equips AI agents to interact with Google-Drive through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Google Drive is a cloud-based file storage and synchronization service that allows users
to store files, share content, and collaborate on documents. This connector provides
access to files, shared drives, permissions, comments, replies, revisions,
and change tracking, including the ability to create, update, delete, and upload files.


## Example questions

The Google-Drive connector is optimized to handle prompts like these.

- List all files in my Google Drive
- Show me details for a recent file
- Download a recent file from my Drive
- Export a recent Google Doc as PDF
- Export a recent Google Sheet as CSV
- Show me the content of a recent file
- List all shared drives I have access to
- Show me details for a shared drive I have access to
- Show permissions for a recent file
- List comments on a recent file
- Show replies to a recent comment on a file
- Show revision history for a recent file
- Get my Drive storage quota and user info
- List files in a folder I have access to
- Create a new file in Google Drive
- Upload a document to Drive
- Delete a file from Drive
- Move a file to a different folder
- Show me files modified in the last week
- What changes have been made since my last sync?

## Unsupported questions

The Google-Drive connector isn't currently able to handle prompts like these.

- Update file permissions
- Add a comment to a file

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

@agent.tool_plain
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

@tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

mcp = FastMCP("Google-Drive Agent")

@mcp.tool()
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `GoogleDriveConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

@agent.tool_plain
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

@tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Drive Agent")

@mcp.tool()
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Google-Drive Agent")

@mcp.tool()
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Files | [List](./REFERENCE.md#files-list), [Get](./REFERENCE.md#files-get), [Create](./REFERENCE.md#files-create), [Update](./REFERENCE.md#files-update), [Delete](./REFERENCE.md#files-delete), [Download](./REFERENCE.md#files-download) |
| Files Upload | [Create](./REFERENCE.md#files-upload-create) |
| Files Export | [Download](./REFERENCE.md#files-export-download) |
| Drives | [List](./REFERENCE.md#drives-list), [Get](./REFERENCE.md#drives-get) |
| Permissions | [List](./REFERENCE.md#permissions-list), [Get](./REFERENCE.md#permissions-get) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get) |
| Replies | [List](./REFERENCE.md#replies-list), [Get](./REFERENCE.md#replies-get) |
| Revisions | [List](./REFERENCE.md#revisions-list), [Get](./REFERENCE.md#revisions-get) |
| Changes | [List](./REFERENCE.md#changes-list) |
| Changes Start Page Token | [Get](./REFERENCE.md#changes-start-page-token-get) |
| About | [Get](./REFERENCE.md#about-get) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Google-Drive API docs

See the official [Google-Drive API reference](https://developers.google.com/workspace/drive/api/reference/rest/v3).

## Version information

- **Package version:** 0.2.4
- **Connector version:** 0.2.4
- **Generated with Connector SDK commit SHA:** unknown