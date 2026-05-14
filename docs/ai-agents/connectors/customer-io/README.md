# Customer-Io

The Customer-Io agent connector is a Python package that equips AI agents to interact with Customer-Io through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Customer.io App API, providing read access to campaigns, newsletters, segments, messages, activities, sender identities, snippets, collections, reporting webhooks, exports, and transactional message templates. Customer.io is a messaging platform that lets you send automated emails, push notifications, SMS, and in-app messages based on customer behavior. This connector retrieves data from the App API (not the Track API) and requires a Bearer-type App API key generated in your Customer.io workspace settings.


## Example prompts

The Customer-Io connector is optimized to handle prompts like these.

- List all campaigns in Customer.io
- Show me all newsletters
- What segments are defined in my workspace?
- Get the details of campaign 42
- List all sender identities
- Show me all reporting webhooks
- What snippets do we have?
- List all collections
- Show recent activities
- Create a snippet called 'footer' with content '\<p\>Thanks!\</p\>'
- Update the snippet 'header' to say 'Welcome back!'
- Create a new collection called 'products'
- Create a reporting webhook for email events
- Create a manual segment called 'VIP Customers'
- Export all customers matching a segment
- Send a transactional email to user@example.com
- Send an SMS notification to +15551234567
- Send a push notification to user 123
- Trigger broadcast campaign 42
- List all transactional message templates
- Get the details of transactional message 5
- Show the content variants of transactional template 3
- Update the subject of transactional content 139 in template 3
- Which campaigns are currently active?
- Find newsletters sent in the last month
- What are the most recent email deliveries?
- Which exports have completed?

## Unsupported prompts

The Customer-Io connector isn't currently able to handle prompts like these.

- Create a new campaign
- Delete a segment
- Delete a snippet
- Delete a collection
- Delete a reporting webhook
- Delete a newsletter
- Send a newsletter via API
- Schedule a newsletter via API

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Campaign Actions | [List](./REFERENCE.md#campaign-actions-list), [Get](./REFERENCE.md#campaign-actions-get), [Context Store Search](./REFERENCE.md#campaign-actions-context-store-search) |
| Newsletters | [List](./REFERENCE.md#newsletters-list), [Get](./REFERENCE.md#newsletters-get), [Context Store Search](./REFERENCE.md#newsletters-context-store-search) |
| Segments | [List](./REFERENCE.md#segments-list), [Create](./REFERENCE.md#segments-create), [Get](./REFERENCE.md#segments-get) |
| Messages | [List](./REFERENCE.md#messages-list), [Get](./REFERENCE.md#messages-get) |
| Activities | [List](./REFERENCE.md#activities-list) |
| Sender Identities | [List](./REFERENCE.md#sender-identities-list), [Get](./REFERENCE.md#sender-identities-get) |
| Snippets | [List](./REFERENCE.md#snippets-list), [Create](./REFERENCE.md#snippets-create), [Update](./REFERENCE.md#snippets-update) |
| Collections | [List](./REFERENCE.md#collections-list), [Create](./REFERENCE.md#collections-create), [Get](./REFERENCE.md#collections-get), [Update](./REFERENCE.md#collections-update) |
| Reporting Webhooks | [List](./REFERENCE.md#reporting-webhooks-list), [Create](./REFERENCE.md#reporting-webhooks-create), [Get](./REFERENCE.md#reporting-webhooks-get), [Update](./REFERENCE.md#reporting-webhooks-update) |
| Exports | [List](./REFERENCE.md#exports-list), [Create](./REFERENCE.md#exports-create), [Get](./REFERENCE.md#exports-get) |
| Transactional Messages | [List](./REFERENCE.md#transactional-messages-list), [Get](./REFERENCE.md#transactional-messages-get) |
| Transactional Message Contents | [List](./REFERENCE.md#transactional-message-contents-list), [Update](./REFERENCE.md#transactional-message-contents-update) |
| Transactional Email | [Create](./REFERENCE.md#transactional-email-create) |
| Transactional Sms | [Create](./REFERENCE.md#transactional-sms-create) |
| Transactional Push | [Create](./REFERENCE.md#transactional-push-create) |
| Transactional Inbox Message | [Create](./REFERENCE.md#transactional-inbox-message-create) |
| Broadcast Trigger | [Create](./REFERENCE.md#broadcast-trigger-create) |


## Customer-Io API docs

See the official [Customer-Io API reference](https://customer.io/docs/api/app/).

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

The `connect()` factory returns a fully typed `CustomerIoConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector

connector = connect("customer-io", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector

connector = connect("customer-io", workspace_name="<your_workspace_name>")

@tool
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector

connector = connect("customer-io", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@CustomerIoConnector.tool_utils(framework="openai_agents")
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Customer-Io Assistant", tools=[customer_io_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector

connector = connect("customer-io", workspace_name="<your_workspace_name>")

mcp = FastMCP("Customer-Io Agent")

@mcp.tool
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = CustomerIoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = CustomerIoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = CustomerIoConnector(
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
@CustomerIoConnector.tool_utils(framework="openai_agents")
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Customer-Io Assistant", tools=[customer_io_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = CustomerIoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Customer-Io Agent")

@mcp.tool
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.connectors.customer_io.models import CustomerIoAuthConfig

connector = CustomerIoConnector(
    auth_config=CustomerIoAuthConfig(
        app_api_key="<Your Customer.io App API key. Generate one in your workspace settings at Settings > API Credentials > App API Key.
>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.connectors.customer_io.models import CustomerIoAuthConfig

connector = CustomerIoConnector(
    auth_config=CustomerIoAuthConfig(
        app_api_key="<Your Customer.io App API key. Generate one in your workspace settings at Settings > API Credentials > App API Key.
>"
    )
)

@tool
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.connectors.customer_io.models import CustomerIoAuthConfig

connector = CustomerIoConnector(
    auth_config=CustomerIoAuthConfig(
        app_api_key="<Your Customer.io App API key. Generate one in your workspace settings at Settings > API Credentials > App API Key.
>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@CustomerIoConnector.tool_utils(framework="openai_agents")
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Customer-Io Assistant", tools=[customer_io_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.customer_io import CustomerIoConnector
from airbyte_agent_sdk.connectors.customer_io.models import CustomerIoAuthConfig

connector = CustomerIoConnector(
    auth_config=CustomerIoAuthConfig(
        app_api_key="<Your Customer.io App API key. Generate one in your workspace settings at Settings > API Credentials > App API Key.
>"
    )
)

mcp = FastMCP("Customer-Io Agent")

@mcp.tool
@CustomerIoConnector.tool_utils
async def customer_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Customer-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.0
