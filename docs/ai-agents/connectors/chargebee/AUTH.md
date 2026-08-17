# Chargebee authentication

This page documents the authentication and configuration options for the Chargebee agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
This authentication method isn't available for this connector.


### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Chargebee API key (used as the HTTP Basic username) |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Data before this date is excluded. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Chargebee",
    "name": "My Chargebee Connector",
    "credentials": {
      "api_key": "<Your Chargebee API key (used as the HTTP Basic username)>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Data before this date is excluded.>"
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
  "name": "chargebee"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "chargebee"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "chargebee",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `ChargebeeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Chargebee Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

mcp = FastMCP("Chargebee Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

#### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `ChargebeeConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

@tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ChargebeeConnector.tool_utils(framework="openai_agents")
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Chargebee Assistant", tools=[chargebee_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

mcp = FastMCP("Chargebee Agent")

@mcp.tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Chargebee Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Chargebee Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
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
This authentication method isn't available for this connector.

### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Chargebee API key (used as the HTTP Basic username) |

Example request:

```python
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    )
)
```

## Configuration

The Chargebee connector also needs these configuration values to construct the base API URL.

- **Hosted CLI**: `airbyte-agent connectors create` doesn't currently accept these configuration fields directly. For hosted connectors that need these values, create the connector with the hosted API `replication_config`, then use the CLI for describe and execute operations after creation.
- **Hosted API**: pass these values in the connector creation `replication_config`.
- **Open source mode**: provide these values with your local connector setup so the connector can build the correct API base URL.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `site` | `string` | Yes | your-site | Your Chargebee site name (subdomain) |
