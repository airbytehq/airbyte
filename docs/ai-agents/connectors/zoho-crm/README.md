# Zoho-Crm

The Zoho-Crm agent connector is a Python package that equips AI agents to interact with Zoho-Crm through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zoho CRM API, providing access to CRM modules including leads, contacts, accounts, deals, campaigns, tasks, events, calls, products, quotes, and invoices. Supports OAuth 2.0 authentication with regional data center support (US, EU, AU, IN, CN, JP). Supports read operations (list and get) for all entities, and write operations (create and update) for leads, contacts, accounts, deals, and tasks.


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
- Create a new lead named John Smith at Acme Corp
- Update the status of lead to Contacted
- Create a new contact with email jane@example.com
- Create a new account called Global Industries
- Create a deal called Enterprise License worth $50,000
- Update the deal stage to Closed Won
- Create a task to follow up with the client
- Update the task priority to High
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
| Leads | [List](./REFERENCE.md#leads-list), [Create](./REFERENCE.md#leads-create), [Get](./REFERENCE.md#leads-get), [Update](./REFERENCE.md#leads-update), [Context Store Search](./REFERENCE.md#leads-context-store-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Create](./REFERENCE.md#accounts-create), [Get](./REFERENCE.md#accounts-get), [Update](./REFERENCE.md#accounts-update), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Create](./REFERENCE.md#deals-create), [Get](./REFERENCE.md#deals-get), [Update](./REFERENCE.md#deals-update), [Context Store Search](./REFERENCE.md#deals-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Create](./REFERENCE.md#tasks-create), [Get](./REFERENCE.md#tasks-get), [Update](./REFERENCE.md#tasks-update), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Context Store Search](./REFERENCE.md#events-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get), [Context Store Search](./REFERENCE.md#products-context-store-search) |
| Quotes | [List](./REFERENCE.md#quotes-list), [Get](./REFERENCE.md#quotes-get), [Context Store Search](./REFERENCE.md#quotes-context-store-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Context Store Search](./REFERENCE.md#invoices-context-store-search) |


## Zoho-Crm API docs

See the official [Zoho-Crm API reference](https://www.zoho.com/crm/developer/docs/api/v2/).

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

The `connect()` factory returns a fully typed `ZohoCrmConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


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
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZohoCrmConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
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
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZohoCrmConnector(
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

@mcp.tool
@ZohoCrmConnector.tool_utils
async def zoho_crm_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zoho-Crm connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

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
    )
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
    )
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
    )
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
    )
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

## Version information

**Connector version:** 1.0.3
