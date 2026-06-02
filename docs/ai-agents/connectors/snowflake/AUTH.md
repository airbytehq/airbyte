# Snowflake authentication

This page documents the authentication and configuration options for the Snowflake agent connector.

## Hosted mode (most cases)

In hosted mode, create the connector through the Airbyte Agent CLI or API, then execute operations using the CLI, Python SDK, or API. If you need a step-by-step guide, see the [developer quickstart](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

### OAuth
This authentication method isn't available for this connector.


### Token
Create a connector with Token credentials.


`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `programmatic_access_token` | `str` | Yes | Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake. |

`replication_config` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `database` | `str` | Yes | The database for Airbyte to access data. |
| `warehouse` | `str` | Yes | The warehouse for Airbyte to access data. |
| `role` | `str` | Yes | The role for Airbyte to access Snowflake. |

Example request:


```bash
curl -X POST "https://api.airbyte.ai/api/v1/integrations/connectors" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_name": "<WORKSPACE_NAME>",
    "connector_type": "Snowflake",
    "name": "My Snowflake Connector",
    "credentials": {
      "programmatic_access_token": "<Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.>"
    },
    "replication_config": {
      "database": "<The database for Airbyte to access data.>",
      "warehouse": "<The warehouse for Airbyte to access data.>",
      "role": "<The role for Airbyte to access Snowflake.>"
    }
  }'
```

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
  "name": "snowflake"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "<entity>",
  "action": "<action>",
  "params": {}
}'
```

**Python SDK**

The `connect()` factory returns a fully typed `SnowflakeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector

connector = connect("snowflake", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SnowflakeConnector.tool_utils
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector

connector = connect("snowflake", workspace_name="<your_workspace_name>")

@tool
@SnowflakeConnector.tool_utils
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snowflake connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector

connector = connect("snowflake", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SnowflakeConnector.tool_utils(framework="openai_agents")
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snowflake connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Snowflake Assistant", tools=[snowflake_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector

connector = connect("snowflake", workspace_name="<your_workspace_name>")

mcp = FastMCP("Snowflake Agent")

@mcp.tool
@SnowflakeConnector.tool_utils
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snowflake connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):
**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnowflakeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SnowflakeConnector.tool_utils
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnowflakeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@SnowflakeConnector.tool_utils
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snowflake connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnowflakeConnector(
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
@SnowflakeConnector.tool_utils(framework="openai_agents")
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snowflake connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Snowflake Assistant", tools=[snowflake_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SnowflakeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Snowflake Agent")

@mcp.tool
@SnowflakeConnector.tool_utils
async def snowflake_execute(entity: str, action: str, params: dict | None = None):
    """Execute Snowflake connector operations."""
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
This authentication method isn't available for this connector.

### Token

`credentials` fields you need:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `programmatic_access_token` | `str` | Yes | Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake. |

Example request:

```python
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector
from airbyte_agent_sdk.connectors.snowflake.models import SnowflakeAuthConfig

connector = SnowflakeConnector(
    auth_config=SnowflakeAuthConfig(
        programmatic_access_token="<Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.>"
    )
)
```

## Configuration

The Snowflake connector also needs these configuration values to construct the base API URL.

- **Hosted CLI**: `airbyte-agent connectors create` doesn't currently accept these configuration fields directly. For hosted connectors that need these values, create the connector with the hosted API `replication_config`, then use the CLI for describe and execute operations after creation.
- **Hosted API**: pass these values in the connector creation `replication_config`.
- **Open source mode**: provide these values with your local connector setup so the connector can build the correct API base URL.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `account` | `string` | Yes | orgname-accountname | Snowflake account identifier in the format orgname-accountname (e.g., myorg-myaccount) |
