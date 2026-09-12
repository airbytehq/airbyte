# Mailchimp

The Mailchimp agent connector is a Python package that equips AI agents to interact with Mailchimp through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Mailchimp is an email marketing platform that enables businesses to create, send, and analyze
email campaigns, manage subscriber lists, and automate marketing workflows. This connector
provides read access to campaigns, lists, reports, email activity, automations, and more
for marketing analytics and audience management.


## Example prompts

The Mailchimp connector is optimized to handle prompts like these.

- List all subscribers in my main mailing list
- List all automation workflows in my account
- Show me all segments for my primary audience
- List all interest categories for my primary audience
- Show me email activity for a recent campaign
- Show me the performance report for a recent campaign
- Show me all my email campaigns from the last month
- What are the open rates for my recent campaigns?
- Who unsubscribed from list \{list_id\} this week?
- What tags are applied to my subscribers?
- How many subscribers do I have in each list?
- What are my top performing campaigns by click rate?

## Unsupported prompts

The Mailchimp connector isn't currently able to handle prompts like these.

- Create a new email campaign
- Add a subscriber to my list
- Delete a campaign
- Update subscriber information
- Send a campaign now
- Create a new automation workflow

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search), [Context Store SQL Query](./REFERENCE.md#campaigns-context-store-sql-query) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get), [Context Store Search](./REFERENCE.md#lists-context-store-search), [Context Store SQL Query](./REFERENCE.md#lists-context-store-sql-query) |
| List Members | [List](./REFERENCE.md#list-members-list), [Get](./REFERENCE.md#list-members-get), [Context Store Search](./REFERENCE.md#list-members-context-store-search), [Context Store SQL Query](./REFERENCE.md#list-members-context-store-sql-query) |
| Reports | [List](./REFERENCE.md#reports-list), [Get](./REFERENCE.md#reports-get), [Context Store Search](./REFERENCE.md#reports-context-store-search), [Context Store SQL Query](./REFERENCE.md#reports-context-store-sql-query) |
| Email Activity | [List](./REFERENCE.md#email-activity-list), [Context Store Search](./REFERENCE.md#email-activity-context-store-search), [Context Store SQL Query](./REFERENCE.md#email-activity-context-store-sql-query) |
| Automations | [List](./REFERENCE.md#automations-list), [Context Store Search](./REFERENCE.md#automations-context-store-search), [Context Store SQL Query](./REFERENCE.md#automations-context-store-sql-query) |
| Tags | [List](./REFERENCE.md#tags-list), [Context Store Search](./REFERENCE.md#tags-context-store-search), [Context Store SQL Query](./REFERENCE.md#tags-context-store-sql-query) |
| Interest Categories | [List](./REFERENCE.md#interest-categories-list), [Get](./REFERENCE.md#interest-categories-get), [Context Store Search](./REFERENCE.md#interest-categories-context-store-search), [Context Store SQL Query](./REFERENCE.md#interest-categories-context-store-sql-query) |
| Interests | [List](./REFERENCE.md#interests-list), [Get](./REFERENCE.md#interests-get), [Context Store Search](./REFERENCE.md#interests-context-store-search), [Context Store SQL Query](./REFERENCE.md#interests-context-store-sql-query) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get), [Context Store Search](./REFERENCE.md#segments-context-store-search), [Context Store SQL Query](./REFERENCE.md#segments-context-store-sql-query) |
| Segment Members | [List](./REFERENCE.md#segment-members-list), [Context Store Search](./REFERENCE.md#segment-members-context-store-search), [Context Store SQL Query](./REFERENCE.md#segment-members-context-store-sql-query) |
| Unsubscribes | [List](./REFERENCE.md#unsubscribes-list), [Context Store Search](./REFERENCE.md#unsubscribes-context-store-search), [Context Store SQL Query](./REFERENCE.md#unsubscribes-context-store-sql-query) |


## Mailchimp API docs

See the official [Mailchimp API reference](https://mailchimp.com/developer/marketing/api/).

## Interfaces

Use the Mailchimp connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "mailchimp"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "mailchimp"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "mailchimp",
  "entity": "campaigns",
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

The `connect()` factory returns a fully typed `MailchimpConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Mailchimp Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

mcp = FastMCP("Mailchimp Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `MailchimpConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MailchimpConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="mailchimp_inspect",
    docs_tool="mailchimp_read_docs",
)
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@MailchimpConnector.agent_tool(framework="pydantic_ai")
async def mailchimp_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@MailchimpConnector.agent_tool(framework="pydantic_ai")
async def mailchimp_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

@MailchimpConnector.agent_tool(
    inspect_tool="mailchimp_inspect",
    docs_tool="mailchimp_read_docs",
)
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@MailchimpConnector.agent_tool()
async def mailchimp_inspect():
    return await connector.inspect_connector()

@MailchimpConnector.agent_tool()
async def mailchimp_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (mailchimp_inspect, mailchimp_read_docs, mailchimp_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `MailchimpConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `MailchimpConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

@tool
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    """Execute Mailchimp connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@MailchimpConnector.tool_utils(framework="openai_agents")
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    """Execute Mailchimp connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Mailchimp Assistant", tools=[mailchimp_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector

connector = connect("mailchimp", workspace_name="<your_workspace_name>")

mcp = FastMCP("Mailchimp Agent")

@mcp.tool
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    """Execute Mailchimp connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MailchimpConnector(
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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MailchimpConnector(
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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MailchimpConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Mailchimp Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = MailchimpConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Mailchimp Agent")

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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Mailchimp Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

mcp = FastMCP("Mailchimp Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `MailchimpConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MailchimpConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="mailchimp_inspect",
    docs_tool="mailchimp_read_docs",
)
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@MailchimpConnector.agent_tool(framework="pydantic_ai")
async def mailchimp_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@MailchimpConnector.agent_tool(framework="pydantic_ai")
async def mailchimp_read_docs(section: str | None = None):
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
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

@MailchimpConnector.agent_tool(
    inspect_tool="mailchimp_inspect",
    docs_tool="mailchimp_read_docs",
)
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@MailchimpConnector.agent_tool()
async def mailchimp_inspect():
    return await connector.inspect_connector()

@MailchimpConnector.agent_tool()
async def mailchimp_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (mailchimp_inspect, mailchimp_read_docs, mailchimp_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `MailchimpConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `MailchimpConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

@tool
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    """Execute Mailchimp connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@MailchimpConnector.tool_utils(framework="openai_agents")
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    """Execute Mailchimp connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Mailchimp Assistant", tools=[mailchimp_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.mailchimp import MailchimpConnector
from airbyte_agent_sdk.connectors.mailchimp.models import MailchimpAuthConfig

connector = MailchimpConnector(
    auth_config=MailchimpAuthConfig(
        api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>"
    ),
    data_center="<The data center for your Mailchimp account (e.g., us1, us2, us6)>"
)

mcp = FastMCP("Mailchimp Agent")

@mcp.tool
@MailchimpConnector.tool_utils
async def mailchimp_execute(entity: str, action: str, params: dict | None = None):
    """Execute Mailchimp connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.11