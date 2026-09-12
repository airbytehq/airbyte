# Zendesk-Chat

The Zendesk-Chat agent connector is a Python package that equips AI agents to interact with Zendesk-Chat through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Zendesk Chat enables real-time customer support through live chat. This connector
provides access to chat transcripts, agents, departments, shortcuts, triggers,
and other chat configuration data for analytics and support insights.

## Supported Entities
- **accounts**: Account information and billing details
- **agents**: Chat agents with roles and department assignments
- **agent_timeline**: Agent activity timeline (incremental export)
- **bans**: Banned visitors (IP and visitor-based)
- **chats**: Chat transcripts with full conversation history (incremental export)
- **departments**: Chat departments for routing
- **goals**: Conversion goals for tracking
- **roles**: Agent role definitions
- **routing_settings**: Account-level routing configuration
- **shortcuts**: Canned responses for agents
- **skills**: Agent skills for skill-based routing
- **triggers**: Automated chat triggers

## Rate Limits
Zendesk Chat API uses the `Retry-After` header for rate limit backoff.
The connector handles this automatically.


## Example prompts

The Zendesk-Chat connector is optimized to handle prompts like these.

- List all banned visitors
- List all departments with their settings
- Show me all chats from last week
- List all agents in the support department
- What are the most used chat shortcuts?
- Show chat volume by department
- What triggers are currently active?
- Show agent activity timeline for today

## Unsupported prompts

The Zendesk-Chat connector isn't currently able to handle prompts like these.

- Start a new chat session
- Send a message to a visitor
- Create a new agent
- Update department settings
- Delete a shortcut

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [Get](./REFERENCE.md#accounts-get) |
| Agents | [List](./REFERENCE.md#agents-list), [Get](./REFERENCE.md#agents-get), [Context Store Search](./REFERENCE.md#agents-context-store-search), [Context Store SQL Query](./REFERENCE.md#agents-context-store-sql-query) |
| Agent Timeline | [List](./REFERENCE.md#agent-timeline-list) |
| Bans | [List](./REFERENCE.md#bans-list), [Get](./REFERENCE.md#bans-get) |
| Chats | [List](./REFERENCE.md#chats-list), [Get](./REFERENCE.md#chats-get), [Context Store Search](./REFERENCE.md#chats-context-store-search), [Context Store SQL Query](./REFERENCE.md#chats-context-store-sql-query) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get), [Context Store Search](./REFERENCE.md#departments-context-store-search), [Context Store SQL Query](./REFERENCE.md#departments-context-store-sql-query) |
| Goals | [List](./REFERENCE.md#goals-list), [Get](./REFERENCE.md#goals-get) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get) |
| Routing Settings | [Get](./REFERENCE.md#routing-settings-get) |
| Shortcuts | [List](./REFERENCE.md#shortcuts-list), [Get](./REFERENCE.md#shortcuts-get), [Context Store Search](./REFERENCE.md#shortcuts-context-store-search), [Context Store SQL Query](./REFERENCE.md#shortcuts-context-store-sql-query) |
| Skills | [List](./REFERENCE.md#skills-list), [Get](./REFERENCE.md#skills-get) |
| Triggers | [List](./REFERENCE.md#triggers-list), [Context Store Search](./REFERENCE.md#triggers-context-store-search), [Context Store SQL Query](./REFERENCE.md#triggers-context-store-sql-query) |


## Zendesk-Chat API docs

See the official [Zendesk-Chat API reference](https://developer.zendesk.com/api-reference/live-chat/chat-api/introduction/).

## Interfaces

Use the Zendesk-Chat connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "zendesk-chat"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "zendesk-chat"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zendesk-chat",
  "entity": "accounts",
  "action": "get"
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

The `connect()` factory returns a fully typed `ZendeskChatConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zendesk-Chat Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Chat Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ZendeskChatConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskChatConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="zendesk_chat_inspect",
    docs_tool="zendesk_chat_read_docs",
)
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ZendeskChatConnector.agent_tool(framework="pydantic_ai")
async def zendesk_chat_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ZendeskChatConnector.agent_tool(framework="pydantic_ai")
async def zendesk_chat_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

@ZendeskChatConnector.agent_tool(
    inspect_tool="zendesk_chat_inspect",
    docs_tool="zendesk_chat_read_docs",
)
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ZendeskChatConnector.agent_tool()
async def zendesk_chat_inspect():
    return await connector.inspect_connector()

@ZendeskChatConnector.agent_tool()
async def zendesk_chat_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (zendesk_chat_inspect, zendesk_chat_read_docs, zendesk_chat_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ZendeskChatConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ZendeskChatConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

@tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskChatConnector.tool_utils(framework="openai_agents")
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Chat Assistant", tools=[zendesk_chat_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Chat Agent")

@mcp.tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zendesk-Chat Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Zendesk-Chat Agent")

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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zendesk-Chat Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

mcp = FastMCP("Zendesk-Chat Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ZendeskChatConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskChatConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="zendesk_chat_inspect",
    docs_tool="zendesk_chat_read_docs",
)
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ZendeskChatConnector.agent_tool(framework="pydantic_ai")
async def zendesk_chat_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ZendeskChatConnector.agent_tool(framework="pydantic_ai")
async def zendesk_chat_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

@ZendeskChatConnector.agent_tool(
    inspect_tool="zendesk_chat_inspect",
    docs_tool="zendesk_chat_read_docs",
)
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ZendeskChatConnector.agent_tool()
async def zendesk_chat_inspect():
    return await connector.inspect_connector()

@ZendeskChatConnector.agent_tool()
async def zendesk_chat_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (zendesk_chat_inspect, zendesk_chat_read_docs, zendesk_chat_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ZendeskChatConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ZendeskChatConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

@tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskChatConnector.tool_utils(framework="openai_agents")
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Chat Assistant", tools=[zendesk_chat_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    ),
    subdomain="<Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)>"
)

mcp = FastMCP("Zendesk-Chat Agent")

@mcp.tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.10