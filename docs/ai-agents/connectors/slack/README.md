# Slack

The Slack agent connector is a Python package that equips AI agents to interact with Slack through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Slack is a business communication platform that offers messaging, file sharing, and integrations
with other tools. This connector provides read access to users, channels, channel members, channel
messages, and threads for workspace analytics. It also supports write operations including sending,
updating, deleting, and scheduling messages, sending ephemeral messages, creating and renaming
channels, archiving channels, joining channels, removing users from channels, setting channel topics
and purposes, adding and removing reactions, pinning messages, adding bookmarks, and inviting users
to channels.


## Example prompts

The Slack connector is optimized to handle prompts like these.

- List all users in my Slack workspace
- Show me all public channels
- List members of a public channel
- Show me recent messages in a public channel
- Show me thread replies for a recent message
- List all channels I have access to
- Show me user details for a workspace member
- List channel members for a public channel
- Send a message to a channel saying 'Hello team!'
- Post a message in the general channel
- Update the most recent message in a channel
- Create a new public channel called 'project-updates'
- Create a private channel named 'team-internal'
- Rename a channel to 'new-channel-name'
- Set the topic for a channel to 'Daily standup notes'
- Update the purpose of a channel
- Add a thumbsup reaction to the latest message in a channel
- React with :rocket: to the latest message in a channel
- Reply to a recent thread with 'Thanks for the update!'
- Invite a user to a channel
- Add a team member to the #project-updates channel
- Send an ephemeral message to a user in a channel
- Whisper a private reminder to a user in #general
- Schedule a message in a channel for tomorrow at 9am
- Send a reminder to a channel at 5pm today
- Delete the bot's last message in a channel
- Remove the :thumbsup: reaction from a message
- Archive the #old-project channel
- Remove a user from the #team channel
- Pin the latest important message in a channel
- Add a bookmark link to a channel
- Join the #announcements channel
- Have the bot join a public channel
- What messages were posted in channel \{channel_id\} last week?
- Show me the conversation history for channel \{channel_id\}
- Search for messages mentioning \{keyword\} in channel \{channel_id\}

## Unsupported prompts

The Slack connector isn't currently able to handle prompts like these.

- Delete channel \{channel_id\}
- Create a new user in the workspace
- Update user profile information
- Unarchive a channel

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search), [Context Store SQL Query](./REFERENCE.md#users-context-store-sql-query) |
| Channels | [List](./REFERENCE.md#channels-list), [Get](./REFERENCE.md#channels-get), [Create](./REFERENCE.md#channels-create), [Update](./REFERENCE.md#channels-update), [Context Store Search](./REFERENCE.md#channels-context-store-search), [Context Store SQL Query](./REFERENCE.md#channels-context-store-sql-query) |
| Channel Messages | [List](./REFERENCE.md#channel-messages-list), [Context Store Search](./REFERENCE.md#channel-messages-context-store-search), [Context Store SQL Query](./REFERENCE.md#channel-messages-context-store-sql-query), [Semantic Search](./REFERENCE.md#channel-messages-semantic-search) |
| Threads | [List](./REFERENCE.md#threads-list), [Context Store Search](./REFERENCE.md#threads-context-store-search), [Context Store SQL Query](./REFERENCE.md#threads-context-store-sql-query), [Semantic Search](./REFERENCE.md#threads-semantic-search) |
| Messages | [Create](./REFERENCE.md#messages-create), [Update](./REFERENCE.md#messages-update), [Delete](./REFERENCE.md#messages-delete) |
| Channel Topics | [Create](./REFERENCE.md#channel-topics-create) |
| Channel Purposes | [Create](./REFERENCE.md#channel-purposes-create) |
| Channel Invites | [Create](./REFERENCE.md#channel-invites-create) |
| Reactions | [Create](./REFERENCE.md#reactions-create), [Delete](./REFERENCE.md#reactions-delete) |
| Ephemeral Messages | [Create](./REFERENCE.md#ephemeral-messages-create) |
| Scheduled Messages | [Create](./REFERENCE.md#scheduled-messages-create) |
| Channel Archives | [Create](./REFERENCE.md#channel-archives-create) |
| Channel Kicks | [Create](./REFERENCE.md#channel-kicks-create) |
| Channel Joins | [Create](./REFERENCE.md#channel-joins-create) |
| Pins | [Create](./REFERENCE.md#pins-create) |
| Bookmarks | [Create](./REFERENCE.md#bookmarks-create) |


## Slack API docs

See the official [Slack API reference](https://api.slack.com/methods).

## Interfaces

Use the Slack connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "slack"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "slack"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "slack",
  "entity": "users",
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

The `connect()` factory returns a fully typed `SlackConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Slack Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

mcp = FastMCP("Slack Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `SlackConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SlackConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="slack_inspect",
    docs_tool="slack_read_docs",
)
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@SlackConnector.agent_tool(framework="pydantic_ai")
async def slack_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@SlackConnector.agent_tool(framework="pydantic_ai")
async def slack_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

@SlackConnector.agent_tool(
    inspect_tool="slack_inspect",
    docs_tool="slack_read_docs",
)
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@SlackConnector.agent_tool()
async def slack_inspect():
    return await connector.inspect_connector()

@SlackConnector.agent_tool()
async def slack_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (slack_inspect, slack_read_docs, slack_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `SlackConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `SlackConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

@tool
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    """Execute Slack connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SlackConnector.tool_utils(framework="openai_agents")
async def slack_execute(entity: str, action: str, params: dict | None = None):
    """Execute Slack connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Slack Assistant", tools=[slack_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.slack import SlackConnector

connector = connect("slack", workspace_name="<your_workspace_name>")

mcp = FastMCP("Slack Agent")

@mcp.tool
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    """Execute Slack connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SlackConnector(
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
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SlackConnector(
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
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SlackConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Slack Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SlackConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Slack Agent")

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
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
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
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Slack Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

mcp = FastMCP("Slack Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `SlackConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SlackConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="slack_inspect",
    docs_tool="slack_read_docs",
)
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@SlackConnector.agent_tool(framework="pydantic_ai")
async def slack_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@SlackConnector.agent_tool(framework="pydantic_ai")
async def slack_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

@SlackConnector.agent_tool(
    inspect_tool="slack_inspect",
    docs_tool="slack_read_docs",
)
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@SlackConnector.agent_tool()
async def slack_inspect():
    return await connector.inspect_connector()

@SlackConnector.agent_tool()
async def slack_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (slack_inspect, slack_read_docs, slack_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `SlackConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `SlackConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

@tool
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    """Execute Slack connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SlackConnector.tool_utils(framework="openai_agents")
async def slack_execute(entity: str, action: str, params: dict | None = None):
    """Execute Slack connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Slack Assistant", tools=[slack_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.slack import SlackConnector
from airbyte_agent_sdk.connectors.slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        bot_key="<Your Slack Bot Key (xoxb-) or User Token (xoxp-)>"
    )
)

mcp = FastMCP("Slack Agent")

@mcp.tool
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    """Execute Slack connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.22