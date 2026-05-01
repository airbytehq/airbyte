# Zendesk-Chat

The Zendesk-Chat agent connector is a Python package that equips AI agents to interact with Zendesk-Chat through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Zendesk Chat enables real-time customer support through live chat. This connector
provides access to chat transcripts, agents, departments, shortcuts, triggers,
and other chat configuration data for analytics and support insights.

## Supported Entities
- **accounts**: Account information and billing details
- **agents**: Chat agents with roles and department assignments
- **agent_timeline**: Agent activity timeline (incremental export)
- **bans**: Banned visitors (IP and visitor-based)
- **chats**: Chat transcripts with full conversation history (incremental export)
- **departments**: Chat departments for routing
- **goals**: Conversion goals for tracking
- **roles**: Agent role definitions
- **routing_settings**: Account-level routing configuration
- **shortcuts**: Canned responses for agents
- **skills**: Agent skills for skill-based routing
- **triggers**: Automated chat triggers

## Rate Limits
Zendesk Chat API uses the `Retry-After` header for rate limit backoff.
The connector handles this automatically.


## Example questions

The Zendesk-Chat connector is optimized to handle prompts like these.

- List all banned visitors
- List all departments with their settings
- Show me all chats from last week
- List all agents in the support department
- What are the most used chat shortcuts?
- Show chat volume by department
- What triggers are currently active?
- Show agent activity timeline for today

## Unsupported questions

The Zendesk-Chat connector isn't currently able to handle prompts like these.

- Start a new chat session
- Send a message to a visitor
- Create a new agent
- Update department settings
- Delete a shortcut

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    )
)

@agent.tool_plain
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    )
)

@tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.connectors.zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    )
)

mcp = FastMCP("Zendesk-Chat Agent")

@mcp.tool()
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `ZendeskChatConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

@agent.tool_plain
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

@tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector

connector = connect("zendesk-chat", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Chat Agent")

@mcp.tool()
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_chat import ZendeskChatConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskChatConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Zendesk-Chat Agent")

@mcp.tool()
@ZendeskChatConnector.tool_utils
async def zendesk_chat_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Zendesk-Chat connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [Get](./REFERENCE.md#accounts-get) |
| Agents | [List](./REFERENCE.md#agents-list), [Get](./REFERENCE.md#agents-get), [Context Store Search](./REFERENCE.md#agents-context-store-search) |
| Agent Timeline | [List](./REFERENCE.md#agent-timeline-list) |
| Bans | [List](./REFERENCE.md#bans-list), [Get](./REFERENCE.md#bans-get) |
| Chats | [List](./REFERENCE.md#chats-list), [Get](./REFERENCE.md#chats-get), [Context Store Search](./REFERENCE.md#chats-context-store-search) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get), [Context Store Search](./REFERENCE.md#departments-context-store-search) |
| Goals | [List](./REFERENCE.md#goals-list), [Get](./REFERENCE.md#goals-get) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get) |
| Routing Settings | [Get](./REFERENCE.md#routing-settings-get) |
| Shortcuts | [List](./REFERENCE.md#shortcuts-list), [Get](./REFERENCE.md#shortcuts-get), [Context Store Search](./REFERENCE.md#shortcuts-context-store-search) |
| Skills | [List](./REFERENCE.md#skills-list), [Get](./REFERENCE.md#skills-get) |
| Triggers | [List](./REFERENCE.md#triggers-list), [Context Store Search](./REFERENCE.md#triggers-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Zendesk-Chat API docs

See the official [Zendesk-Chat API reference](https://developer.zendesk.com/api-reference/live-chat/chat-api/introduction/).

## Version information

- **Package version:** 0.1.10
- **Connector version:** 0.1.10
- **Generated with Connector SDK commit SHA:** unknown