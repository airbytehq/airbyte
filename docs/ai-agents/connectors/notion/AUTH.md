# Notion authentication

This page documents the authentication and configuration options for the Notion agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your Notion OAuth integration's client ID |
| `client_secret` | `str` | Yes | Your Notion OAuth integration's client secret |
| `access_token` | `str` | Yes | OAuth access token obtained through the Notion authorization flow |

Example request:

```python
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionOauth20AuthConfig

connector = NotionConnector(
    auth_config=NotionOauth20AuthConfig(
        client_id="<Your Notion OAuth integration's client ID>",
        client_secret="<Your Notion OAuth integration's client secret>",
        access_token="<OAuth access token obtained through the Notion authorization flow>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | Notion internal integration token (starts with ntn_ or secret_) |

Example request:

```python
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.connectors.notion.models import NotionAccessTokenAuthConfig

connector = NotionConnector(
    auth_config=NotionAccessTokenAuthConfig(
        token="<Notion internal integration token (starts with ntn_ or secret_)>"
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
| `client_id` | `str` | Yes | Your Notion OAuth integration's client ID |
| `client_secret` | `str` | Yes | Your Notion OAuth integration's client secret |
| `access_token` | `str` | Yes | OAuth access token obtained through the Notion authorization flow |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Notion",
    "name": "My Notion Connector",
    "credentials": {
      "client_id": "<Your Notion OAuth integration's client ID>",
      "client_secret": "<Your Notion OAuth integration's client secret>",
      "access_token": "<OAuth access token obtained through the Notion authorization flow>"
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
    "connector_type": "notion",
    "configuration": {
      "client_id": "<Your Notion OAuth integration's client ID>",
      "client_secret": "<Your Notion OAuth integration's client secret>"
    }
  }'
```

**To revert to Airbyte-managed defaults**:

```bash
curl -X DELETE "https://api.airbyte.ai/api/v1/oauth/credentials/connector_type/notion" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>"
```

##### Step 1: Initiate the OAuth flow

Request a consent URL for your user.

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `workspace_name` | `string` | Yes | Your unique identifier for the workspace |
| `connector_type` | `string` | Yes | The connector type (e.g., "Notion") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Notion",
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
| `token` | `str` | Yes | Notion internal integration token (starts with ntn_ or secret_) |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Notion",
    "name": "My Notion Connector",
    "credentials": {
      "token": "<Notion internal integration token (starts with ntn_ or secret_)>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.


**Python SDK**

The `connect()` factory returns a fully typed `NotionConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.notion import NotionConnector

connector = connect("notion", workspace_name="<your_workspace_name>")

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
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
@NotionConnector.tool_utils(framework="openai_agents")
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Notion Assistant", tools=[notion_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.notion import NotionConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = NotionConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Notion Agent")

@mcp.tool
@NotionConnector.tool_utils
async def notion_execute(entity: str, action: str, params: dict | None = None):
    """Execute Notion connector operations."""
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


