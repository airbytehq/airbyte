# Chargebee

The Chargebee agent connector is a Python package that equips AI agents to interact with Chargebee through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Chargebee billing and subscription management API. Supports reading subscriptions, customers, invoices, credit notes, coupons, transactions, events, orders, items, item prices, and payment sources. Chargebee is a recurring billing platform that helps SaaS and subscription businesses manage the full subscription lifecycle.


## Example questions

The Chargebee connector is optimized to handle prompts like these.

- List all active subscriptions
- Show me details for a specific customer
- List recent invoices
- Show me details for a specific subscription
- List all coupons
- List recent transactions
- List recent events
- Show me customers with the highest monthly recurring revenue
- Which subscriptions are set to cancel in the next 30 days?
- List all overdue invoices and their amounts
- Analyze subscription churn trends over the past quarter
- What are the most popular items by number of subscriptions?
- Show me total revenue breakdown by currency
- Identify customers with expiring payment sources
- Compare subscription plan distribution across item prices
- List all credit notes issued in the past month
- What is the average subscription lifetime for each plan?

## Unsupported questions

The Chargebee connector isn't currently able to handle prompts like these.

- Create a new subscription in Chargebee
- Update a customer's billing address
- Cancel a subscription
- Apply a coupon to a subscription
- Issue a refund for an invoice

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
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    )
)

@agent.tool_plain
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    )
)

@tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.connectors.chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    )
)

mcp = FastMCP("Chargebee Agent")

@mcp.tool()
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `ChargebeeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

@agent.tool_plain
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

@tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector

connector = connect("chargebee", workspace_name="<your_workspace_name>")

mcp = FastMCP("Chargebee Agent")

@mcp.tool()
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.chargebee import ChargebeeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Chargebee Agent")

@mcp.tool()
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Chargebee connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customer | [List](./REFERENCE.md#customer-list), [Get](./REFERENCE.md#customer-get), [Context Store Search](./REFERENCE.md#customer-context-store-search) |
| Subscription | [List](./REFERENCE.md#subscription-list), [Get](./REFERENCE.md#subscription-get), [Context Store Search](./REFERENCE.md#subscription-context-store-search) |
| Invoice | [List](./REFERENCE.md#invoice-list), [Get](./REFERENCE.md#invoice-get), [Context Store Search](./REFERENCE.md#invoice-context-store-search) |
| Credit Note | [List](./REFERENCE.md#credit-note-list), [Get](./REFERENCE.md#credit-note-get), [Context Store Search](./REFERENCE.md#credit-note-context-store-search) |
| Coupon | [List](./REFERENCE.md#coupon-list), [Get](./REFERENCE.md#coupon-get), [Context Store Search](./REFERENCE.md#coupon-context-store-search) |
| Transaction | [List](./REFERENCE.md#transaction-list), [Get](./REFERENCE.md#transaction-get), [Context Store Search](./REFERENCE.md#transaction-context-store-search) |
| Event | [List](./REFERENCE.md#event-list), [Get](./REFERENCE.md#event-get), [Context Store Search](./REFERENCE.md#event-context-store-search) |
| Order | [List](./REFERENCE.md#order-list), [Get](./REFERENCE.md#order-get), [Context Store Search](./REFERENCE.md#order-context-store-search) |
| Item | [List](./REFERENCE.md#item-list), [Get](./REFERENCE.md#item-get), [Context Store Search](./REFERENCE.md#item-context-store-search) |
| Item Price | [List](./REFERENCE.md#item-price-list), [Get](./REFERENCE.md#item-price-get), [Context Store Search](./REFERENCE.md#item-price-context-store-search) |
| Payment Source | [List](./REFERENCE.md#payment-source-list), [Get](./REFERENCE.md#payment-source-get), [Context Store Search](./REFERENCE.md#payment-source-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Chargebee API docs

See the official [Chargebee API reference](https://apidocs.chargebee.com/docs/api).

## Version information

- **Package version:** 1.0.2
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** unknown