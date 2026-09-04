# Zendesk-Talk authentication

This page documents the authentication and configuration options for the Zendesk-Talk agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
Use the CLI for hosted OAuth connector creation when possible. It opens the hosted setup flow and avoids passing connector secrets through the command line:

```bash
airbyte-agent login
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "zendesk-talk"
}'
```

For API-first use cases, create a connector with OAuth credentials directly.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |
| `refresh_token` | `str` | No | OAuth 2.0 refresh token (optional) |
| `client_id` | `str` | No | OAuth client ID |
| `client_secret` | `str` | No | OAuth client secret |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating data. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Zendesk-Talk",
    "name": "My Zendesk-Talk Connector",
    "credentials": {
      "access_token": "<OAuth 2.0 access token>",
      "refresh_token": "<OAuth 2.0 refresh token (optional)>",
      "client_id": "<OAuth client ID>",
      "client_secret": "<OAuth client secret>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating data.>"
    }
  }'
```




### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `email` | `str` | Yes | Your Zendesk account email address |
| `api_token` | `str` | Yes | Your Zendesk API token from Admin Center |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating data. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Zendesk-Talk",
    "name": "My Zendesk-Talk Connector",
    "credentials": {
      "email": "<Your Zendesk account email address>",
      "api_token": "<Your Zendesk API token from Admin Center>"
    },
    "replication_config": {
      "start_date": "<UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating data.>"
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
  "name": "zendesk-talk"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "zendesk-talk"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zendesk-talk",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `ZendeskTalkConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zendesk-Talk Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Talk Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

#### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `ZendeskTalkConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

@tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskTalkConnector.tool_utils(framework="openai_agents")
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Talk Assistant", tools=[zendesk_talk_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Talk Agent")

@mcp.tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zendesk-Talk Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Zendesk-Talk Agent")

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

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |
| `refresh_token` | `str` | No | OAuth 2.0 refresh token (optional) |
| `client_id` | `str` | No | OAuth client ID |
| `client_secret` | `str` | No | OAuth client secret |

Example request:

```python
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkOauth20AuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkOauth20AuthConfig(
        access_token="<OAuth 2.0 access token>",
        refresh_token="<OAuth 2.0 refresh token (optional)>",
        client_id="<OAuth client ID>",
        client_secret="<OAuth client secret>"
    )
)
```

### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `email` | `str` | Yes | Your Zendesk account email address |
| `api_token` | `str` | Yes | Your Zendesk API token from Admin Center |

Example request:

```python
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)
```

## Configuration

The Zendesk-Talk connector also needs these configuration values to construct the base API URL.

- **Hosted CLI**: `airbyte-agent connectors create` doesn't currently accept these configuration fields directly. For hosted connectors that need these values, create the connector with the hosted API `replication_config`, then use the CLI for describe and execute operations after creation.
- **Hosted API**: pass these values in the connector creation `replication_config`.
- **Open source mode**: provide these values with your local connector setup so the connector can build the correct API base URL.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `subdomain` | `string` | Yes | your-subdomain | Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL) |
