# Google-Analytics-Data-Api

The Google-Analytics-Data-Api agent connector is a Python package that equips AI agents to interact with Google-Analytics-Data-Api through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Google Analytics 4 (GA4) Data API connector for accessing website and app analytics data.
This connector provides access to pre-configured analytics reports including website overview,
active users, traffic sources, page performance, device breakdowns, and geographic locations.
Reports are retrieved via the GA4 Data API v1beta using configurable date ranges and
property IDs. Supports OAuth2 and service account key authentication with Google
Analytics read-only scope.


## Example prompts

The Google-Analytics-Data-Api connector is optimized to handle prompts like these.

- Show me the website overview report
- List daily active users
- Show weekly active user trends
- Get the four-weekly active users report
- List traffic sources
- Show me page performance metrics
- Get device breakdown data
- List user locations
- What are the top traffic sources by sessions?
- Which pages have the highest bounce rate?
- What devices do most users browse from?
- Which countries send the most traffic?
- How has daily active users changed over the last month?

## Unsupported prompts

The Google-Analytics-Data-Api connector isn't currently able to handle prompts like these.

- Create a new GA4 property
- Delete analytics data
- Modify tracking configurations
- Run a custom report with arbitrary dimensions
- Access real-time analytics data

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Website Overview | [List](./REFERENCE.md#website-overview-list), [Context Store Search](./REFERENCE.md#website-overview-context-store-search), [Context Store SQL Query](./REFERENCE.md#website-overview-context-store-sql-query) |
| Daily Active Users | [List](./REFERENCE.md#daily-active-users-list), [Context Store Search](./REFERENCE.md#daily-active-users-context-store-search), [Context Store SQL Query](./REFERENCE.md#daily-active-users-context-store-sql-query) |
| Weekly Active Users | [List](./REFERENCE.md#weekly-active-users-list), [Context Store Search](./REFERENCE.md#weekly-active-users-context-store-search), [Context Store SQL Query](./REFERENCE.md#weekly-active-users-context-store-sql-query) |
| Four Weekly Active Users | [List](./REFERENCE.md#four-weekly-active-users-list), [Context Store Search](./REFERENCE.md#four-weekly-active-users-context-store-search), [Context Store SQL Query](./REFERENCE.md#four-weekly-active-users-context-store-sql-query) |
| Traffic Sources | [List](./REFERENCE.md#traffic-sources-list), [Context Store Search](./REFERENCE.md#traffic-sources-context-store-search), [Context Store SQL Query](./REFERENCE.md#traffic-sources-context-store-sql-query) |
| Pages | [List](./REFERENCE.md#pages-list), [Context Store Search](./REFERENCE.md#pages-context-store-search), [Context Store SQL Query](./REFERENCE.md#pages-context-store-sql-query) |
| Devices | [List](./REFERENCE.md#devices-list), [Context Store Search](./REFERENCE.md#devices-context-store-search), [Context Store SQL Query](./REFERENCE.md#devices-context-store-sql-query) |
| Locations | [List](./REFERENCE.md#locations-list), [Context Store Search](./REFERENCE.md#locations-context-store-search), [Context Store SQL Query](./REFERENCE.md#locations-context-store-sql-query) |


## Google-Analytics-Data-Api API docs

See the official [Google-Analytics-Data-Api API reference](https://developers.google.com/analytics/devguides/reporting/data/v1/rest).

## Interfaces

Use the Google-Analytics-Data-Api connector through the Airbyte Agent CLI, the Python SDK, or the API.

### CLI

Install the CLI:

```bash
curl -fsSL https://airbyte.ai/install.sh | bash
```

Authenticate with Airbyte:

```bash
airbyte-agent login
```

Create the connector. The CLI opens the hosted setup flow:

```bash
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "google-analytics-data-api"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "google-analytics-data-api"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "google-analytics-data-api",
  "entity": "website_overview",
  "action": "list"
}'
```

### Python SDK

#### Installation

```bash
uv pip install airbyte-agent-sdk
```

#### Usage

Connectors can run in hosted or open source mode.

##### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `GoogleAnalyticsDataApiConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Analytics-Data-Api Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `GoogleAnalyticsDataApiConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="google_analytics_data_api_inspect",
    docs_tool="google_analytics_data_api_read_docs",
)
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.agent_tool(framework="pydantic_ai")
async def google_analytics_data_api_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.agent_tool(framework="pydantic_ai")
async def google_analytics_data_api_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

@GoogleAnalyticsDataApiConnector.agent_tool(
    inspect_tool="google_analytics_data_api_inspect",
    docs_tool="google_analytics_data_api_read_docs",
)
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@GoogleAnalyticsDataApiConnector.agent_tool()
async def google_analytics_data_api_inspect():
    return await connector.inspect_connector()

@GoogleAnalyticsDataApiConnector.agent_tool()
async def google_analytics_data_api_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (google_analytics_data_api_inspect, google_analytics_data_api_read_docs, google_analytics_data_api_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `GoogleAnalyticsDataApiConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `GoogleAnalyticsDataApiConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

@tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleAnalyticsDataApiConnector.tool_utils(framework="openai_agents")
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=[google_analytics_data_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector

connector = connect("google-analytics-data-api", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Analytics-Data-Api Agent")

@mcp.tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Google-Analytics-Data-Api Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

mcp = FastMCP("Google-Analytics-Data-Api Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `GoogleAnalyticsDataApiConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="google_analytics_data_api_inspect",
    docs_tool="google_analytics_data_api_read_docs",
)
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.agent_tool(framework="pydantic_ai")
async def google_analytics_data_api_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.agent_tool(framework="pydantic_ai")
async def google_analytics_data_api_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

@GoogleAnalyticsDataApiConnector.agent_tool(
    inspect_tool="google_analytics_data_api_inspect",
    docs_tool="google_analytics_data_api_read_docs",
)
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@GoogleAnalyticsDataApiConnector.agent_tool()
async def google_analytics_data_api_inspect():
    return await connector.inspect_connector()

@GoogleAnalyticsDataApiConnector.agent_tool()
async def google_analytics_data_api_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (google_analytics_data_api_inspect, google_analytics_data_api_read_docs, google_analytics_data_api_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `GoogleAnalyticsDataApiConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `GoogleAnalyticsDataApiConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

@tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleAnalyticsDataApiConnector.tool_utils(framework="openai_agents")
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Analytics-Data-Api Assistant", tools=[google_analytics_data_api_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_analytics_data_api import GoogleAnalyticsDataApiConnector
from airbyte_agent_sdk.connectors.google_analytics_data_api.models import GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig

connector = GoogleAnalyticsDataApiConnector(
    auth_config=GoogleAnalyticsDataApiServiceAccountKeyAuthenticationAuthConfig(
        credentials_json="<The JSON key linked to the service account used for authorization. For steps on obtaining this key, refer to https://docs.airbyte.com/integrations/sources/google-analytics-data-api/#setup-guide>"
    )
)

mcp = FastMCP("Google-Analytics-Data-Api Agent")

@mcp.tool
@GoogleAnalyticsDataApiConnector.tool_utils
async def google_analytics_data_api_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Analytics-Data-Api connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.1.0