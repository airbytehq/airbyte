# Paypal-Transaction

The Paypal-Transaction agent connector is a Python package that equips AI agents to interact with Paypal-Transaction through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the PayPal Transaction Search API. Provides access to transaction history, account balances, payments, disputes, catalog products, and invoices for a PayPal account. Uses OAuth2 client credentials for authentication.


## Example questions

The Paypal-Transaction connector is optimized to handle prompts like these.

- List all balances for my PayPal account
- Show recent transactions from the last 7 days
- List all catalog products
- Show details for a specific product
- List all disputes
- Show recent payments
- What transactions had the highest amounts last month?
- Find all declined transactions
- Show disputes grouped by status
- What is the total balance across all currencies?

## Unsupported questions

The Paypal-Transaction connector isn't currently able to handle prompts like these.

- Create a new payment
- Refund a transaction
- Delete a dispute
- Update product details

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector
from airbyte_agent_sdk.connectors.paypal_transaction.models import PaypalTransactionAuthConfig

connector = PaypalTransactionConnector(
    auth_config=PaypalTransactionAuthConfig(
        client_id="<The Client ID of your PayPal developer application.>",
        client_secret="<The Client Secret of your PayPal developer application.>",
        access_token="<OAuth2 access token obtained via client credentials grant. Use the PayPal token endpoint with your client_id and client_secret to obtain this.
>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector, AirbyteAuthConfig

connector = PaypalTransactionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Balances | [List](./REFERENCE.md#balances-list), [Context Store Search](./REFERENCE.md#balances-context-store-search) |
| Transactions | [List](./REFERENCE.md#transactions-list), [Context Store Search](./REFERENCE.md#transactions-context-store-search) |
| List Payments | [List](./REFERENCE.md#list-payments-list), [Context Store Search](./REFERENCE.md#list-payments-context-store-search) |
| List Disputes | [List](./REFERENCE.md#list-disputes-list), [Context Store Search](./REFERENCE.md#list-disputes-context-store-search) |
| List Products | [List](./REFERENCE.md#list-products-list), [Context Store Search](./REFERENCE.md#list-products-context-store-search) |
| Show Product Details | [Get](./REFERENCE.md#show-product-details-get), [Context Store Search](./REFERENCE.md#show-product-details-context-store-search) |
| Search Invoices | [List](./REFERENCE.md#search-invoices-list), [Context Store Search](./REFERENCE.md#search-invoices-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Paypal-Transaction API docs

See the official [Paypal-Transaction API reference](https://developer.paypal.com/docs/api/transaction-search/v1/).

## Version information

- **Package version:** 1.0.2
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** unknown