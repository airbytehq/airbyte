# Hubspot authentication

This page documents the authentication and configuration options for the Hubspot agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | No | Your HubSpot OAuth2 Client ID |
| `client_secret` | `str` | No | Your HubSpot OAuth2 Client Secret |
| `refresh_token` | `str` | Yes | Your HubSpot OAuth2 Refresh Token |
| `access_token` | `str` | No | Your HubSpot OAuth2 Access Token (optional if refresh_token is provided) |

Example request:

```python
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.connectors.hubspot.models import HubspotOauth2AuthConfig

connector = HubspotConnector(
    auth_config=HubspotOauth2AuthConfig(
        client_id="<Your HubSpot OAuth2 Client ID>",
        client_secret="<Your HubSpot OAuth2 Client Secret>",
        refresh_token="<Your HubSpot OAuth2 Refresh Token>",
        access_token="<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `private_app_token` | `str` | Yes | Access token from a HubSpot Private App |

Example request:

```python
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.connectors.hubspot.models import HubspotPrivateAppAuthConfig

connector = HubspotConnector(
    auth_config=HubspotPrivateAppAuthConfig(
        private_app_token="<Access token from a HubSpot Private App>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

#### OAuth
Create a connector with OAuth credentials.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | No | Your HubSpot OAuth2 Client ID |
| `client_secret` | `str` | No | Your HubSpot OAuth2 Client Secret |
| `refresh_token` | `str` | Yes | Your HubSpot OAuth2 Refresh Token |
| `access_token` | `str` | No | Your HubSpot OAuth2 Access Token (optional if refresh_token is provided) |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Hubspot",
    "name": "My Hubspot Connector",
    "credentials": {
      "client_id": "<Your HubSpot OAuth2 Client ID>",
      "client_secret": "<Your HubSpot OAuth2 Client Secret>",
      "refresh_token": "<Your HubSpot OAuth2 Refresh Token>",
      "access_token": "<Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)>"
    }
  }'
```



#### Bring your own OAuth flow
To implement your own OAuth flow, use Airbyte's server-side OAuth API endpoints. For a complete guide, see [Build your own OAuth flow](https://docs.airbyte.com/ai-agents/platform/authenticate/build-auth/build-your-own).

##### Configure your own OAuth app credentials (optional)

By default, Airbyte uses its own OAuth app credentials. You can override these with your own so that OAuth consent screens show your company's branding. If you skip this step, the consent screen shows "Airbyte" as the requesting application.

```bash
curl -X PUT "https://api.airbyte.ai/api/v1/oauth/credentials" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "hubspot",
    "configuration": {
      "client_id": "<Your HubSpot OAuth app's client ID>",
      "client_secret": "<Your HubSpot OAuth app's client secret>"
    }
  }'
```

**To revert to Airbyte-managed defaults**:

```bash
curl -X DELETE "https://api.airbyte.ai/api/v1/oauth/credentials/connector_type/hubspot" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>"
```

##### Step 1: Initiate the OAuth flow

Request a consent URL for your user.

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `workspace_name` | `string` | Yes | Your unique identifier for the workspace |
| `connector_type` | `string` | Yes | The connector type (e.g., "Hubspot") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Hubspot",
    "redirect_url": "https://yourapp.com/oauth/callback"
  }'
```

Redirect your user to the `consent_url` from the response.

##### Step 2: Handle the callback

After the user authorizes access, Airbyte automatically creates the connector and redirects them to your `redirect_url` with a `connector_id` query parameter. You don't need to make a separate API call to create the connector.

```text
https://yourapp.com/oauth/callback?connector_id=<connector_id>
```

Extract the `connector_id` from the callback URL and store it for future operations. For error handling and a complete implementation example, see [Build your own OAuth flow](https://docs.airbyte.com/ai-agents/platform/authenticate/build-auth/build-your-own#part-3-handle-the-callback).

#### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `private_app_token` | `str` | Yes | Access token from a HubSpot Private App |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Hubspot",
    "name": "My Hubspot Connector",
    "credentials": {
      "private_app_token": "<Access token from a HubSpot Private App>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.


**Python SDK**

The `connect()` factory returns a fully typed `HubspotConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

@tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@HubspotConnector.tool_utils(framework="openai_agents")
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Hubspot Assistant", tools=[hubspot_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector

connector = connect("hubspot", workspace_name="<your_workspace_name>")

mcp = FastMCP("Hubspot Agent")

@mcp.tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
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
@HubspotConnector.tool_utils(framework="openai_agents")
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Hubspot Assistant", tools=[hubspot_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.hubspot import HubspotConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = HubspotConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Hubspot Agent")

@mcp.tool
@HubspotConnector.tool_utils
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute Hubspot connector operations."""
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


