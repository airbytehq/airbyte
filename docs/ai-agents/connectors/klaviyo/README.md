# Klaviyo

The Klaviyo agent connector is a Python package that equips AI agents to interact with Klaviyo through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Klaviyo is a marketing automation platform that helps businesses build customer relationships
through personalized email, SMS, and push notifications. This connector provides access to
Klaviyo's core entities including profiles, lists, campaigns, events, metrics, flows, and
email templates for marketing analytics and customer engagement insights.


## Example questions

The Klaviyo connector is optimized to handle prompts like these.

- List all profiles in my Klaviyo account
- Show me details for a recent profile
- Show me all email lists
- Show me details for a recent email list
- What campaigns have been created?
- Show me details for a recent campaign
- Show me all email campaigns
- List all events for tracking customer actions
- Show me all metrics (event types)
- Show me details for a recent metric
- What automated flows are configured?
- Show me details for a recent flow
- List all email templates
- Show me details for a recent email template

## Unsupported questions

The Klaviyo connector isn't currently able to handle prompts like these.

- Create a new profile
- Update a profile's email address
- Delete a list
- Send an email campaign
- Add a profile to a list

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
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector
from airbyte_agent_sdk.connectors.klaviyo.models import KlaviyoAuthConfig

connector = KlaviyoConnector(
    auth_config=KlaviyoAuthConfig(
        api_key="<Your Klaviyo private API key>"
    )
)

@agent.tool_plain
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector
from airbyte_agent_sdk.connectors.klaviyo.models import KlaviyoAuthConfig

connector = KlaviyoConnector(
    auth_config=KlaviyoAuthConfig(
        api_key="<Your Klaviyo private API key>"
    )
)

@tool
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Klaviyo connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector
from airbyte_agent_sdk.connectors.klaviyo.models import KlaviyoAuthConfig

connector = KlaviyoConnector(
    auth_config=KlaviyoAuthConfig(
        api_key="<Your Klaviyo private API key>"
    )
)

mcp = FastMCP("Klaviyo Agent")

@mcp.tool()
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Klaviyo connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `KlaviyoConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector

connector = connect("klaviyo", workspace_name="<your_workspace_name>")

@agent.tool_plain
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector

connector = connect("klaviyo", workspace_name="<your_workspace_name>")

@tool
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Klaviyo connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector

connector = connect("klaviyo", workspace_name="<your_workspace_name>")

mcp = FastMCP("Klaviyo Agent")

@mcp.tool()
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Klaviyo connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = KlaviyoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = KlaviyoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Klaviyo connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.klaviyo import KlaviyoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = KlaviyoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Klaviyo Agent")

@mcp.tool()
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Klaviyo connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Profiles | [List](./REFERENCE.md#profiles-list), [Get](./REFERENCE.md#profiles-get), [Context Store Search](./REFERENCE.md#profiles-context-store-search) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get), [Context Store Search](./REFERENCE.md#lists-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Events | [List](./REFERENCE.md#events-list), [Context Store Search](./REFERENCE.md#events-context-store-search) |
| Metrics | [List](./REFERENCE.md#metrics-list), [Get](./REFERENCE.md#metrics-get), [Context Store Search](./REFERENCE.md#metrics-context-store-search) |
| Flows | [List](./REFERENCE.md#flows-list), [Get](./REFERENCE.md#flows-get), [Context Store Search](./REFERENCE.md#flows-context-store-search) |
| Email Templates | [List](./REFERENCE.md#email-templates-list), [Get](./REFERENCE.md#email-templates-get), [Context Store Search](./REFERENCE.md#email-templates-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Klaviyo API docs

See the official [Klaviyo API reference](https://developers.klaviyo.com/en/reference/api_overview).

## Version information

- **Package version:** 1.0.4
- **Connector version:** 1.0.4
- **Generated with Connector SDK commit SHA:** unknown