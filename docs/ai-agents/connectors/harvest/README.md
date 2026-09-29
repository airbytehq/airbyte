# Harvest

The Harvest agent connector is a Python package that equips AI agents to interact with Harvest through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Harvest time-tracking and invoicing API (v2). Provides read access
to time tracking data including users, clients, projects, tasks, time entries, invoices,
estimates, expenses, and more. Harvest is a cloud-based time tracking and invoicing
solution that helps teams track time, manage projects, and streamline invoicing.


## Example prompts

The Harvest connector is optimized to handle prompts like these.

- List all users in Harvest
- Show me all active projects
- List all clients
- Show me recent time entries
- List all invoices
- Show me all tasks
- List all expense categories
- Get company information
- How many hours were logged last week?
- Which projects have the most time entries?
- Show me all unbilled time entries
- What are the active projects for a specific client?
- List all overdue invoices
- Which users logged the most hours this month?

## Unsupported prompts

The Harvest connector isn't currently able to handle prompts like these.

- Create a new time entry in Harvest
- Update a project budget
- Delete an invoice
- Start a timer for a task

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search), [Context Store SQL Query](./REFERENCE.md#users-context-store-sql-query) |
| Clients | [List](./REFERENCE.md#clients-list), [Get](./REFERENCE.md#clients-get), [Context Store Search](./REFERENCE.md#clients-context-store-search), [Context Store SQL Query](./REFERENCE.md#clients-context-store-sql-query) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Context Store Search](./REFERENCE.md#contacts-context-store-search), [Context Store SQL Query](./REFERENCE.md#contacts-context-store-sql-query) |
| Company | [Get](./REFERENCE.md#company-get), [Context Store Search](./REFERENCE.md#company-context-store-search), [Context Store SQL Query](./REFERENCE.md#company-context-store-sql-query) |
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Context Store Search](./REFERENCE.md#projects-context-store-search), [Context Store SQL Query](./REFERENCE.md#projects-context-store-sql-query) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Context Store Search](./REFERENCE.md#tasks-context-store-search), [Context Store SQL Query](./REFERENCE.md#tasks-context-store-sql-query) |
| Time Entries | [List](./REFERENCE.md#time-entries-list), [Get](./REFERENCE.md#time-entries-get), [Context Store Search](./REFERENCE.md#time-entries-context-store-search), [Context Store SQL Query](./REFERENCE.md#time-entries-context-store-sql-query) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Context Store Search](./REFERENCE.md#invoices-context-store-search), [Context Store SQL Query](./REFERENCE.md#invoices-context-store-sql-query) |
| Invoice Item Categories | [List](./REFERENCE.md#invoice-item-categories-list), [Get](./REFERENCE.md#invoice-item-categories-get), [Context Store Search](./REFERENCE.md#invoice-item-categories-context-store-search), [Context Store SQL Query](./REFERENCE.md#invoice-item-categories-context-store-sql-query) |
| Estimates | [List](./REFERENCE.md#estimates-list), [Get](./REFERENCE.md#estimates-get), [Context Store Search](./REFERENCE.md#estimates-context-store-search), [Context Store SQL Query](./REFERENCE.md#estimates-context-store-sql-query) |
| Estimate Item Categories | [List](./REFERENCE.md#estimate-item-categories-list), [Get](./REFERENCE.md#estimate-item-categories-get), [Context Store Search](./REFERENCE.md#estimate-item-categories-context-store-search), [Context Store SQL Query](./REFERENCE.md#estimate-item-categories-context-store-sql-query) |
| Expenses | [List](./REFERENCE.md#expenses-list), [Get](./REFERENCE.md#expenses-get), [Context Store Search](./REFERENCE.md#expenses-context-store-search), [Context Store SQL Query](./REFERENCE.md#expenses-context-store-sql-query) |
| Expense Categories | [List](./REFERENCE.md#expense-categories-list), [Get](./REFERENCE.md#expense-categories-get), [Context Store Search](./REFERENCE.md#expense-categories-context-store-search), [Context Store SQL Query](./REFERENCE.md#expense-categories-context-store-sql-query) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get), [Context Store Search](./REFERENCE.md#roles-context-store-search), [Context Store SQL Query](./REFERENCE.md#roles-context-store-sql-query) |
| User Assignments | [List](./REFERENCE.md#user-assignments-list), [Context Store Search](./REFERENCE.md#user-assignments-context-store-search), [Context Store SQL Query](./REFERENCE.md#user-assignments-context-store-sql-query) |
| Task Assignments | [List](./REFERENCE.md#task-assignments-list), [Context Store Search](./REFERENCE.md#task-assignments-context-store-search), [Context Store SQL Query](./REFERENCE.md#task-assignments-context-store-sql-query) |
| Time Projects | [List](./REFERENCE.md#time-projects-list), [Context Store Search](./REFERENCE.md#time-projects-context-store-search), [Context Store SQL Query](./REFERENCE.md#time-projects-context-store-sql-query) |
| Time Tasks | [List](./REFERENCE.md#time-tasks-list), [Context Store Search](./REFERENCE.md#time-tasks-context-store-search), [Context Store SQL Query](./REFERENCE.md#time-tasks-context-store-sql-query) |


## Harvest API docs

See the official [Harvest API reference](https://help.getharvest.com/api-v2/).

## Interfaces

Use the Harvest connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "harvest"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "harvest"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "harvest",
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

The `connect()` factory returns a fully typed `HarvestConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Harvest Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

mcp = FastMCP("Harvest Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `HarvestConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HarvestConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="harvest_inspect",
    docs_tool="harvest_read_docs",
)
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@HarvestConnector.agent_tool(framework="pydantic_ai")
async def harvest_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@HarvestConnector.agent_tool(framework="pydantic_ai")
async def harvest_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

@HarvestConnector.agent_tool(
    inspect_tool="harvest_inspect",
    docs_tool="harvest_read_docs",
)
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@HarvestConnector.agent_tool()
async def harvest_inspect():
    return await connector.inspect_connector()

@HarvestConnector.agent_tool()
async def harvest_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (harvest_inspect, harvest_read_docs, harvest_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `HarvestConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `HarvestConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

@tool
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Harvest connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@HarvestConnector.tool_utils(framework="openai_agents")
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Harvest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Harvest Assistant", tools=[harvest_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.harvest import HarvestConnector

connector = connect("harvest", workspace_name="<your_workspace_name>")

mcp = FastMCP("Harvest Agent")

@mcp.tool
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Harvest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HarvestConnector(
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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HarvestConnector(
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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HarvestConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Harvest Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HarvestConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Harvest Agent")

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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Harvest Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

mcp = FastMCP("Harvest Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `HarvestConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HarvestConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="harvest_inspect",
    docs_tool="harvest_read_docs",
)
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@HarvestConnector.agent_tool(framework="pydantic_ai")
async def harvest_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@HarvestConnector.agent_tool(framework="pydantic_ai")
async def harvest_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

@HarvestConnector.agent_tool(
    inspect_tool="harvest_inspect",
    docs_tool="harvest_read_docs",
)
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@HarvestConnector.agent_tool()
async def harvest_inspect():
    return await connector.inspect_connector()

@HarvestConnector.agent_tool()
async def harvest_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (harvest_inspect, harvest_read_docs, harvest_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `HarvestConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `HarvestConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

@tool
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Harvest connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@HarvestConnector.tool_utils(framework="openai_agents")
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Harvest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Harvest Assistant", tools=[harvest_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.harvest import HarvestConnector
from airbyte_agent_sdk.connectors.harvest.models import HarvestPersonalAccessTokenAuthConfig

connector = HarvestConnector(
    auth_config=HarvestPersonalAccessTokenAuthConfig(
        token="<Your Harvest personal access token>",
        account_id="<Your Harvest account ID>"
    )
)

mcp = FastMCP("Harvest Agent")

@mcp.tool
@HarvestConnector.tool_utils
async def harvest_execute(entity: str, action: str, params: dict | None = None):
    """Execute Harvest connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.5