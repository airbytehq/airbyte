# Typeform

The Typeform agent connector is a Python package that equips AI agents to interact with Typeform through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Typeform API. Provides access to forms, form responses, webhooks, workspaces, images, and themes. Supports listing and retrieving typeform resources for survey and form management workflows.


## Example prompts

The Typeform connector is optimized to handle prompts like these.

- List all my typeforms
- Show me the responses for my latest form
- What workspaces do I have?
- List all themes in my account
- Get the details of a specific form
- Which forms received the most responses last month?
- Find responses submitted in the last week
- What forms were created this year?
- Show me all forms in a specific workspace

## Unsupported prompts

The Typeform connector isn't currently able to handle prompts like these.

- Create a new typeform
- Delete a form response
- Update form settings
- Send a webhook notification

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Forms | [List](./REFERENCE.md#forms-list), [Get](./REFERENCE.md#forms-get), [Context Store Search](./REFERENCE.md#forms-context-store-search) |
| Responses | [List](./REFERENCE.md#responses-list), [Context Store Search](./REFERENCE.md#responses-context-store-search) |
| Webhooks | [List](./REFERENCE.md#webhooks-list), [Context Store Search](./REFERENCE.md#webhooks-context-store-search) |
| Workspaces | [List](./REFERENCE.md#workspaces-list), [Context Store Search](./REFERENCE.md#workspaces-context-store-search) |
| Images | [List](./REFERENCE.md#images-list), [Context Store Search](./REFERENCE.md#images-context-store-search) |
| Themes | [List](./REFERENCE.md#themes-list), [Context Store Search](./REFERENCE.md#themes-context-store-search) |


## Typeform API docs

See the official [Typeform API reference](https://developer.typeform.com/).

## SDK installation

```bash
uv pip install airbyte-agent-sdk
```

## SDK usage

Connectors can run in hosted or open source mode.

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `TypeformConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.typeform import TypeformConnector

connector = connect("typeform", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.typeform import TypeformConnector

connector = connect("typeform", workspace_name="<your_workspace_name>")

@tool
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.typeform import TypeformConnector

connector = connect("typeform", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TypeformConnector.tool_utils(framework="openai_agents")
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Typeform Assistant", tools=[typeform_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.typeform import TypeformConnector

connector = connect("typeform", workspace_name="<your_workspace_name>")

mcp = FastMCP("Typeform Agent")

@mcp.tool
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TypeformConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TypeformConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TypeformConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TypeformConnector.tool_utils(framework="openai_agents")
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Typeform Assistant", tools=[typeform_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TypeformConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Typeform Agent")

@mcp.tool
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.connectors.typeform.models import TypeformAuthConfig

connector = TypeformConnector(
    auth_config=TypeformAuthConfig(
        access_token="<Personal access token from your Typeform account settings>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.connectors.typeform.models import TypeformAuthConfig

connector = TypeformConnector(
    auth_config=TypeformAuthConfig(
        access_token="<Personal access token from your Typeform account settings>"
    )
)

@tool
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.connectors.typeform.models import TypeformAuthConfig

connector = TypeformConnector(
    auth_config=TypeformAuthConfig(
        access_token="<Personal access token from your Typeform account settings>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TypeformConnector.tool_utils(framework="openai_agents")
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Typeform Assistant", tools=[typeform_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.typeform import TypeformConnector
from airbyte_agent_sdk.connectors.typeform.models import TypeformAuthConfig

connector = TypeformConnector(
    auth_config=TypeformAuthConfig(
        access_token="<Personal access token from your Typeform account settings>"
    )
)

mcp = FastMCP("Typeform Agent")

@mcp.tool
@TypeformConnector.tool_utils
async def typeform_execute(entity: str, action: str, params: dict | None = None):
    """Execute Typeform connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.4
