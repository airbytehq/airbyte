# Gmail authentication

This page documents the authentication and configuration options for the Gmail agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
Use the CLI for hosted OAuth connector creation when possible. It opens the hosted setup flow and avoids passing connector secrets through the command line:

```bash
airbyte-agent login
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "gmail"
}'
```

For API-first use cases, create a connector with OAuth credentials directly.

`credentials` fields you need:


| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | Your Google OAuth2 Access Token (optional, will be obtained via refresh) |
| `refresh_token` | `str` | Yes | Your Google OAuth2 Refresh Token |
| `client_id` | `str` | No | Your Google OAuth2 Client ID |
| `client_secret` | `str` | No | Your Google OAuth2 Client Secret |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `include_spam_and_trash` | `bool` | No | Include messages from SPAM and TRASH in the results. Defaults to false. |

Example request:

```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Gmail",
    "name": "My Gmail Connector",
    "credentials": {
      "access_token": "<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
      "refresh_token": "<Your Google OAuth2 Refresh Token>",
      "client_id": "<Your Google OAuth2 Client ID>",
      "client_secret": "<Your Google OAuth2 Client Secret>"
    },
    "replication_config": {
      "include_spam_and_trash": "<Include messages from SPAM and TRASH in the results. Defaults to false.>"
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
  "name": "gmail"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "gmail"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "gmail",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `GmailConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gmail import GmailConnector

connector = connect("gmail", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gmail import GmailConnector

connector = connect("gmail", workspace_name="<your_workspace_name>")

@tool
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gmail connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gmail import GmailConnector

connector = connect("gmail", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GmailConnector.tool_utils(framework="openai_agents")
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gmail connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Gmail Assistant", tools=[gmail_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gmail import GmailConnector

connector = connect("gmail", workspace_name="<your_workspace_name>")

mcp = FastMCP("Gmail Agent")

@mcp.tool
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gmail connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.gmail import GmailConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GmailConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.gmail import GmailConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GmailConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gmail connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.gmail import GmailConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GmailConnector(
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
@GmailConnector.tool_utils(framework="openai_agents")
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gmail connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Gmail Assistant", tools=[gmail_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.gmail import GmailConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GmailConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Gmail Agent")

@mcp.tool
@GmailConnector.tool_utils
async def gmail_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gmail connector operations."""
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
| `access_token` | `str` | No | Your Google OAuth2 Access Token (optional, will be obtained via refresh) |
| `refresh_token` | `str` | Yes | Your Google OAuth2 Refresh Token |
| `client_id` | `str` | No | Your Google OAuth2 Client ID |
| `client_secret` | `str` | No | Your Google OAuth2 Client Secret |

Example request:

```python
from airbyte_agent_sdk.connectors.gmail import GmailConnector
from airbyte_agent_sdk.connectors.gmail.models import GmailAuthConfig

connector = GmailConnector(
    auth_config=GmailAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)
```

### Token
This authentication method isn't available for this connector.

