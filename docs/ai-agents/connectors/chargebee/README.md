# Chargebee

The Chargebee agent connector is a Python package that equips AI agents to interact with Chargebee through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Chargebee billing and subscription management API. Supports reading subscriptions, customers, invoices, credit notes, coupons, transactions, events, orders, items, item prices, and payment sources. Chargebee is a recurring billing platform that helps SaaS and subscription businesses manage the full subscription lifecycle.


## Example prompts

The Chargebee connector is optimized to handle prompts like these.

- List all active subscriptions
- Show me details for a specific customer
- List recent invoices
- Show me details for a specific subscription
- List all coupons
- List recent transactions
- List recent events
- Show me customers with the highest monthly recurring revenue
- Which subscriptions are set to cancel in the next 30 days?
- List all overdue invoices and their amounts
- Analyze subscription churn trends over the past quarter
- What are the most popular items by number of subscriptions?
- Show me total revenue breakdown by currency
- Identify customers with expiring payment sources
- Compare subscription plan distribution across item prices
- List all credit notes issued in the past month
- What is the average subscription lifetime for each plan?

## Unsupported prompts

The Chargebee connector isn't currently able to handle prompts like these.

- Create a new subscription in Chargebee
- Update a customer's billing address
- Cancel a subscription
- Apply a coupon to a subscription
- Issue a refund for an invoice

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customer | [List](./REFERENCE.md#customer-list), [Get](./REFERENCE.md#customer-get), [Context Store Search](./REFERENCE.md#customer-context-store-search), [Context Store SQL Query](./REFERENCE.md#customer-context-store-sql-query) |
| Subscription | [List](./REFERENCE.md#subscription-list), [Get](./REFERENCE.md#subscription-get), [Context Store Search](./REFERENCE.md#subscription-context-store-search), [Context Store SQL Query](./REFERENCE.md#subscription-context-store-sql-query) |
| Invoice | [List](./REFERENCE.md#invoice-list), [Get](./REFERENCE.md#invoice-get), [Context Store Search](./REFERENCE.md#invoice-context-store-search), [Context Store SQL Query](./REFERENCE.md#invoice-context-store-sql-query) |
| Credit Note | [List](./REFERENCE.md#credit-note-list), [Get](./REFERENCE.md#credit-note-get), [Context Store Search](./REFERENCE.md#credit-note-context-store-search), [Context Store SQL Query](./REFERENCE.md#credit-note-context-store-sql-query) |
| Coupon | [List](./REFERENCE.md#coupon-list), [Get](./REFERENCE.md#coupon-get), [Context Store Search](./REFERENCE.md#coupon-context-store-search), [Context Store SQL Query](./REFERENCE.md#coupon-context-store-sql-query) |
| Transaction | [List](./REFERENCE.md#transaction-list), [Get](./REFERENCE.md#transaction-get), [Context Store Search](./REFERENCE.md#transaction-context-store-search), [Context Store SQL Query](./REFERENCE.md#transaction-context-store-sql-query) |
| Event | [List](./REFERENCE.md#event-list), [Get](./REFERENCE.md#event-get), [Context Store Search](./REFERENCE.md#event-context-store-search), [Context Store SQL Query](./REFERENCE.md#event-context-store-sql-query) |
| Order | [List](./REFERENCE.md#order-list), [Get](./REFERENCE.md#order-get), [Context Store Search](./REFERENCE.md#order-context-store-search), [Context Store SQL Query](./REFERENCE.md#order-context-store-sql-query) |
| Item | [List](./REFERENCE.md#item-list), [Get](./REFERENCE.md#item-get), [Context Store Search](./REFERENCE.md#item-context-store-search), [Context Store SQL Query](./REFERENCE.md#item-context-store-sql-query) |
| Item Price | [List](./REFERENCE.md#item-price-list), [Get](./REFERENCE.md#item-price-get), [Context Store Search](./REFERENCE.md#item-price-context-store-search), [Context Store SQL Query](./REFERENCE.md#item-price-context-store-sql-query) |
| Payment Source | [List](./REFERENCE.md#payment-source-list), [Get](./REFERENCE.md#payment-source-get), [Context Store Search](./REFERENCE.md#payment-source-context-store-search), [Context Store SQL Query](./REFERENCE.md#payment-source-context-store-sql-query) |


## Chargebee API docs

See the official [Chargebee API reference](https://apidocs.chargebee.com/docs/api).

## Interfaces

Use the Chargebee connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "chargebee"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "chargebee"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "chargebee",
  "entity": "customer",
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

The `connect()` factory returns a fully typed `ChargebeeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Chargebee Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

mcp = FastMCP("Chargebee Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ChargebeeConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ChargebeeConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="chargebee_inspect",
    docs_tool="chargebee_read_docs",
)
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ChargebeeConnector.agent_tool(framework="pydantic_ai")
async def chargebee_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ChargebeeConnector.agent_tool(framework="pydantic_ai")
async def chargebee_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

@ChargebeeConnector.agent_tool(
    inspect_tool="chargebee_inspect",
    docs_tool="chargebee_read_docs",
)
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ChargebeeConnector.agent_tool()
async def chargebee_inspect():
    return await connector.inspect_connector()

@ChargebeeConnector.agent_tool()
async def chargebee_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (chargebee_inspect, chargebee_read_docs, chargebee_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ChargebeeConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ChargebeeConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

@tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ChargebeeConnector.tool_utils(framework="openai_agents")
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Chargebee Assistant", tools=[chargebee_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

mcp = FastMCP("Chargebee Agent")

@mcp.tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Chargebee Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Chargebee Agent")

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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Chargebee Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

mcp = FastMCP("Chargebee Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `ChargebeeConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ChargebeeConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="chargebee_inspect",
    docs_tool="chargebee_read_docs",
)
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@ChargebeeConnector.agent_tool(framework="pydantic_ai")
async def chargebee_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@ChargebeeConnector.agent_tool(framework="pydantic_ai")
async def chargebee_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

@ChargebeeConnector.agent_tool(
    inspect_tool="chargebee_inspect",
    docs_tool="chargebee_read_docs",
)
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@ChargebeeConnector.agent_tool()
async def chargebee_inspect():
    return await connector.inspect_connector()

@ChargebeeConnector.agent_tool()
async def chargebee_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (chargebee_inspect, chargebee_read_docs, chargebee_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `ChargebeeConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `ChargebeeConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

@tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ChargebeeConnector.tool_utils(framework="openai_agents")
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Chargebee Assistant", tools=[chargebee_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    ),
    site="<Your Chargebee site name (subdomain)>"
)

mcp = FastMCP("Chargebee Agent")

@mcp.tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.2