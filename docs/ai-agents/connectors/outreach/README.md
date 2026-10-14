# Outreach

The Outreach agent connector is a Python package that equips AI agents to interact with Outreach through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Outreach sales engagement platform API. Outreach helps sales teams
automate and optimize their outreach workflows through sequences, templates, and
prospect management. This connector provides read access to key Outreach entities
including prospects, accounts, sequences, sequence states, opportunities, calls,
mailings, tasks, users, stages, personas, templates, snippets, mailboxes,
call dispositions, call purposes, and sequence steps.


## Example prompts

The Outreach connector is optimized to handle prompts like these.

- List all prospects in Outreach
- Show me all active sequences
- Get details about my Outreach accounts
- List all users in my Outreach org
- Show me recent calls logged in Outreach
- List all mailings sent
- What tasks are assigned in Outreach?
- Find prospects added last month
- Which sequences have the most active states?
- Show me accounts in the technology industry
- What are the top opportunities by amount?
- Find calls made by a specific user

## Unsupported prompts

The Outreach connector isn't currently able to handle prompts like these.

- Create a new prospect
- Update an account
- Delete a sequence
- Send a mailing
- Add a prospect to a sequence

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Prospects | [List](./REFERENCE.md#prospects-list), [Get](./REFERENCE.md#prospects-get), [Context Store Search](./REFERENCE.md#prospects-context-store-search), [Context Store SQL Query](./REFERENCE.md#prospects-context-store-sql-query) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Context Store Search](./REFERENCE.md#accounts-context-store-search), [Context Store SQL Query](./REFERENCE.md#accounts-context-store-sql-query) |
| Sequences | [List](./REFERENCE.md#sequences-list), [Get](./REFERENCE.md#sequences-get), [Context Store Search](./REFERENCE.md#sequences-context-store-search), [Context Store SQL Query](./REFERENCE.md#sequences-context-store-sql-query) |
| Sequence States | [List](./REFERENCE.md#sequence-states-list), [Get](./REFERENCE.md#sequence-states-get), [Context Store Search](./REFERENCE.md#sequence-states-context-store-search), [Context Store SQL Query](./REFERENCE.md#sequence-states-context-store-sql-query) |
| Sequence Steps | [List](./REFERENCE.md#sequence-steps-list), [Get](./REFERENCE.md#sequence-steps-get), [Context Store Search](./REFERENCE.md#sequence-steps-context-store-search), [Context Store SQL Query](./REFERENCE.md#sequence-steps-context-store-sql-query) |
| Opportunities | [List](./REFERENCE.md#opportunities-list), [Get](./REFERENCE.md#opportunities-get), [Context Store Search](./REFERENCE.md#opportunities-context-store-search), [Context Store SQL Query](./REFERENCE.md#opportunities-context-store-sql-query) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search), [Context Store SQL Query](./REFERENCE.md#calls-context-store-sql-query) |
| Call Dispositions | [List](./REFERENCE.md#call-dispositions-list), [Get](./REFERENCE.md#call-dispositions-get), [Context Store Search](./REFERENCE.md#call-dispositions-context-store-search), [Context Store SQL Query](./REFERENCE.md#call-dispositions-context-store-sql-query) |
| Call Purposes | [List](./REFERENCE.md#call-purposes-list), [Get](./REFERENCE.md#call-purposes-get), [Context Store Search](./REFERENCE.md#call-purposes-context-store-search), [Context Store SQL Query](./REFERENCE.md#call-purposes-context-store-sql-query) |
| Mailings | [List](./REFERENCE.md#mailings-list), [Get](./REFERENCE.md#mailings-get), [Context Store Search](./REFERENCE.md#mailings-context-store-search), [Context Store SQL Query](./REFERENCE.md#mailings-context-store-sql-query) |
| Mailboxes | [List](./REFERENCE.md#mailboxes-list), [Get](./REFERENCE.md#mailboxes-get), [Context Store Search](./REFERENCE.md#mailboxes-context-store-search), [Context Store SQL Query](./REFERENCE.md#mailboxes-context-store-sql-query) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Context Store Search](./REFERENCE.md#tasks-context-store-search), [Context Store SQL Query](./REFERENCE.md#tasks-context-store-sql-query) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search), [Context Store SQL Query](./REFERENCE.md#users-context-store-sql-query) |
| Stages | [List](./REFERENCE.md#stages-list), [Get](./REFERENCE.md#stages-get), [Context Store Search](./REFERENCE.md#stages-context-store-search), [Context Store SQL Query](./REFERENCE.md#stages-context-store-sql-query) |
| Personas | [List](./REFERENCE.md#personas-list), [Get](./REFERENCE.md#personas-get), [Context Store Search](./REFERENCE.md#personas-context-store-search), [Context Store SQL Query](./REFERENCE.md#personas-context-store-sql-query) |
| Templates | [List](./REFERENCE.md#templates-list), [Get](./REFERENCE.md#templates-get), [Context Store Search](./REFERENCE.md#templates-context-store-search), [Context Store SQL Query](./REFERENCE.md#templates-context-store-sql-query) |
| Snippets | [List](./REFERENCE.md#snippets-list), [Get](./REFERENCE.md#snippets-get), [Context Store Search](./REFERENCE.md#snippets-context-store-search), [Context Store SQL Query](./REFERENCE.md#snippets-context-store-sql-query) |


## Outreach API docs

See the official [Outreach API reference](https://developers.outreach.io/api/reference/).

## Interfaces

Use the Outreach connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "outreach"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "prospects",
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

The `connect()` factory returns a fully typed `OutreachConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Outreach Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

mcp = FastMCP("Outreach Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `OutreachConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OutreachConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="outreach_inspect",
    docs_tool="outreach_read_docs",
)
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@OutreachConnector.agent_tool(framework="pydantic_ai")
async def outreach_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@OutreachConnector.agent_tool(framework="pydantic_ai")
async def outreach_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

@OutreachConnector.agent_tool(
    inspect_tool="outreach_inspect",
    docs_tool="outreach_read_docs",
)
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@OutreachConnector.agent_tool()
async def outreach_inspect():
    return await connector.inspect_connector()

@OutreachConnector.agent_tool()
async def outreach_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (outreach_inspect, outreach_read_docs, outreach_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `OutreachConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `OutreachConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OutreachConnector.tool_utils
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

@tool
@OutreachConnector.tool_utils
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    """Execute Outreach connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@OutreachConnector.tool_utils(framework="openai_agents")
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    """Execute Outreach connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Outreach Assistant", tools=[outreach_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.outreach import OutreachConnector

connector = connect("outreach", workspace_name="<your_workspace_name>")

mcp = FastMCP("Outreach Agent")

@mcp.tool
@OutreachConnector.tool_utils
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    """Execute Outreach connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OutreachConnector(
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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OutreachConnector(
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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OutreachConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Outreach Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OutreachConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Outreach Agent")

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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Outreach Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

mcp = FastMCP("Outreach Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `OutreachConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OutreachConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="outreach_inspect",
    docs_tool="outreach_read_docs",
)
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@OutreachConnector.agent_tool(framework="pydantic_ai")
async def outreach_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@OutreachConnector.agent_tool(framework="pydantic_ai")
async def outreach_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

@OutreachConnector.agent_tool(
    inspect_tool="outreach_inspect",
    docs_tool="outreach_read_docs",
)
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@OutreachConnector.agent_tool()
async def outreach_inspect():
    return await connector.inspect_connector()

@OutreachConnector.agent_tool()
async def outreach_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (outreach_inspect, outreach_read_docs, outreach_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `OutreachConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `OutreachConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OutreachConnector.tool_utils
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

@tool
@OutreachConnector.tool_utils
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    """Execute Outreach connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@OutreachConnector.tool_utils(framework="openai_agents")
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    """Execute Outreach connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Outreach Assistant", tools=[outreach_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.outreach import OutreachConnector
from airbyte_agent_sdk.connectors.outreach.models import OutreachAuthConfig

connector = OutreachConnector(
    auth_config=OutreachAuthConfig(
        client_id="<The Client ID of your Outreach developer application>",
        client_secret="<The Client Secret of your Outreach developer application>",
        refresh_token="<The token for obtaining the new access token>"
    )
)

mcp = FastMCP("Outreach Agent")

@mcp.tool
@OutreachConnector.tool_utils
async def outreach_execute(entity: str, action: str, params: dict | None = None):
    """Execute Outreach connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.0