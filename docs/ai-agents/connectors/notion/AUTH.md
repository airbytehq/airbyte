# Notion authentication

This page documents the authentication and configuration options for the Notion agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
Use the CLI for hosted OAuth connector creation when possible. It opens the hosted setup flow and avoids passing connector secrets through the command line:

```bash
airbyte-agent login
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion"
}'
```

For API-first use cases, create a connector with OAuth credentials directly.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your Notion OAuth integration's client ID |
| `client_secret` | `str` | Yes | Your Notion OAuth integration's client secret |
| `access_token` | `str` | Yes | OAuth access token obtained through the Notion authorization flow |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Notion",
    "name": "My Notion Connector",
    "credentials": {
      "client_id": "<Your Notion OAuth integration's client ID>",
      "client_secret": "<Your Notion OAuth integration's client secret>",
      "access_token": "<OAuth access token obtained through the Notion authorization flow>"
    }
  }'
```




### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | Notion internal integration token (starts with ntn_ or secret_) |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Notion",
    "name": "My Notion Connector",
    "credentials": {
      "token": "<Notion internal integration token (starts with ntn_ or secret_)>"
    }
  }'
```

### Execution

After creating the connector, execute operations using the CLI, Python SDK, or API.
If your Airbyte client can access multiple organizations, set the default organization with `airbyte-agent organizations use`, include `organization_id` in `AirbyteAuthConfig`, or include `X-Organization-Id` in raw API calls.

**CLI**

Authenticate with Airbyte:

```bash
airbyte-agent login
```

Create the connector. The CLI opens the hosted setup flow:

```bash
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `NotionConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
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
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
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


## Open source mode

In open source mode, provide API credentials directly to the connector.

### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your Notion OAuth integration's client ID |
| `client_secret` | `str` | Yes | Your Notion OAuth integration's client secret |
| `access_token` | `str` | Yes | OAuth access token obtained through the Notion authorization flow |

Example request:

```python
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionOauth20AuthConfig

connector = NotionConnector(
    auth_config=NotionOauth20AuthConfig(
        client_id="<Your Notion OAuth integration's client ID>",
        client_secret="<Your Notion OAuth integration's client secret>",
        access_token="<OAuth access token obtained through the Notion authorization flow>"
    )
)
```

### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | Notion internal integration token (starts with ntn_ or secret_) |

Example request:

```python
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionAccessTokenAuthConfig

connector = NotionConnector(
    auth_config=NotionAccessTokenAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
    )
)
```

