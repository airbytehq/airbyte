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

```python
from airbyte_agent_stripe import StripeConnector, StripeAuthConfig

connector = StripeConnector(
  auth_config=StripeAuthConfig(
    api_key="..."
  )
)
result = await connector.customers.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Get](./REFERENCE.md#customers-get), [Search](./REFERENCE.md#customers-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Search](./REFERENCE.md#invoices-search) |
| Charges | [List](./REFERENCE.md#charges-list), [Get](./REFERENCE.md#charges-get), [Search](./REFERENCE.md#charges-search) |
| Subscriptions | [List](./REFERENCE.md#subscriptions-list), [Get](./REFERENCE.md#subscriptions-get), [Search](./REFERENCE.md#subscriptions-search) |
| Refunds | [List](./REFERENCE.md#refunds-list), [Get](./REFERENCE.md#refunds-get) |
| Products | [List](./REFERENCE.md#products-list), [Get](./REFERENCE.md#products-get), [Search](./REFERENCE.md#products-search) |
| Balance | [Get](./REFERENCE.md#balance-get) |
| Balance Transactions | [List](./REFERENCE.md#balance-transactions-list), [Get](./REFERENCE.md#balance-transactions-get) |
| Payment Intents | [List](./REFERENCE.md#payment-intents-list), [Get](./REFERENCE.md#payment-intents-get), [Search](./REFERENCE.md#payment-intents-search) |
| Disputes | [List](./REFERENCE.md#disputes-list), [Get](./REFERENCE.md#disputes-get) |
| Payouts | [List](./REFERENCE.md#payouts-list), [Get](./REFERENCE.md#payouts-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Stripe API reference](https://docs.stripe.com/api).

## Version information

- **Package version:** 0.5.29
- **Connector version:** 0.1.3
- **Generated with Connector SDK commit SHA:** d023e05f2b7a1ddabf81fab7640c64de1e0aa6a1