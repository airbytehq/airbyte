# Zoho-Crm

The Zoho-Crm agent connector is a Python package that equips AI agents to interact with Zoho-Crm through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zoho CRM API, providing access to CRM modules including leads, contacts, accounts, deals, campaigns, tasks, events, calls, products, quotes, and invoices. Supports OAuth 2.0 authentication with regional data center support (US, EU, AU, IN, CN, JP). Supports read operations (list and get) for all entities.


## Example prompts

The Zoho-Crm connector is optimized to handle prompts like these.

- List all leads
- Show me details for a specific lead
- List all contacts
- List all accounts
- List all open deals
- Show me details for a specific deal
- List all campaigns
- List all tasks
- List all events
- List recent calls
- List all products
- List all quotes
- List all invoices
- List all notes
- Show me details for a specific note
- Show me details for a specific call
- Show me details for a specific campaign
- Show me details for a specific event
- Show me details for a specific invoice
- Show me details for a specific product
- Show me details for a specific quote
- Show me details for a specific account
- Show me details for a specific contact
- Show me details for a specific task
- Show me leads created in the last 30 days
- Which deals have the highest amount?
- List all contacts at a specific company
- What is the total revenue across all deals by stage?
- Show me overdue tasks
- Which campaigns generated the most leads?
- Summarize the deal pipeline by stage
- Show me accounts with the highest annual revenue
- List all events scheduled for this week
- What are the top-performing products by unit price?
- Show me all invoices that are past due
- Break down leads by source and industry

## Unsupported prompts

The Zoho-Crm connector isn't currently able to handle prompts like these.

- Delete a deal record
- Send an email to a lead
- Convert a lead to a contact
- Merge duplicate contacts
- Bulk import leads from CSV
- Create a workflow rule

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Leads | [List](./REFERENCE.md#leads-list), [Get](./REFERENCE.md#leads-get), [Context Store Search](./REFERENCE.md#leads-context-store-search), [Context Store SQL Query](./REFERENCE.md#leads-context-store-sql-query), [Semantic Search](./REFERENCE.md#leads-semantic-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Context Store Search](./REFERENCE.md#contacts-context-store-search), [Context Store SQL Query](./REFERENCE.md#contacts-context-store-sql-query), [Semantic Search](./REFERENCE.md#contacts-semantic-search) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Context Store Search](./REFERENCE.md#accounts-context-store-search), [Context Store SQL Query](./REFERENCE.md#accounts-context-store-sql-query), [Semantic Search](./REFERENCE.md#accounts-semantic-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Get](./REFERENCE.md#deals-get), [Context Store Search](./REFERENCE.md#deals-context-store-search), [Context Store SQL Query](./REFERENCE.md#deals-context-store-sql-query), [Semantic Search](./REFERENCE.md#deals-semantic-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search), [Context Store SQL Query](./REFERENCE.md#campaigns-context-store-sql-query), [Semantic Search](./REFERENCE.md#campaigns-semantic-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [Context Store Search](./REFERENCE.md#tasks-context-store-search), [Context Store SQL Query](./REFERENCE.md#tasks-context-store-sql-query), [Semantic Search](./REFERENCE.md#tasks-semantic-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Context Store Search](./REFERENCE.md#events-context-store-search), [Context Store SQL Query](./REFERENCE.md#events-context-store-sql-query), [Semantic Search](./REFERENCE.md#events-semantic-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search), [Context Store SQL Query](./REFERENCE.md#calls-context-store-sql-query), [Semantic Search](./REFERENCE.md#calls-semantic-search) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get), [Context Store Search](./REFERENCE.md#products-context-store-search), [Context Store SQL Query](./REFERENCE.md#products-context-store-sql-query), [Semantic Search](./REFERENCE.md#products-semantic-search) |
| Quotes | [List](./REFERENCE.md#quotes-list), [Get](./REFERENCE.md#quotes-get), [Context Store Search](./REFERENCE.md#quotes-context-store-search), [Context Store SQL Query](./REFERENCE.md#quotes-context-store-sql-query) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Context Store Search](./REFERENCE.md#invoices-context-store-search), [Context Store SQL Query](./REFERENCE.md#invoices-context-store-sql-query) |
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [Context Store Search](./REFERENCE.md#notes-context-store-search), [Context Store SQL Query](./REFERENCE.md#notes-context-store-sql-query), [Semantic Search](./REFERENCE.md#notes-semantic-search) |


## Zoho-Crm API docs

See the official [Zoho-Crm API reference](https://www.zoho.com/crm/developer/docs/api/v2/).

## Interfaces

Use the Zoho-Crm connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "zoho-crm"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "zoho-crm",
  "entity": "leads",
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

The `connect()` factory returns a fully typed `ZohoCrmConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zoho-Crm Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zoho-Crm Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ZohoCrmConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZohoCrmConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="zoho_crm_inspect",
    docs_tool="zoho_crm_read_docs",
)
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ZohoCrmConnector.agent_tool(framework="pydantic_ai")
async def zoho_crm_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ZohoCrmConnector.agent_tool(framework="pydantic_ai")
async def zoho_crm_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

@ZohoCrmConnector.agent_tool(
    inspect_tool="zoho_crm_inspect",
    docs_tool="zoho_crm_read_docs",
)
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ZohoCrmConnector.agent_tool()
async def zoho_crm_inspect():
    return await connector.inspect_connector()

@ZohoCrmConnector.agent_tool()
async def zoho_crm_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (zoho_crm_inspect, zoho_crm_read_docs, zoho_crm_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ZohoCrmConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ZohoCrmConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

@tool
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZohoCrmConnector.tool_utils(framework="openai_agents")
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zoho-Crm Assistant", tools=[zoho_crm_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector

connector = connect("zoho-crm", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zoho-Crm Agent")

@mcp.tool
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZohoCrmConnector(
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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZohoCrmConnector(
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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZohoCrmConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zoho-Crm Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZohoCrmConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Zoho-Crm Agent")

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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Zoho-Crm Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

mcp = FastMCP("Zoho-Crm Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ZohoCrmConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZohoCrmConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="zoho_crm_inspect",
    docs_tool="zoho_crm_read_docs",
)
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ZohoCrmConnector.agent_tool(framework="pydantic_ai")
async def zoho_crm_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ZohoCrmConnector.agent_tool(framework="pydantic_ai")
async def zoho_crm_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

@ZohoCrmConnector.agent_tool(
    inspect_tool="zoho_crm_inspect",
    docs_tool="zoho_crm_read_docs",
)
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ZohoCrmConnector.agent_tool()
async def zoho_crm_inspect():
    return await connector.inspect_connector()

@ZohoCrmConnector.agent_tool()
async def zoho_crm_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (zoho_crm_inspect, zoho_crm_read_docs, zoho_crm_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ZohoCrmConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ZohoCrmConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

@tool
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZohoCrmConnector.tool_utils(framework="openai_agents")
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zoho-Crm Assistant", tools=[zoho_crm_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zoho_crm import ZohoCrmConnector
from airbyte_agent_sdk.connectors.zoho_crm.models import ZohoCrmAuthConfig

connector = ZohoCrmConnector(
    auth_config=ZohoCrmAuthConfig(
        client_id="<OAuth 2.0 Client ID from Zoho Developer Console>",
        client_secret="<OAuth 2.0 Client Secret from Zoho Developer Console>",
        refresh_token="<OAuth 2.0 Refresh Token (does not expire)>"
    ),
    dc_region="<The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
>"
)

mcp = FastMCP("Zoho-Crm Agent")

@mcp.tool
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.1.0