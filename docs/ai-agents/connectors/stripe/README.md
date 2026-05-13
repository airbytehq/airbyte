# Stripe

The Stripe agent connector is a Python package that equips AI agents to interact with Stripe through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Stripe is a payment processing platform that enables businesses to accept payments,
manage subscriptions, and handle financial transactions. This connector provides
access to customers for payment analytics and customer management.


## Example prompts

The Stripe connector is optimized to handle prompts like these.

- List customers created in the last 7 days
- Show me details for a recent customer
- List recent charges
- Show me details for a recent charge
- List recent invoices
- List active subscriptions
- Create a payment intent for $50.00 USD
- Create a new invoice for customer cus_123
- Create a subscription for customer cus_123 with price price_456
- Create a price of $29.99/month for product prod_789
- Create a checkout session for price price_456
- Cancel payment intent pi_123
- Finalize invoice inv_123
- Show me my top 10 customers by total revenue this month
- List all customers who have spent over $5,000 in the last quarter
- Analyze payment trends for my Stripe customers
- Identify which customers have the most consistent subscription payments
- Give me insights into my customer retention rates
- Summarize the payment history for \{customer\}
- Compare customer spending patterns from last month to this month
- Show me details about my highest-value Stripe customers
- What are the key financial insights from my customer base?
- Break down my customers by their average transaction value

## Unsupported prompts

The Stripe connector isn't currently able to handle prompts like these.

- Send a payment reminder to \{customer\}

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Create](./REFERENCE.md#customers-create), [Get](./REFERENCE.md#customers-get), [Update](./REFERENCE.md#customers-update), [Delete](./REFERENCE.md#customers-delete), [API Search](./REFERENCE.md#customers-api_search), [Context Store Search](./REFERENCE.md#customers-context-store-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Create](./REFERENCE.md#invoices-create), [Get](./REFERENCE.md#invoices-get), [API Search](./REFERENCE.md#invoices-api_search), [Context Store Search](./REFERENCE.md#invoices-context-store-search) |
| Invoice Finalizations | [Create](./REFERENCE.md#invoice-finalizations-create) |
| Invoice Sends | [Create](./REFERENCE.md#invoice-sends-create) |
| Charges | [List](./REFERENCE.md#charges-list), [Get](./REFERENCE.md#charges-get), [API Search](./REFERENCE.md#charges-api_search), [Context Store Search](./REFERENCE.md#charges-context-store-search) |
| Subscriptions | [List](./REFERENCE.md#subscriptions-list), [Create](./REFERENCE.md#subscriptions-create), [Get](./REFERENCE.md#subscriptions-get), [Update](./REFERENCE.md#subscriptions-update), [Delete](./REFERENCE.md#subscriptions-delete), [API Search](./REFERENCE.md#subscriptions-api_search), [Context Store Search](./REFERENCE.md#subscriptions-context-store-search) |
| Refunds | [List](./REFERENCE.md#refunds-list), [Create](./REFERENCE.md#refunds-create), [Get](./REFERENCE.md#refunds-get), [Context Store Search](./REFERENCE.md#refunds-context-store-search) |
| Products | [List](./REFERENCE.md#products-list), [Create](./REFERENCE.md#products-create), [Get](./REFERENCE.md#products-get), [Update](./REFERENCE.md#products-update), [Delete](./REFERENCE.md#products-delete), [API Search](./REFERENCE.md#products-api_search) |
| Balance | [Get](./REFERENCE.md#balance-get) |
| Balance Transactions | [List](./REFERENCE.md#balance-transactions-list), [Get](./REFERENCE.md#balance-transactions-get) |
| Payment Intents | [List](./REFERENCE.md#payment-intents-list), [Create](./REFERENCE.md#payment-intents-create), [Get](./REFERENCE.md#payment-intents-get), [Update](./REFERENCE.md#payment-intents-update), [API Search](./REFERENCE.md#payment-intents-api_search) |
| Payment Intent Confirmations | [Create](./REFERENCE.md#payment-intent-confirmations-create) |
| Payment Intent Cancellations | [Create](./REFERENCE.md#payment-intent-cancellations-create) |
| Prices | [Create](./REFERENCE.md#prices-create) |
| Checkout Sessions | [Create](./REFERENCE.md#checkout-sessions-create) |
| Payment Method Attachments | [Create](./REFERENCE.md#payment-method-attachments-create) |
| Disputes | [List](./REFERENCE.md#disputes-list), [Get](./REFERENCE.md#disputes-get) |
| Payouts | [List](./REFERENCE.md#payouts-list), [Get](./REFERENCE.md#payouts-get) |


## Stripe API docs

See the official [Stripe API reference](https://docs.stripe.com/api).

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

The `connect()` factory returns a fully typed `StripeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.stripe import StripeConnector

connector = connect("stripe", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.stripe import StripeConnector

connector = connect("stripe", workspace_name="<your_workspace_name>")

@tool
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.stripe import StripeConnector

connector = connect("stripe", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@StripeConnector.tool_utils(framework="openai_agents")
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Stripe Assistant", tools=[stripe_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.stripe import StripeConnector

connector = connect("stripe", workspace_name="<your_workspace_name>")

mcp = FastMCP("Stripe Agent")

@mcp.tool
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = StripeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = StripeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = StripeConnector(
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
@StripeConnector.tool_utils(framework="openai_agents")
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Stripe Assistant", tools=[stripe_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = StripeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Stripe Agent")

@mcp.tool
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.connectors.stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(
        api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.connectors.stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(
        api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    )
)

@tool
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.connectors.stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(
        api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@StripeConnector.tool_utils(framework="openai_agents")
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Stripe Assistant", tools=[stripe_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.stripe import StripeConnector
from airbyte_agent_sdk.connectors.stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(
        api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    )
)

mcp = FastMCP("Stripe Agent")

@mcp.tool
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute Stripe connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.13
