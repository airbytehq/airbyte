# Ashby authentication

This page documents the authentication and configuration options for the Ashby agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Ashby API key |

Example request:

```python
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.connectors.ashby.models import AshbyAuthConfig

connector = AshbyConnector(
    auth_config=AshbyAuthConfig(
        api_key="<Your Ashby API key>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte Agent API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

#### OAuth
This authentication method isn't available for this connector.

#### Bring your own OAuth flow
This authentication method isn't available for this connector.

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Ashby API key |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | The date from which to start replicating data, in the format YYYY-MM-DDT00:00:00Z. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Ashby",
    "name": "My Ashby Connector",
    "credentials": {
      "api_key": "<Your Ashby API key>"
    },
    "replication_config": {
      "start_date": "<The date from which to start replicating data, in the format YYYY-MM-DDT00:00:00Z.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.


**Python SDK**

The `connect()` factory returns a fully typed `AshbyConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

@tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AshbyConnector.tool_utils(framework="openai_agents")
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Ashby Assistant", tools=[ashby_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

mcp = FastMCP("Ashby Agent")

@mcp.tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
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
@AshbyConnector.tool_utils(framework="openai_agents")
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Ashby Assistant", tools=[ashby_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Ashby Agent")

@mcp.tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'X-Organization-Id: <YOUR_ORGANIZATION_ID>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


