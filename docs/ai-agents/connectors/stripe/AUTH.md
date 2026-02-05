# Stripe authentication and configuration

This page documents the authentication and configuration options for the Stripe agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth
This authentication method isn't available for this connector.

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Stripe API Key (starts with sk_test_ or sk_live_) |

Example request:

```python
from airbyte_agent_stripe import StripeConnector
from airbyte_agent_stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(
        api_key="<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
This authentication method isn't available for this connector.

#### Bring your own OAuth flow
This authentication method isn't available for this connector.

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Stripe API Key (starts with sk_test_ or sk_live_) |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `account_id` | `str` | Yes | Your Stripe account ID (starts with 'acct_', find yours at https://dashboard.stripe.com/settings/account) |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "<EXTERNAL_USER_ID>",
    "connector_type": "Stripe",
    "name": "My Stripe Connector",
    "credentials": {
      "api_key": "<Your Stripe API Key (starts with sk_test_ or sk_live_)>"
    },
    "replication_config": {
      "account_id": "<Your Stripe account ID (starts with 'acct_', find yours at https://dashboard.stripe.com/settings/account)>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.

**Python SDK**

```python
from airbyte_agent_stripe import StripeConnector, AirbyteAuthConfig

connector = StripeConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@StripeConnector.tool_utils
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


