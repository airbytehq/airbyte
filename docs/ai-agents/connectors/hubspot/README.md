# Hubspot

The Hubspot agent connector is a Python package that equips AI agents to interact with Hubspot through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

HubSpot is a CRM platform that provides tools for marketing, sales, customer service,
and content management. This connector provides access to contacts, companies, deals,
tickets, and custom objects for customer relationship management and sales analytics.


## Example prompts

The Hubspot connector is optimized to handle prompts like these.

- List recent deals
- List recent tickets
- List companies in my CRM
- List contacts in my CRM
- Show me all deals from \{company\} this quarter
- What are the top 5 most valuable deals in my pipeline right now?
- Search for contacts in the marketing department at \{company\}
- Give me an overview of my sales team's deals in the last 30 days
- Identify the most active companies in our CRM this month
- Compare the number of deals closed by different sales representatives
- Find all tickets related to a specific product issue and summarize their status

## Unsupported prompts

The Hubspot connector isn't currently able to handle prompts like these.

- Create a new contact record for \{person\}
- Update the contact information for \{customer\}
- Delete the ticket from last week's support case
- Schedule a follow-up task for this deal
- Send an email to all contacts in the sales pipeline

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [API Search](./REFERENCE.md#contacts-api_search), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get), [API Search](./REFERENCE.md#companies-api_search), [Context Store Search](./REFERENCE.md#companies-context-store-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Get](./REFERENCE.md#deals-get), [API Search](./REFERENCE.md#deals-api_search), [Context Store Search](./REFERENCE.md#deals-context-store-search) |
| Tickets | [List](./REFERENCE.md#tickets-list), [Get](./REFERENCE.md#tickets-get), [API Search](./REFERENCE.md#tickets-api_search), [Context Store Search](./REFERENCE.md#tickets-context-store-search) |
| Schemas | [List](./REFERENCE.md#schemas-list), [Get](./REFERENCE.md#schemas-get) |
| Objects | [List](./REFERENCE.md#objects-list), [Get](./REFERENCE.md#objects-get) |


## Hubspot API docs

See the official [Hubspot API reference](https://developers.hubspot.com/docs/api/crm/understanding-the-crm).

## SDK installation

```bash
uv pip install airbyte-agent-sdk
```

## SDK usage

Connectors can run in hosted or open source mode.

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `HubspotConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

@tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@HubspotConnector.tool_utils(framework="openai_agents")
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Hubspot Assistant", tools=[hubspot_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

mcp = FastMCP("Hubspot Agent")

@mcp.tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@HubspotConnector.tool_utils(framework="openai_agents")
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Hubspot Assistant", tools=[hubspot_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Hubspot Agent")

@mcp.tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.connectors.hubspot.models import HubspotPrivateAppAuthConfig

connector = HubspotConnector(
    auth_config=HubspotPrivateAppAuthConfig(
        private_app_token="<Access token from a HubSpot Private App>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.connectors.hubspot.models import HubspotPrivateAppAuthConfig

connector = HubspotConnector(
    auth_config=HubspotPrivateAppAuthConfig(
        private_app_token="<Access token from a HubSpot Private App>"
    )
)

@tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.connectors.hubspot.models import HubspotPrivateAppAuthConfig

connector = HubspotConnector(
    auth_config=HubspotPrivateAppAuthConfig(
        private_app_token="<Access token from a HubSpot Private App>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@HubspotConnector.tool_utils(framework="openai_agents")
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Hubspot Assistant", tools=[hubspot_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.connectors.hubspot.models import HubspotPrivateAppAuthConfig

connector = HubspotConnector(
    auth_config=HubspotPrivateAppAuthConfig(
        private_app_token="<Access token from a HubSpot Private App>"
    )
)

mcp = FastMCP("Hubspot Agent")

@mcp.tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.19
