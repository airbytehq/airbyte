# Granola

The Granola agent connector is a Python package that equips AI agents to interact with Granola through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

The Granola API connector provides read access to meeting notes from Granola,
an AI-powered meeting notes platform. This connector integrates with the Granola
Enterprise API to list and retrieve notes, including summaries, transcripts,
attendees, and calendar event details. Requires an Enterprise plan API key.


## Example questions

The Granola connector is optimized to handle prompts like these.

- List all meeting notes from Granola
- Show me recent meeting notes
- Get the details of a specific note
- List notes created in the last week
- Find meeting notes from last month
- Which meetings had the most attendees?
- Show me notes that mention budget reviews
- What meetings happened this quarter?

## Unsupported questions

The Granola connector isn't currently able to handle prompts like these.

- Create a new meeting note
- Delete a meeting note
- Update an existing note
- Share a note with someone

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
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola Enterprise API key generated from Settings > Workspaces > API tab>"
    )
)

@agent.tool_plain
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola Enterprise API key generated from Settings > Workspaces > API tab>"
    )
)

@tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola Enterprise API key generated from Settings > Workspaces > API tab>"
    )
)

mcp = FastMCP("Granola Agent")

@mcp.tool()
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `GranolaConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

@agent.tool_plain
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

@tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

mcp = FastMCP("Granola Agent")

@mcp.tool()
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Granola Agent")

@mcp.tool()
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [Context Store Search](./REFERENCE.md#notes-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Granola API docs

See the official [Granola API reference](https://docs.granola.ai/introduction).

## Version information

- **Package version:** 1.0.6
- **Connector version:** 1.0.6
- **Generated with Connector SDK commit SHA:** unknown