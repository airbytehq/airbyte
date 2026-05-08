# Github authentication

This page documents the authentication and configuration options for the Github agent connector.

## Authentication

### Open source execution

In open source mode, you provide API credentials directly to the connector.

#### OAuth

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |

Example request:

```python
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubOauth2AuthConfig

connector = GithubConnector(
    auth_config=GithubOauth2AuthConfig(
        access_token="<OAuth 2.0 access token>"
    )
)
```

#### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | GitHub personal access token (fine-grained or classic) |

Example request:

```python
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.connectors.github.models import GithubPersonalAccessTokenAuthConfig

connector = GithubConnector(
    auth_config=GithubPersonalAccessTokenAuthConfig(
        token="<GitHub personal access token (fine-grained or classic)>"
    )
)
```

### Hosted execution

In hosted mode, you first create a connector via the Airbyte Agent API (providing your OAuth or Token credentials), then execute operations using either the Python SDK or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

#### OAuth
Create a connector with OAuth credentials.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `repositories` | `str` | Yes | List of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/*` for all repositories from organization |
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Github",
    "name": "My Github Connector",
    "credentials": {
      "access_token": "<OAuth 2.0 access token>"
    },
    "replication_config": {
      "repositories": "<List of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/*` for all repositories from organization>",
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.>"
    }
  }'
```



#### Bring your own OAuth flow
To implement your own OAuth flow, use Airbyte's server-side OAuth API endpoints. For a complete guide, see [Build your own OAuth flow](https://docs.airbyte.com/ai-agents/platform/authenticate/build-auth/build-your-own).

##### Step 1: Initiate the OAuth flow

Request a consent URL for your user.

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `workspace_name` | `string` | Yes | Your unique identifier for the workspace |
| `connector_type` | `string` | Yes | The connector type (e.g., "Github") |
| `redirect_url` | `string` | Yes | URL to redirect to after OAuth authorization |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors/oauth/initiate" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Github",
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
| `token` | `str` | Yes | GitHub personal access token (fine-grained or classic) |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `repositories` | `str` | Yes | List of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/*` for all repositories from organization |
| `start_date` | `str (date-time)` | Yes | UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Github",
    "name": "My Github Connector",
    "credentials": {
      "token": "<GitHub personal access token (fine-grained or classic)>"
    },
    "replication_config": {
      "repositories": "<List of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/*` for all repositories from organization>",
      "start_date": "<UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.>"
    }
  }'
```

#### Execution

After creating the connector, execute operations using either the Python SDK or API.
If your Airbyte client can access multiple organizations, include `organization_id` in `AirbyteAuthConfig` and `X-Organization-Id` in raw API calls.


**Python SDK**

The `connect()` factory returns a fully typed `GithubConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GithubConnector.tool_utils(framework="openai_agents")
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Github Assistant", tools=[github_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

connector = connect("github", workspace_name="<your_workspace_name>")

mcp = FastMCP("Github Agent")

@mcp.tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
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
@GithubConnector.tool_utils(framework="openai_agents")
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Github Assistant", tools=[github_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.github import GithubConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Github Agent")

@mcp.tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute Github connector operations."""
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


