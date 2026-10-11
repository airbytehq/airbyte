# Intercom

The Intercom agent connector is a Python package that equips AI agents to interact with Intercom through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Intercom is a customer messaging platform that enables businesses to communicate with
customers through chat, email, and in-app messaging. This connector provides access
to core Intercom entities including contacts, conversations, companies, teams,
admins, tags, and segments for customer support analytics and insights. It supports
creating, updating, and deleting contacts and companies; creating and deleting tags;
creating, updating, and deleting conversations; creating notes; and creating, updating,
and deleting internal articles.


## Example prompts

The Intercom connector is optimized to handle prompts like these.

- List all contacts in my Intercom workspace
- List all companies in Intercom
- What teams are configured in my workspace?
- Show me all admins in my Intercom account
- List all tags used in Intercom
- Show me all customer segments
- Show me details for a recent contact
- Show me details for a recent company
- Show me details for a recent conversation
- Create a new lead contact named 'Jane Smith' with email jane@example.com
- Create an internal article titled 'Onboarding Guide' with instructions for new team members
- Create a company named 'Acme Corp' with company_id 'acme-001'
- Create a tag named 'VIP Customer'
- Create a conversation from contact \{id\} saying 'I need help with my account'
- Update the name of contact \{id\} to 'John Updated'
- Add a note to contact \{id\} saying 'Followed up on support request'
- Show me conversations from the last week
- List conversations assigned to team \{team_id\}
- Show me open conversations
- Delete contact \{id\}
- Delete company \{id\}
- Delete tag \{id\}
- Delete conversation \{id\}
- Delete internal article \{id\}
- Update conversation \{id\} to mark it as read
- Update internal article \{id\} with a new title

## Unsupported prompts

The Intercom connector isn't currently able to handle prompts like these.

- Send a message to a customer
- Assign a conversation to an admin

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [Delete](./REFERENCE.md#contacts-delete), [Context Store Search](./REFERENCE.md#contacts-context-store-search), [Context Store SQL Query](./REFERENCE.md#contacts-context-store-sql-query) |
| Conversations | [List](./REFERENCE.md#conversations-list), [Create](./REFERENCE.md#conversations-create), [Get](./REFERENCE.md#conversations-get), [Update](./REFERENCE.md#conversations-update), [Delete](./REFERENCE.md#conversations-delete), [Context Store Search](./REFERENCE.md#conversations-context-store-search), [Context Store SQL Query](./REFERENCE.md#conversations-context-store-sql-query), [Semantic Search](./REFERENCE.md#conversations-semantic-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Create](./REFERENCE.md#companies-create), [Get](./REFERENCE.md#companies-get), [Update](./REFERENCE.md#companies-update), [Delete](./REFERENCE.md#companies-delete), [Context Store Search](./REFERENCE.md#companies-context-store-search), [Context Store SQL Query](./REFERENCE.md#companies-context-store-sql-query) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search), [Context Store SQL Query](./REFERENCE.md#teams-context-store-sql-query) |
| Admins | [List](./REFERENCE.md#admins-list), [Get](./REFERENCE.md#admins-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Create](./REFERENCE.md#tags-create), [Get](./REFERENCE.md#tags-get), [Delete](./REFERENCE.md#tags-delete) |
| Notes | [Create](./REFERENCE.md#notes-create) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get) |
| Internal Articles | [Create](./REFERENCE.md#internal-articles-create), [Update](./REFERENCE.md#internal-articles-update), [Delete](./REFERENCE.md#internal-articles-delete) |


## Intercom API docs

See the official [Intercom API reference](https://developers.intercom.com/docs/references/rest-api/api.intercom.io).

## Interfaces

Use the Intercom connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "intercom"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "intercom"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "intercom",
  "entity": "contacts",
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

The `connect()` factory returns a fully typed `IntercomConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Intercom Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

mcp = FastMCP("Intercom Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `IntercomConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="intercom_inspect",
    docs_tool="intercom_read_docs",
)
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@IntercomConnector.agent_tool(framework="pydantic_ai")
async def intercom_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@IntercomConnector.agent_tool(framework="pydantic_ai")
async def intercom_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

@IntercomConnector.agent_tool(
    inspect_tool="intercom_inspect",
    docs_tool="intercom_read_docs",
)
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@IntercomConnector.agent_tool()
async def intercom_inspect():
    return await connector.inspect_connector()

@IntercomConnector.agent_tool()
async def intercom_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (intercom_inspect, intercom_read_docs, intercom_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `IntercomConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `IntercomConnector.agent_tool` above.

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
from airbyte_agent_sdk import build_connector_tools
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

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
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

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Intercom Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
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
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
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
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Intercom Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

mcp = FastMCP("Intercom Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `IntercomConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="intercom_inspect",
    docs_tool="intercom_read_docs",
)
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@IntercomConnector.agent_tool(framework="pydantic_ai")
async def intercom_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@IntercomConnector.agent_tool(framework="pydantic_ai")
async def intercom_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

@IntercomConnector.agent_tool(
    inspect_tool="intercom_inspect",
    docs_tool="intercom_read_docs",
)
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@IntercomConnector.agent_tool()
async def intercom_inspect():
    return await connector.inspect_connector()

@IntercomConnector.agent_tool()
async def intercom_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (intercom_inspect, intercom_read_docs, intercom_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `IntercomConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `IntercomConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
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
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
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
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
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
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
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


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.10