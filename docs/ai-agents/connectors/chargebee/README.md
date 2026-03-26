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
uv pip install airbyte-agent-chargebee
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_chargebee import ChargebeeConnector
from airbyte_agent_chargebee.models import ChargebeeAuthConfig

connector = ChargebeeConnector(
    auth_config=ChargebeeAuthConfig(
        api_key="<Your Chargebee API key (used as the HTTP Basic username)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_chargebee import ChargebeeConnector, AirbyteAuthConfig

connector = ChargebeeConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ChargebeeConnector.tool_utils
async def chargebee_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customer | [List](./REFERENCE.md#customer-list), [Get](./REFERENCE.md#customer-get), [Search](./REFERENCE.md#customer-search) |
| Subscription | [List](./REFERENCE.md#subscription-list), [Get](./REFERENCE.md#subscription-get), [Search](./REFERENCE.md#subscription-search) |
| Invoice | [List](./REFERENCE.md#invoice-list), [Get](./REFERENCE.md#invoice-get), [Search](./REFERENCE.md#invoice-search) |
| Credit Note | [List](./REFERENCE.md#credit-note-list), [Get](./REFERENCE.md#credit-note-get), [Search](./REFERENCE.md#credit-note-search) |
| Coupon | [List](./REFERENCE.md#coupon-list), [Get](./REFERENCE.md#coupon-get), [Search](./REFERENCE.md#coupon-search) |
| Transaction | [List](./REFERENCE.md#transaction-list), [Get](./REFERENCE.md#transaction-get), [Search](./REFERENCE.md#transaction-search) |
| Event | [List](./REFERENCE.md#event-list), [Get](./REFERENCE.md#event-get), [Search](./REFERENCE.md#event-search) |
| Order | [List](./REFERENCE.md#order-list), [Get](./REFERENCE.md#order-get), [Search](./REFERENCE.md#order-search) |
| Item | [List](./REFERENCE.md#item-list), [Get](./REFERENCE.md#item-get), [Search](./REFERENCE.md#item-search) |
| Item Price | [List](./REFERENCE.md#item-price-list), [Get](./REFERENCE.md#item-price-get), [Search](./REFERENCE.md#item-price-search) |
| Payment Source | [List](./REFERENCE.md#payment-source-list), [Get](./REFERENCE.md#payment-source-get), [Search](./REFERENCE.md#payment-source-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Chargebee API docs

See the official [Chargebee API reference](https://apidocs.chargebee.com/docs/api).

## Version information

- **Package version:** 0.1.8
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** 75f388847745be753ab20224c66697e1d4a84347
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/chargebee/CHANGELOG.md)