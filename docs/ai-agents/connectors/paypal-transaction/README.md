# Paypal-Transaction

The Paypal-Transaction agent connector is a Python package that equips AI agents to interact with Paypal-Transaction through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the PayPal Transaction Search API. Provides access to transaction history, account balances, payments, disputes, catalog products, and invoices for a PayPal account. Uses OAuth2 client credentials for authentication.


## Example prompts

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

## Unsupported prompts

The Paypal-Transaction connector isn't currently able to handle prompts like these.

- Create a new payment
- Refund a transaction
- Delete a dispute
- Update product details

## Entities and actions

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


## Paypal-Transaction API docs

See the official [Paypal-Transaction API reference](https://developer.paypal.com/docs/api/transaction-search/v1/).

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

The `connect()` factory returns a fully typed `PaypalTransactionConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector

connector = connect("paypal-transaction", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector

connector = connect("paypal-transaction", workspace_name="<your_workspace_name>")

@tool
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector

connector = connect("paypal-transaction", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@PaypalTransactionConnector.tool_utils(framework="openai_agents")
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Paypal-Transaction Assistant", tools=[paypal_transaction_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector

connector = connect("paypal-transaction", workspace_name="<your_workspace_name>")

mcp = FastMCP("Paypal-Transaction Agent")

@mcp.tool
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PaypalTransactionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PaypalTransactionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PaypalTransactionConnector(
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
@PaypalTransactionConnector.tool_utils(framework="openai_agents")
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Paypal-Transaction Assistant", tools=[paypal_transaction_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.paypal_transaction import PaypalTransactionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = PaypalTransactionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Paypal-Transaction Agent")

@mcp.tool
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
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

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
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

@tool
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
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

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@PaypalTransactionConnector.tool_utils(framework="openai_agents")
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Paypal-Transaction Assistant", tools=[paypal_transaction_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
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

mcp = FastMCP("Paypal-Transaction Agent")

@mcp.tool
@PaypalTransactionConnector.tool_utils
async def paypal_transaction_execute(entity: str, action: str, params: dict | None = None):
    """Execute Paypal-Transaction connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.3
