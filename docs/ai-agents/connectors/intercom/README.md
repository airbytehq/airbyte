# Intercom

The Intercom agent connector is a Python package that equips AI agents to interact with Intercom through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Intercom is a customer messaging platform that enables businesses to communicate with
customers through chat, email, and in-app messaging. This connector provides access
to core Intercom entities including contacts, conversations, companies, teams,
admins, tags, and segments for customer support analytics and insights. It also supports
creating and updating contacts, creating notes, creating internal articles, creating
and updating companies, and creating tags.


## Example prompts

The Intercom connector is optimized to handle prompts like these.

- List all contacts in my Intercom workspace
- List all companies in Intercom
- What teams are configured in my workspace?
- Show me all admins in my Intercom account
- List all tags used in Intercom
- Show me all customer segments
- Show me details for a recent contact
- Show me details for a recent company
- Show me details for a recent conversation
- Create a new lead contact named 'Jane Smith' with email jane@example.com
- Create an internal article titled 'Onboarding Guide' with instructions for new team members
- Create a company named 'Acme Corp' with company_id 'acme-001'
- Create a tag named 'VIP Customer'
- Update the name of contact \{id\} to 'John Updated'
- Add a note to contact \{id\} saying 'Followed up on support request'
- Show me conversations from the last week
- List conversations assigned to team \{team_id\}
- Show me open conversations

## Unsupported prompts

The Intercom connector isn't currently able to handle prompts like these.

- Send a message to a customer
- Delete a conversation
- Delete a contact
- Delete a company
- Assign a conversation to an admin

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Conversations | [List](./REFERENCE.md#conversations-list), [Get](./REFERENCE.md#conversations-get), [Context Store Search](./REFERENCE.md#conversations-context-store-search) |
| Companies | [List](./REFERENCE.md#companies-list), [Create](./REFERENCE.md#companies-create), [Get](./REFERENCE.md#companies-get), [Update](./REFERENCE.md#companies-update), [Context Store Search](./REFERENCE.md#companies-context-store-search) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get), [Context Store Search](./REFERENCE.md#teams-context-store-search) |
| Admins | [List](./REFERENCE.md#admins-list), [Get](./REFERENCE.md#admins-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Create](./REFERENCE.md#tags-create), [Get](./REFERENCE.md#tags-get) |
| Notes | [Create](./REFERENCE.md#notes-create) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get) |
| Internal Articles | [Create](./REFERENCE.md#internal-articles-create) |


## Intercom API docs

See the official [Intercom API reference](https://developers.intercom.com/docs/references/rest-api/api.intercom.io).

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

The `connect()` factory returns a fully typed `IntercomConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

@tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@IntercomConnector.tool_utils(framework="openai_agents")
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Intercom Assistant", tools=[intercom_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.intercom import IntercomConnector

connector = connect("intercom", workspace_name="<your_workspace_name>")

mcp = FastMCP("Intercom Agent")

@mcp.tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
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
@IntercomConnector.tool_utils(framework="openai_agents")
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Intercom Assistant", tools=[intercom_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IntercomConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Intercom Agent")

@mcp.tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

@tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@IntercomConnector.tool_utils(framework="openai_agents")
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Intercom Assistant", tools=[intercom_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.intercom import IntercomConnector
from airbyte_agent_sdk.connectors.intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

mcp = FastMCP("Intercom Agent")

@mcp.tool
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    """Execute Intercom connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.10
