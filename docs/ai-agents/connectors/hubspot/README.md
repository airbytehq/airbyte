# Hubspot

The Hubspot agent connector is a Python package that equips AI agents to interact with Hubspot through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

HubSpot is a CRM platform that provides tools for marketing, sales, customer service,
and content management. This connector provides access to contacts, companies, deals,
tickets, notes, calls, emails, meetings, tasks, and custom objects for customer relationship management and sales analytics.


## Example prompts

The Hubspot connector is optimized to handle prompts like these.

- List recent deals
- List recent tickets
- List companies in my CRM
- List contacts in my CRM
- Create a new contact with email john@example.com and name John Smith
- Create a new deal called 'Enterprise License' with amount 50000
- Update the deal stage to 'closedwon' for a specific deal
- Create a new company called 'Acme Corp' with domain acme.com
- Create a support ticket with subject 'Login issue' and priority HIGH
- Update the contact email for a specific contact
- Add a note to contact 12345 saying 'Discussed pricing options'
- List recent notes in my CRM
- Get the details of a specific note
- Delete a note from HubSpot
- Log a call with contact 12345 about pricing discussion
- List recent calls in my CRM
- Create an email record for outreach to a contact
- List recent emails in my CRM
- Schedule a meeting with a contact for next Tuesday
- List recent meetings in my CRM
- Create a follow-up task for a deal
- List tasks in my CRM
- Show me all deals from Acme Corp this quarter
- What are the top 5 most valuable deals in my pipeline right now?
- Search for contacts in the marketing department at HubSpot
- Give me an overview of my sales team's deals in the last 30 days
- Identify the most active companies in our CRM this month
- Compare the number of deals closed by different sales representatives
- Find all tickets related to a specific product issue and summarize their status

## Unsupported prompts

The Hubspot connector isn't currently able to handle prompts like these.

- Delete a contact from HubSpot
- Delete a deal record

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [API Search](./REFERENCE.md#contacts-api_search), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Create](./REFERENCE.md#companies-create), [Get](./REFERENCE.md#companies-get), [Update](./REFERENCE.md#companies-update), [API Search](./REFERENCE.md#companies-api_search), [Context Store Search](./REFERENCE.md#companies-context-store-search) |
| Deals | [List](./REFERENCE.md#deals-list), [Create](./REFERENCE.md#deals-create), [Get](./REFERENCE.md#deals-get), [Update](./REFERENCE.md#deals-update), [API Search](./REFERENCE.md#deals-api_search), [Context Store Search](./REFERENCE.md#deals-context-store-search) |
| Tickets | [List](./REFERENCE.md#tickets-list), [Create](./REFERENCE.md#tickets-create), [Get](./REFERENCE.md#tickets-get), [Update](./REFERENCE.md#tickets-update), [API Search](./REFERENCE.md#tickets-api_search), [Context Store Search](./REFERENCE.md#tickets-context-store-search) |
| Notes | [List](./REFERENCE.md#notes-list), [Create](./REFERENCE.md#notes-create), [Get](./REFERENCE.md#notes-get), [Update](./REFERENCE.md#notes-update), [Delete](./REFERENCE.md#notes-delete), [Context Store Search](./REFERENCE.md#notes-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Create](./REFERENCE.md#calls-create), [Get](./REFERENCE.md#calls-get), [Update](./REFERENCE.md#calls-update), [Delete](./REFERENCE.md#calls-delete), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Emails | [List](./REFERENCE.md#emails-list), [Create](./REFERENCE.md#emails-create), [Get](./REFERENCE.md#emails-get), [Update](./REFERENCE.md#emails-update), [Delete](./REFERENCE.md#emails-delete), [Context Store Search](./REFERENCE.md#emails-context-store-search) |
| Meetings | [List](./REFERENCE.md#meetings-list), [Create](./REFERENCE.md#meetings-create), [Get](./REFERENCE.md#meetings-get), [Update](./REFERENCE.md#meetings-update), [Delete](./REFERENCE.md#meetings-delete), [Context Store Search](./REFERENCE.md#meetings-context-store-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Create](./REFERENCE.md#tasks-create), [Get](./REFERENCE.md#tasks-get), [Update](./REFERENCE.md#tasks-update), [Delete](./REFERENCE.md#tasks-delete), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Schemas | [List](./REFERENCE.md#schemas-list), [Get](./REFERENCE.md#schemas-get) |
| Objects | [List](./REFERENCE.md#objects-list), [Get](./REFERENCE.md#objects-get) |


## Hubspot API docs

See the official [Hubspot API reference](https://developers.hubspot.com/docs/api/crm/understanding-the-crm).

## Interfaces

Use the Hubspot connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "hubspot"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "hubspot",
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

##### Open source

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

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.19