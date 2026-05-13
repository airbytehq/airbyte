# Intercom authentication

This page documents the authentication and configuration options for the Intercom agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Intercom API Access Token |

Example request:

```python
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
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
| `access_token` | `str` | Yes | Your Intercom API Access Token |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Intercom",
    "name": "My Intercom Connector",
    "credentials": {
      "access_token": "<Your Intercom API Access Token>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.


**Python SDK**

The `connect()` factory returns a fully typed `IntercomConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

@tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@IntercomConnector.tool_utils(framework="openai_agents")
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Intercom Assistant", tools=[intercom_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

mcp = FastMCP("Intercom Agent")

@mcp.tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
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
@IntercomConnector.tool_utils(framework="openai_agents")
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Intercom Assistant", tools=[intercom_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Intercom Agent")

@mcp.tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
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


