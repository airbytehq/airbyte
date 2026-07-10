# Amazon-Seller-Partner authentication

This page documents the authentication and configuration options for the Amazon-Seller-Partner agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
Use the CLI for hosted OAuth connector creation when possible. It opens the hosted setup flow and avoids passing connector secrets through the command line:

```bash
airbyte-agent login
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-seller-partner"
}'
```

For API-first use cases, create a connector with OAuth credentials directly.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `lwa_app_id` | `str` | Yes | Your Login with Amazon Client ID. |
| `lwa_client_secret` | `str` | Yes | Your Login with Amazon Client Secret. |
| `refresh_token` | `str` | Yes | The Refresh Token obtained via the OAuth authorization flow. |
| `access_token` | `str` | No | Access token (optional if refresh_token is provided). |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `replication_start_date` | `str (date-time)` | Yes | UTC date and time in ISO 8601 format (e.g. 2024-01-01T00:00:00Z). Any data before this date will not be replicated. This sets the earliest date for order creation and financial event queries. For most sellers, a start date of 1-2 years ago is a good default. Must include the time component and Z timezone suffix. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Amazon-Seller-Partner",
    "name": "My Amazon-Seller-Partner Connector",
    "credentials": {
      "lwa_app_id": "<Your Login with Amazon Client ID.>",
      "lwa_client_secret": "<Your Login with Amazon Client Secret.>",
      "refresh_token": "<The Refresh Token obtained via the OAuth authorization flow.>",
      "access_token": "<Access token (optional if refresh_token is provided).>"
    },
    "replication_config": {
      "replication_start_date": "<UTC date and time in ISO 8601 format (e.g. 2024-01-01T00:00:00Z). Any data before this date will not be replicated. This sets the earliest date for order creation and financial event queries. For most sellers, a start date of 1-2 years ago is a good default. Must include the time component and Z timezone suffix.>"
    }
  }'
```




### Token
This authentication method isn't available for this connector.

### Execution

After creating the connector, execute operations using the CLI, Python SDK, or API.
If your Airbyte client can access multiple organizations, set the default organization with `airbyte-agent organizations use`, include `organization_id` in `AirbyteAuthConfig`, or include `X-Organization-Id` in raw API calls.

**CLI**

Authenticate with Airbyte:

```bash
airbyte-agent login
```

Create the connector. The CLI opens the hosted setup flow:

```bash
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-seller-partner"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-seller-partner"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "amazon-seller-partner",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `AmazonSellerPartnerConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

@tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AmazonSellerPartnerConnector.tool_utils(framework="openai_agents")
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=[amazon_seller_partner_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector

connector = connect("amazon-seller-partner", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amazon-Seller-Partner Agent")

@mcp.tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
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
@AmazonSellerPartnerConnector.tool_utils(framework="openai_agents")
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amazon-Seller-Partner Assistant", tools=[amazon_seller_partner_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Amazon-Seller-Partner Agent")

@mcp.tool
@AmazonSellerPartnerConnector.tool_utils
async def amazon_seller_partner_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amazon-Seller-Partner connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**API**

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <YOUR_BEARER_TOKEN>' \
  -H 'X-Organization-Id: <YOUR_ORGANIZATION_ID>' \
  -H 'Content-Type: application/json' \
  -d '{"entity": "<entity>", "action": "<action>", "params": {}}'
```


## Open source mode

In open source mode, provide API credentials directly to the connector.

### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `lwa_app_id` | `str` | Yes | Your Login with Amazon Client ID. |
| `lwa_client_secret` | `str` | Yes | Your Login with Amazon Client Secret. |
| `refresh_token` | `str` | Yes | The Refresh Token obtained via the OAuth authorization flow. |
| `access_token` | `str` | No | Access token (optional if refresh_token is provided). |

Example request:

```python
from airbyte_agent_sdk.connectors.amazon_seller_partner import AmazonSellerPartnerConnector
from airbyte_agent_sdk.connectors.amazon_seller_partner.models import AmazonSellerPartnerAuthConfig

connector = AmazonSellerPartnerConnector(
    auth_config=AmazonSellerPartnerAuthConfig(
        lwa_app_id="<Your Login with Amazon Client ID.>",
        lwa_client_secret="<Your Login with Amazon Client Secret.>",
        refresh_token="<The Refresh Token obtained via the OAuth authorization flow.>",
        access_token="<Access token (optional if refresh_token is provided).>"
    )
)
```

### Token
This authentication method isn't available for this connector.

## Configuration

The Amazon-Seller-Partner connector also needs these configuration values to construct the base API URL.

- **Hosted CLI**: `airbyte-agent connectors create` doesn't currently accept these configuration fields directly. For hosted connectors that need these values, create the connector with the hosted API `replication_config`, then use the CLI for describe and execute operations after creation.
- **Hosted API**: pass these values in the connector creation `replication_config`.
- **Open source mode**: provide these values with your local connector setup so the connector can build the correct API base URL.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `region` | `string` | Yes | na | The seller's marketplace region. This determines both the API endpoint and the marketplace ID used for queries. Select the country code where you sell:
North America (NA endpoint): US (Amazon.com), CA (Amazon.ca), MX (Amazon.com.mx), BR (Amazon.com.br)
Europe (EU endpoint): DE (Amazon.de), FR (Amazon.fr), IT (Amazon.it), ES (Amazon.es), UK/GB (Amazon.co.uk), NL (Amazon.nl), SE (Amazon.se), PL (Amazon.pl), BE (Amazon.com.be), TR (Amazon.com.tr), EG (Amazon.eg), SA (Amazon.sa), AE (Amazon.ae), IN (Amazon.in), ZA (Amazon.co.za)
Far East (FE endpoint): JP (Amazon.co.jp), AU (Amazon.com.au), SG (Amazon.sg)
The region is automatically mapped to the correct API endpoint (na/eu/fe) and marketplace ID. You only need to specify your country code. |
