# Pylon

The Pylon agent connector is a Python package that equips AI agents to interact with Pylon through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Pylon is a customer support platform that helps B2B companies manage customer interactions
across Slack, email, chat widgets, and other channels. This connector provides access to
issues, accounts, contacts, teams, tags, users, custom fields, ticket forms, and user roles
for customer support analytics and account intelligence insights.


## Example prompts

The Pylon connector is optimized to handle prompts like these.

- List all open issues in Pylon
- Show me all accounts in Pylon
- List all contacts in Pylon
- What teams are configured in my Pylon workspace?
- Show me all tags used in Pylon
- List all users in my Pylon account
- Show me the custom fields configured for issues
- List all ticket forms in Pylon
- What user roles are available in Pylon?
- Show me details for a specific issue
- Get details for a specific account
- Show me details for a specific contact
- Reply to the customer on an issue saying we are looking into it
- Send a message to the customer on the billing issue
- Assign an issue to a specific team member
- Change the status of an issue to waiting_on_customer
- Close an issue as resolved
- Delete a test issue
- What are the most common issue sources this month?
- Show me issues assigned to a specific team
- Which accounts have the most open issues?
- Analyze issue resolution times over the last 30 days
- List contacts associated with a specific account

## Unsupported prompts

The Pylon connector isn't currently able to handle prompts like these.

- Delete an account
- Schedule a meeting with a contact

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Issues | [List](./REFERENCE.md#issues-list), [Create](./REFERENCE.md#issues-create), [Get](./REFERENCE.md#issues-get), [Update](./REFERENCE.md#issues-update), [Delete](./REFERENCE.md#issues-delete), [Context Store Search](./REFERENCE.md#issues-context-store-search) |
| Issue Replies | [Create](./REFERENCE.md#issue-replies-create) |
| Issue Assignments | [Update](./REFERENCE.md#issue-assignments-update) |
| Issue Statuses | [Update](./REFERENCE.md#issue-statuses-update) |
| Messages | [List](./REFERENCE.md#messages-list) |
| Issue Notes | [Create](./REFERENCE.md#issue-notes-create) |
| Issue Threads | [Create](./REFERENCE.md#issue-threads-create) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Create](./REFERENCE.md#accounts-create), [Get](./REFERENCE.md#accounts-get), [Update](./REFERENCE.md#accounts-update), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Create](./REFERENCE.md#teams-create), [Get](./REFERENCE.md#teams-get), [Update](./REFERENCE.md#teams-update), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Tags | [List](./REFERENCE.md#tags-list), [Create](./REFERENCE.md#tags-create), [Get](./REFERENCE.md#tags-get), [Update](./REFERENCE.md#tags-update), [Context Store Search](./REFERENCE.md#tags-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Custom Fields | [List](./REFERENCE.md#custom-fields-list), [Get](./REFERENCE.md#custom-fields-get), [Context Store Search](./REFERENCE.md#custom-fields-context-store-search) |
| Ticket Forms | [List](./REFERENCE.md#ticket-forms-list), [Context Store Search](./REFERENCE.md#ticket-forms-context-store-search) |
| User Roles | [List](./REFERENCE.md#user-roles-list), [Context Store Search](./REFERENCE.md#user-roles-context-store-search) |
| Tasks | [Create](./REFERENCE.md#tasks-create), [Update](./REFERENCE.md#tasks-update) |
| Projects | [Create](./REFERENCE.md#projects-create), [Update](./REFERENCE.md#projects-update) |
| Milestones | [Create](./REFERENCE.md#milestones-create), [Update](./REFERENCE.md#milestones-update) |
| Articles | [Create](./REFERENCE.md#articles-create), [Update](./REFERENCE.md#articles-update) |
| Collections | [Create](./REFERENCE.md#collections-create) |
| Me | [Get](./REFERENCE.md#me-get) |


## Pylon API docs

See the official [Pylon API reference](https://docs.usepylon.com/pylon-docs/developer/api/api-reference).

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

The `connect()` factory returns a fully typed `PylonConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pylon import PylonConnector

connector = connect("pylon", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pylon import PylonConnector

connector = connect("pylon", workspace_name="<your_workspace_name>")

@tool
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pylon import PylonConnector

connector = connect("pylon", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@PylonConnector.tool_utils(framework="openai_agents")
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Pylon Assistant", tools=[pylon_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.pylon import PylonConnector

connector = connect("pylon", workspace_name="<your_workspace_name>")

mcp = FastMCP("Pylon Agent")

@mcp.tool
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PylonConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PylonConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PylonConnector(
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
@PylonConnector.tool_utils(framework="openai_agents")
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Pylon Assistant", tools=[pylon_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PylonConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Pylon Agent")

@mcp.tool
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.connectors.pylon.models import PylonAuthConfig

connector = PylonConnector(
    auth_config=PylonAuthConfig(
        api_token="<Your Pylon API token. Only admin users can create API tokens.>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.connectors.pylon.models import PylonAuthConfig

connector = PylonConnector(
    auth_config=PylonAuthConfig(
        api_token="<Your Pylon API token. Only admin users can create API tokens.>"
    )
)

@tool
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.connectors.pylon.models import PylonAuthConfig

connector = PylonConnector(
    auth_config=PylonAuthConfig(
        api_token="<Your Pylon API token. Only admin users can create API tokens.>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@PylonConnector.tool_utils(framework="openai_agents")
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Pylon Assistant", tools=[pylon_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.pylon import PylonConnector
from airbyte_agent_sdk.connectors.pylon.models import PylonAuthConfig

connector = PylonConnector(
    auth_config=PylonAuthConfig(
        api_token="<Your Pylon API token. Only admin users can create API tokens.>"
    )
)

mcp = FastMCP("Pylon Agent")

@mcp.tool
@PylonConnector.tool_utils
async def pylon_execute(entity: str, action: str, params: dict | None = None):
    """Execute Pylon connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.10
