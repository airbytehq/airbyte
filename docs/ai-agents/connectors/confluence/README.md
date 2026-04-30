# Confluence

The Confluence agent connector is a Python package that equips AI agents to interact with Confluence through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Confluence Cloud REST API. Provides read access to Confluence spaces, pages, blog posts, groups, and audit logs. Uses the Confluence Cloud REST API v2 for spaces, pages, and blog posts, and the v1 API for groups and audit records. Authenticates via HTTP Basic using an Atlassian account email and API token.

## Example questions

The Confluence connector is optimized to handle prompts like these.

- List all spaces in my Confluence instance
- Show me the most recently created pages
- List all blog posts
- Show me details for a specific page
- List all groups in Confluence
- Show me recent audit log entries
- Get details about a specific space
- Show me blog post details
- Find pages created in the last 7 days
- What spaces have the most pages?
- Show me all pages in a specific space
- Find blog posts by a specific author
- What audit events happened this week?

## Unsupported questions

The Confluence connector isn't currently able to handle prompts like these.

- Create a new page in Confluence
- Update an existing page
- Delete a space
- Upload an attachment to a page
- Manage space permissions

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
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.connectors.confluence.models import ConfluenceAuthConfig

connector = ConfluenceConnector(
    auth_config=ConfluenceAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    )
)

@agent.tool_plain
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.connectors.confluence.models import ConfluenceAuthConfig

connector = ConfluenceConnector(
    auth_config=ConfluenceAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    )
)

@tool
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Confluence connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.connectors.confluence.models import ConfluenceAuthConfig

connector = ConfluenceConnector(
    auth_config=ConfluenceAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    )
)

mcp = FastMCP("Confluence Agent")

@mcp.tool()
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Confluence connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `ConfluenceConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector

connector = connect("confluence", workspace_name="<your_workspace_name>")

@agent.tool_plain
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector

connector = connect("confluence", workspace_name="<your_workspace_name>")

@tool
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Confluence connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector

connector = connect("confluence", workspace_name="<your_workspace_name>")

mcp = FastMCP("Confluence Agent")

@mcp.tool()
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Confluence connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ConfluenceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ConfluenceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Confluence connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ConfluenceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Confluence Agent")

@mcp.tool()
@ConfluenceConnector.tool_utils
async def confluence_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Confluence connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Spaces | [List](./REFERENCE.md#spaces-list), [Get](./REFERENCE.md#spaces-get), [Context Store Search](./REFERENCE.md#spaces-context-store-search) |
| Pages | [List](./REFERENCE.md#pages-list), [Get](./REFERENCE.md#pages-get), [Context Store Search](./REFERENCE.md#pages-context-store-search) |
| Blog Posts | [List](./REFERENCE.md#blog-posts-list), [Get](./REFERENCE.md#blog-posts-get), [Context Store Search](./REFERENCE.md#blog-posts-context-store-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Context Store Search](./REFERENCE.md#groups-context-store-search) |
| Audit | [List](./REFERENCE.md#audit-list), [Context Store Search](./REFERENCE.md#audit-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Confluence API docs

See the official [Confluence API reference](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/).

## Version information

- **Package version:** 1.0.1
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** unknown