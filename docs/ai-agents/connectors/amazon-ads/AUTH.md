# Amazon-Ads authentication

This page documents the authentication and configuration options for the Amazon-Ads agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
Use the CLI for hosted OAuth connector creation when possible. It opens the hosted setup flow and avoids passing connector secrets through the command line:

```bash
airbyte-agent login
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-ads"
}'
```

For API-first use cases, create a connector with OAuth credentials directly.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | No | The client ID of your Amazon Ads API application |
| `client_secret` | `str` | No | The client secret of your Amazon Ads API application |
| `refresh_token` | `str` | Yes | The refresh token obtained from the OAuth authorization flow |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Amazon-Ads",
    "name": "My Amazon-Ads Connector",
    "credentials": {
      "client_id": "<The client ID of your Amazon Ads API application>",
      "client_secret": "<The client secret of your Amazon Ads API application>",
      "refresh_token": "<The refresh token obtained from the OAuth authorization flow>"
    }
  }'
```




### Token
This authentication method isn't available for this connector.

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
  "name": "amazon-ads"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-ads"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-ads",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `AmazonAdsConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amazon-Ads Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amazon-Ads Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

#### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `AmazonAdsConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmazonAdsConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="amazon_ads_inspect",
    docs_tool="amazon_ads_read_docs",
)
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@AmazonAdsConnector.agent_tool(framework="pydantic_ai")
async def amazon_ads_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@AmazonAdsConnector.agent_tool(framework="pydantic_ai")
async def amazon_ads_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

@AmazonAdsConnector.agent_tool(
    inspect_tool="amazon_ads_inspect",
    docs_tool="amazon_ads_read_docs",
)
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@AmazonAdsConnector.agent_tool()
async def amazon_ads_inspect():
    return await connector.inspect_connector()

@AmazonAdsConnector.agent_tool()
async def amazon_ads_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (amazon_ads_inspect, amazon_ads_read_docs, amazon_ads_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

#### Legacy alternatives

These examples are kept for existing integrations. The deprecated `AmazonAdsConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `AmazonAdsConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

@tool
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AmazonAdsConnector.tool_utils(framework="openai_agents")
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amazon-Ads Assistant", tools=[amazon_ads_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amazon-Ads Agent")

@mcp.tool
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
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
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
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
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amazon-Ads Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Amazon-Ads Agent")

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
| `client_id` | `str` | No | The client ID of your Amazon Ads API application |
| `client_secret` | `str` | No | The client secret of your Amazon Ads API application |
| `refresh_token` | `str` | Yes | The refresh token obtained from the OAuth authorization flow |

Example request:

```python
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.connectors.amazon_ads.models import AmazonAdsAuthConfig

connector = AmazonAdsConnector(
    auth_config=AmazonAdsAuthConfig(
        client_id="<The client ID of your Amazon Ads API application>",
        client_secret="<The client secret of your Amazon Ads API application>",
        refresh_token="<The refresh token obtained from the OAuth authorization flow>"
    ),
    region="<The Amazon Ads API endpoint URL based on region:
- NA (North America): https://advertising-api.amazon.com
- EU (Europe): https://advertising-api-eu.amazon.com
- FE (Far East): https://advertising-api-fe.amazon.com
>"
)
```

### Token
This authentication method isn't available for this connector.

## Configuration

The Amazon-Ads connector also needs these configuration values to construct the base API URL.

- **Hosted CLI**: `airbyte-agent connectors create` doesn't currently accept these configuration fields directly. For hosted connectors that need these values, create the connector with the hosted API `replication_config`, then use the CLI for describe and execute operations after creation.
- **Hosted API**: pass these values in the connector creation `replication_config`.
- **Open source mode**: provide these values with your local connector setup so the connector can build the correct API base URL.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `region` | `string` | Yes | https://advertising-api.amazon.com | The Amazon Ads API endpoint URL based on region:
- NA (North America): https://advertising-api.amazon.com
- EU (Europe): https://advertising-api-eu.amazon.com
- FE (Far East): https://advertising-api-fe.amazon.com
 |
