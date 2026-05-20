# Zendesk-Talk

The Zendesk-Talk agent connector is a Python package that equips AI agents to interact with Zendesk-Talk through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zendesk Talk (Voice) API. Provides access to phone numbers,
addresses, greetings, IVR configurations, call data, and agent/account statistics
for Zendesk Talk voice support channels.


## Example prompts

The Zendesk-Talk connector is optimized to handle prompts like these.

- List all phone numbers in our Zendesk Talk account
- Show all addresses on file
- List all IVR configurations
- Show all greetings
- List greeting categories
- Show agent activity statistics
- Show the account overview stats
- Show current queue activity
- Which phone numbers have SMS enabled?
- Find agents who have missed the most calls today
- What is the average call duration across all calls?
- Which phone numbers are toll-free?

## Unsupported prompts

The Zendesk-Talk connector isn't currently able to handle prompts like these.

- Create a new phone number
- Delete an IVR configuration
- Update a greeting
- Make an outbound call

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Phone Numbers | [List](./REFERENCE.md#phone-numbers-list), [Get](./REFERENCE.md#phone-numbers-get), [Context Store Search](./REFERENCE.md#phone-numbers-context-store-search) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Context Store Search](./REFERENCE.md#addresses-context-store-search) |
| Greetings | [List](./REFERENCE.md#greetings-list), [Get](./REFERENCE.md#greetings-get), [Context Store Search](./REFERENCE.md#greetings-context-store-search) |
| Greeting Categories | [List](./REFERENCE.md#greeting-categories-list), [Get](./REFERENCE.md#greeting-categories-get), [Context Store Search](./REFERENCE.md#greeting-categories-context-store-search) |
| Ivrs | [List](./REFERENCE.md#ivrs-list), [Get](./REFERENCE.md#ivrs-get), [Context Store Search](./REFERENCE.md#ivrs-context-store-search) |
| Agents Activity | [List](./REFERENCE.md#agents-activity-list), [Context Store Search](./REFERENCE.md#agents-activity-context-store-search) |
| Agents Overview | [List](./REFERENCE.md#agents-overview-list), [Context Store Search](./REFERENCE.md#agents-overview-context-store-search) |
| Account Overview | [List](./REFERENCE.md#account-overview-list), [Context Store Search](./REFERENCE.md#account-overview-context-store-search) |
| Current Queue Activity | [List](./REFERENCE.md#current-queue-activity-list), [Context Store Search](./REFERENCE.md#current-queue-activity-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Call Legs | [List](./REFERENCE.md#call-legs-list), [Context Store Search](./REFERENCE.md#call-legs-context-store-search) |


## Zendesk-Talk API docs

See the official [Zendesk-Talk API reference](https://developer.zendesk.com/api-reference/voice/talk-api/introduction/).

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

The `connect()` factory returns a fully typed `ZendeskTalkConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

@tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskTalkConnector.tool_utils(framework="openai_agents")
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Talk Assistant", tools=[zendesk_talk_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector

connector = connect("zendesk-talk", workspace_name="<your_workspace_name>")

mcp = FastMCP("Zendesk-Talk Agent")

@mcp.tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
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
@ZendeskTalkConnector.tool_utils(framework="openai_agents")
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Talk Assistant", tools=[zendesk_talk_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Zendesk-Talk Agent")

@mcp.tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

@tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ZendeskTalkConnector.tool_utils(framework="openai_agents")
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Zendesk-Talk Assistant", tools=[zendesk_talk_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

mcp = FastMCP("Zendesk-Talk Agent")

@mcp.tool
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    """Execute Zendesk-Talk connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.3
