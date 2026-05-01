# Confluence authentication

This page documents the authentication and configuration options for the Confluence agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `username` | `str` | Yes | Your Atlassian account email address |
| `password` | `str` | Yes | Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens |

Example request:

```python
from airbyte_agent_sdk.connectors.confluence import ConfluenceConnector
from airbyte_agent_sdk.connectors.confluence.models import ConfluenceAuthConfig

connector = ConfluenceConnector(
    auth_config=ConfluenceAuthConfig(
        username="<Your Atlassian account email address>",
        password="<Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
This authentication method isn't available for this connector.

#### Bring your own OAuth flow
This authentication method isn't available for this connector.

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `username` | `str` | Yes | Your Atlassian account email address |
| `password` | `str` | Yes | Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Confluence",
    "name": "My Confluence Connector",
    "credentials": {
      "username": "<Your Atlassian account email address>",
      "password": "<Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.


**Python SDK**

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

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'X-Organization-Id: <YOUR_ORGANIZATION_ID>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


## Configuration

The Confluence connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `subdomain` | `string` | Yes | \{subdomain\} | Your Confluence Cloud subdomain (e.g., mycompany for mycompany.atlassian.net) |
