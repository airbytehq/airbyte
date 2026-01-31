# Stripe agent connector

Stripe is a payment processing platform that enables businesses to accept payments,
manage subscriptions, and handle financial transactions. This connector provides
access to customers for payment analytics and customer management.


## Example questions

The Stripe connector is optimized to handle prompts like these.

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

## Unsupported questions

The Stripe connector isn't currently able to handle prompts like these.

- Create a new customer profile in Stripe
- Update the billing information for \{customer\}
- Delete a customer record
- Send a payment reminder to \{customer\}
- Schedule an automatic invoice for \{company\}

## Installation

```bash
uv pip install airbyte-agent-stripe
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_stripe import StripeConnector
from airbyte_agent_stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(
        api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_stripe import StripeConnector

connector = StripeConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Create](./REFERENCE.md#customers-create), [Get](./REFERENCE.md#customers-get), [Update](./REFERENCE.md#customers-update), [Delete](./REFERENCE.md#customers-delete), [API Search](./REFERENCE.md#customers-api_search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [API Search](./REFERENCE.md#invoices-api_search) |
| Charges | [List](./REFERENCE.md#charges-list), [Get](./REFERENCE.md#charges-get), [API Search](./REFERENCE.md#charges-api_search) |
| Subscriptions | [List](./REFERENCE.md#subscriptions-list), [Get](./REFERENCE.md#subscriptions-get), [API Search](./REFERENCE.md#subscriptions-api_search) |
| Refunds | [List](./REFERENCE.md#refunds-list), [Create](./REFERENCE.md#refunds-create), [Get](./REFERENCE.md#refunds-get) |
| Products | [List](./REFERENCE.md#products-list), [Create](./REFERENCE.md#products-create), [Get](./REFERENCE.md#products-get), [Update](./REFERENCE.md#products-update), [Delete](./REFERENCE.md#products-delete), [API Search](./REFERENCE.md#products-api_search) |
| Balance | [Get](./REFERENCE.md#balance-get) |
| Balance Transactions | [List](./REFERENCE.md#balance-transactions-list), [Get](./REFERENCE.md#balance-transactions-get) |
| Payment Intents | [List](./REFERENCE.md#payment-intents-list), [Get](./REFERENCE.md#payment-intents-get), [API Search](./REFERENCE.md#payment-intents-api_search) |
| Disputes | [List](./REFERENCE.md#disputes-list), [Get](./REFERENCE.md#disputes-get) |
| Payouts | [List](./REFERENCE.md#payouts-list), [Get](./REFERENCE.md#payouts-get) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Stripe API docs

See the official [Stripe API reference](https://docs.stripe.com/api).

## Version information

- **Package version:** 0.5.73
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/stripe/CHANGELOG.md)