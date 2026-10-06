# Zendesk-Talk

The Zendesk-Talk agent connector is a Python package that equips AI agents to interact with Zendesk-Talk through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zendesk Talk (Voice) API. Provides access to phone numbers,
addresses, greetings, IVR configurations, call data, and agent/account statistics
for Zendesk Talk voice support channels.


## Example prompts

The Zendesk-Talk connector is optimized to handle prompts like these.

- List all phone numbers in our Zendesk Talk account
- Show all addresses on file
- List all IVR configurations
- Show all greetings
- List greeting categories
- Show agent activity statistics
- Show the account overview stats
- Show current queue activity
- Which phone numbers have SMS enabled?
- Find agents who have missed the most calls today
- What is the average call duration across all calls?
- Which phone numbers are toll-free?

## Unsupported prompts

The Zendesk-Talk connector isn't currently able to handle prompts like these.

- Create a new phone number
- Delete an IVR configuration
- Update a greeting
- Make an outbound call

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Phone Numbers | [List](./REFERENCE.md#phone-numbers-list), [Get](./REFERENCE.md#phone-numbers-get), [Context Store Search](./REFERENCE.md#phone-numbers-context-store-search), [Context Store SQL Query](./REFERENCE.md#phone-numbers-context-store-sql-query) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Context Store Search](./REFERENCE.md#addresses-context-store-search), [Context Store SQL Query](./REFERENCE.md#addresses-context-store-sql-query) |
| Greetings | [List](./REFERENCE.md#greetings-list), [Get](./REFERENCE.md#greetings-get), [Context Store Search](./REFERENCE.md#greetings-context-store-search), [Context Store SQL Query](./REFERENCE.md#greetings-context-store-sql-query) |
| Greeting Categories | [List](./REFERENCE.md#greeting-categories-list), [Get](./REFERENCE.md#greeting-categories-get), [Context Store Search](./REFERENCE.md#greeting-categories-context-store-search), [Context Store SQL Query](./REFERENCE.md#greeting-categories-context-store-sql-query) |
| Ivrs | [List](./REFERENCE.md#ivrs-list), [Get](./REFERENCE.md#ivrs-get), [Context Store Search](./REFERENCE.md#ivrs-context-store-search), [Context Store SQL Query](./REFERENCE.md#ivrs-context-store-sql-query) |
| Agents Activity | [List](./REFERENCE.md#agents-activity-list), [Context Store Search](./REFERENCE.md#agents-activity-context-store-search), [Context Store SQL Query](./REFERENCE.md#agents-activity-context-store-sql-query) |
| Agents Overview | [List](./REFERENCE.md#agents-overview-list), [Context Store Search](./REFERENCE.md#agents-overview-context-store-search), [Context Store SQL Query](./REFERENCE.md#agents-overview-context-store-sql-query) |
| Account Overview | [List](./REFERENCE.md#account-overview-list), [Context Store Search](./REFERENCE.md#account-overview-context-store-search), [Context Store SQL Query](./REFERENCE.md#account-overview-context-store-sql-query) |
| Current Queue Activity | [List](./REFERENCE.md#current-queue-activity-list), [Context Store Search](./REFERENCE.md#current-queue-activity-context-store-search), [Context Store SQL Query](./REFERENCE.md#current-queue-activity-context-store-sql-query) |
| Calls | [List](./REFERENCE.md#calls-list), [Context Store Search](./REFERENCE.md#calls-context-store-search), [Context Store SQL Query](./REFERENCE.md#calls-context-store-sql-query) |
| Call Legs | [List](./REFERENCE.md#call-legs-list), [Context Store Search](./REFERENCE.md#call-legs-context-store-search), [Context Store SQL Query](./REFERENCE.md#call-legs-context-store-sql-query) |


## Zendesk-Talk API docs

See the official [Zendesk-Talk API reference](https://developer.zendesk.com/api-reference/voice/talk-api/introduction/).

## Interfaces

Use the Zendesk-Talk connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "entity": "phone_numbers",
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

The `connect()` factory returns a fully typed `ZendeskTalkConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ZendeskTalkConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="zendesk_talk_inspect",
    docs_tool="zendesk_talk_read_docs",
)
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ZendeskTalkConnector.agent_tool(framework="pydantic_ai")
async def zendesk_talk_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ZendeskTalkConnector.agent_tool(framework="pydantic_ai")
async def zendesk_talk_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

@ZendeskTalkConnector.agent_tool(
    inspect_tool="zendesk_talk_inspect",
    docs_tool="zendesk_talk_read_docs",
)
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ZendeskTalkConnector.agent_tool()
async def zendesk_talk_inspect():
    return await connector.inspect_connector()

@ZendeskTalkConnector.agent_tool()
async def zendesk_talk_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (zendesk_talk_inspect, zendesk_talk_read_docs, zendesk_talk_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ZendeskTalkConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ZendeskTalkConnector.agent_tool` above.

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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
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
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
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
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

mcp = FastMCP("Zendesk-Talk Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ZendeskTalkConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="zendesk_talk_inspect",
    docs_tool="zendesk_talk_read_docs",
)
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ZendeskTalkConnector.agent_tool(framework="pydantic_ai")
async def zendesk_talk_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ZendeskTalkConnector.agent_tool(framework="pydantic_ai")
async def zendesk_talk_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

@ZendeskTalkConnector.agent_tool(
    inspect_tool="zendesk_talk_inspect",
    docs_tool="zendesk_talk_read_docs",
)
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ZendeskTalkConnector.agent_tool()
async def zendesk_talk_inspect():
    return await connector.inspect_connector()

@ZendeskTalkConnector.agent_tool()
async def zendesk_talk_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (zendesk_talk_inspect, zendesk_talk_read_docs, zendesk_talk_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ZendeskTalkConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ZendeskTalkConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

mcp = FastMCP("Zendesk-Talk Agent")

@mcp.tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.3