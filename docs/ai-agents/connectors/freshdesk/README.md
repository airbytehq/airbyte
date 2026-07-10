# Freshdesk

The Freshdesk agent connector is a Python package that equips AI agents to interact with Freshdesk through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Freshdesk customer support platform API (v2). Provides read access to helpdesk data including tickets, contacts, agents, groups, companies, roles, satisfaction ratings, surveys, time entries, and ticket fields. Freshdesk is a cloud-based customer support solution that enables companies to manage customer conversations across email, phone, chat, and social media.


## Example prompts

The Freshdesk connector is optimized to handle prompts like these.

- List all open tickets in Freshdesk
- Show me all agents in the support team
- List all groups configured in Freshdesk
- Get the details of ticket #26
- Show me all companies in Freshdesk
- List all roles defined in the helpdesk
- Show me the ticket fields and their options
- List time entries for tickets
- What are the high priority tickets from last week?
- Which tickets have breached their SLA due date?
- Show me tickets assigned to agent \{agent_name\}
- Find all tickets from company \{company_name\}
- How many tickets were created this month by status?
- What are the satisfaction ratings for resolved tickets?

## Unsupported prompts

The Freshdesk connector isn't currently able to handle prompts like these.

- Create a new ticket in Freshdesk
- Update the status of ticket #\{ticket_id\}
- Delete a contact from Freshdesk
- Assign a ticket to a different agent

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [Context Store Search](./REFERENCE.md#tickets-context-store-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Agents | [List](./REFERENCE.md#agents-list), [Get](./REFERENCE.md#agents-get), [Context Store Search](./REFERENCE.md#agents-context-store-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get), [Context Store Search](./REFERENCE.md#groups-context-store-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get), [Context Store Search](./REFERENCE.md#companies-context-store-search) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get), [Context Store Search](./REFERENCE.md#roles-context-store-search) |
| Satisfaction Ratings | [List](./REFERENCE.md#satisfaction-ratings-list), [Context Store Search](./REFERENCE.md#satisfaction-ratings-context-store-search) |
| Surveys | [List](./REFERENCE.md#surveys-list), [Context Store Search](./REFERENCE.md#surveys-context-store-search) |
| Time Entries | [List](./REFERENCE.md#time-entries-list), [Context Store Search](./REFERENCE.md#time-entries-context-store-search) |
| Ticket Fields | [List](./REFERENCE.md#ticket-fields-list), [Context Store Search](./REFERENCE.md#ticket-fields-context-store-search) |


## Freshdesk API docs

See the official [Freshdesk API reference](https://developers.freshdesk.com/api/).

## Interfaces

Use the Freshdesk connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "freshdesk"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "freshdesk"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "freshdesk",
  "entity": "tickets",
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

The `connect()` factory returns a fully typed `FreshdeskConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Freshdesk Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

mcp = FastMCP("Freshdesk Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `FreshdeskConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

@tool
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Freshdesk connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@FreshdeskConnector.tool_utils(framework="openai_agents")
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Freshdesk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Freshdesk Assistant", tools=[freshdesk_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector

connector = connect("freshdesk", workspace_name="<your_workspace_name>")

mcp = FastMCP("Freshdesk Agent")

@mcp.tool
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Freshdesk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FreshdeskConnector(
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
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FreshdeskConnector(
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
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FreshdeskConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Freshdesk Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = FreshdeskConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Freshdesk Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
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
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Freshdesk Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

mcp = FastMCP("Freshdesk Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `FreshdeskConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

@tool
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Freshdesk connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@FreshdeskConnector.tool_utils(framework="openai_agents")
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Freshdesk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Freshdesk Assistant", tools=[freshdesk_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.freshdesk import FreshdeskConnector
from airbyte_agent_sdk.connectors.freshdesk.models import FreshdeskAuthConfig

connector = FreshdeskConnector(
    auth_config=FreshdeskAuthConfig(
        api_key="<Your Freshdesk API key (found in Profile Settings)>"
    )
)

mcp = FastMCP("Freshdesk Agent")

@mcp.tool
@FreshdeskConnector.tool_utils
async def freshdesk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Freshdesk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.3