# Zendesk-Support

The Zendesk-Support agent connector is a Python package that equips AI agents to interact with Zendesk-Support through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Zendesk Support is a customer service platform that helps businesses manage support
tickets, customer interactions, and help center content. This connector provides
access to tickets, users, organizations, groups, comments, attachments, automations,
triggers, macros, views, satisfaction ratings, SLA policies, and help center articles
for customer support analytics and service performance insights.


## Example prompts

The Zendesk-Support connector is optimized to handle prompts like these.

- Show me the tickets assigned to me last week
- List all unresolved tickets
- Show me the details of recent tickets
- Create a new ticket with subject 'Login issue' and priority high
- Update ticket 12345 to status solved
- Add a comment to ticket 12345 saying 'This has been resolved'
- Set the priority of ticket 12345 to urgent and assign it to agent 98765
- Create a new end-user named 'Jane Doe' with email jane@example.com
- Update user 54321 with notes 'VIP customer'
- What are the top 5 support issues our organization has faced this month?
- Analyze the satisfaction ratings for our support team in the last 30 days
- Compare ticket resolution times across different support groups
- Identify the most common ticket fields used in our support workflow
- Summarize the performance of our SLA policies this quarter

## Unsupported prompts

The Zendesk-Support connector isn't currently able to handle prompts like these.

- Delete these old support tickets
- Merge two tickets together
- Export all tickets to a CSV file

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Tickets | [List](./REFERENCE.md#tickets-list), [Create](./REFERENCE.md#tickets-create), [Get](./REFERENCE.md#tickets-get), [Update](./REFERENCE.md#tickets-update), [Context Store Search](./REFERENCE.md#tickets-context-store-search) |
| Ticket Comments | [Create](./REFERENCE.md#ticket-comments-create), [List](./REFERENCE.md#ticket-comments-list), [Context Store Search](./REFERENCE.md#ticket-comments-context-store-search) |
| Ticket Bulk Updates | [Create](./REFERENCE.md#ticket-bulk-updates-create) |
| Deleted Tickets | [List](./REFERENCE.md#deleted-tickets-list), [Context Store Search](./REFERENCE.md#deleted-tickets-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Create](./REFERENCE.md#users-create), [Get](./REFERENCE.md#users-get), [Update](./REFERENCE.md#users-update), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Organizations | [List](./REFERENCE.md#organizations-list), [Get](./REFERENCE.md#organizations-get), [Context Store Search](./REFERENCE.md#organizations-context-store-search) |
| Groups | [List](./REFERENCE.md#groups-list), [Get](./REFERENCE.md#groups-get), [Context Store Search](./REFERENCE.md#groups-context-store-search) |
| Attachments | [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Ticket Audits | [List](./REFERENCE.md#ticket-audits-list), [List](./REFERENCE.md#ticket-audits-list), [Context Store Search](./REFERENCE.md#ticket-audits-context-store-search) |
| Ticket Metrics | [List](./REFERENCE.md#ticket-metrics-list), [Context Store Search](./REFERENCE.md#ticket-metrics-context-store-search) |
| Ticket Fields | [List](./REFERENCE.md#ticket-fields-list), [Get](./REFERENCE.md#ticket-fields-get), [Context Store Search](./REFERENCE.md#ticket-fields-context-store-search) |
| Brands | [List](./REFERENCE.md#brands-list), [Get](./REFERENCE.md#brands-get), [Context Store Search](./REFERENCE.md#brands-context-store-search) |
| Views | [List](./REFERENCE.md#views-list), [Get](./REFERENCE.md#views-get) |
| Macros | [Get](./REFERENCE.md#macros-get), [List](./REFERENCE.md#macros-list) |
| Triggers | [List](./REFERENCE.md#triggers-list), [Get](./REFERENCE.md#triggers-get) |
| Automations | [List](./REFERENCE.md#automations-list), [Get](./REFERENCE.md#automations-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Context Store Search](./REFERENCE.md#tags-context-store-search) |
| Satisfaction Ratings | [List](./REFERENCE.md#satisfaction-ratings-list), [Get](./REFERENCE.md#satisfaction-ratings-get), [Context Store Search](./REFERENCE.md#satisfaction-ratings-context-store-search) |
| Group Memberships | [List](./REFERENCE.md#group-memberships-list) |
| Organization Memberships | [List](./REFERENCE.md#organization-memberships-list) |
| Sla Policies | [List](./REFERENCE.md#sla-policies-list), [Get](./REFERENCE.md#sla-policies-get) |
| Ticket Forms | [List](./REFERENCE.md#ticket-forms-list), [Get](./REFERENCE.md#ticket-forms-get), [Context Store Search](./REFERENCE.md#ticket-forms-context-store-search) |
| Articles | [List](./REFERENCE.md#articles-list), [Get](./REFERENCE.md#articles-get) |
| Article Attachments | [List](./REFERENCE.md#article-attachments-list), [Get](./REFERENCE.md#article-attachments-get), [Download](./REFERENCE.md#article-attachments-download) |


## Zendesk-Support API docs

See the official [Zendesk-Support API reference](https://developer.zendesk.com/api-reference/ticketing/introduction/).

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

The `connect()` factory returns a fully typed `ZendeskSupportConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector

connector = connect("zendesk-support", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector

connector = connect("zendesk-support", workspace_name="<your_workspace_name>")

@tool
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector

connector = connect("zendesk-support", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskSupportConnector.tool_utils(framework="openai_agents")
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Support Assistant", tools=[zendesk_support_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector

connector = connect("zendesk-support", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Support Agent")

@mcp.tool
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskSupportConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskSupportConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskSupportConnector(
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
@ZendeskSupportConnector.tool_utils(framework="openai_agents")
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Support Assistant", tools=[zendesk_support_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskSupportConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Zendesk-Support Agent")

@mcp.tool
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.connectors.zendesk_support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.connectors.zendesk_support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

@tool
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.connectors.zendesk_support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskSupportConnector.tool_utils(framework="openai_agents")
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Support Assistant", tools=[zendesk_support_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_support import ZendeskSupportConnector
from airbyte_agent_sdk.connectors.zendesk_support.models import ZendeskSupportApiTokenAuthConfig

connector = ZendeskSupportConnector(
    auth_config=ZendeskSupportApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

mcp = FastMCP("Zendesk-Support Agent")

@mcp.tool
@ZendeskSupportConnector.tool_utils
async def zendesk_support_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Support connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.20
