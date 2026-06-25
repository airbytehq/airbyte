# Snowflake

The Snowflake agent connector is a Python package that equips AI agents to interact with Snowflake through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connects to Snowflake via the SQL REST API (POST /api/v2/statements) to query
metadata about databases, schemas, tables, views, warehouses, and columns,
to read records from tables and views, and to create, update, and delete
records in tables. Uses Programmatic Access Token (PAT) authentication.
Metadata operations execute SHOW commands; record operations execute the SQL
statement you provide. This connector is experimental (beta): record actions
run arbitrary SQL bounded only by the connected PAT's Snowflake role, so scope
that role to least privilege (read-only for read-only use cases).
Parameterized bind variables (the SQL API `bindings` field / `?` placeholders)
are not supported in this beta; inline literal values into the statement.


## Example prompts

The Snowflake connector is optimized to handle prompts like these.

- List all databases in Snowflake
- Show me all schemas
- What tables are available?
- List all views
- Show me the warehouses
- What columns does my data have?
- Get the record with id 42 from the users table
- List all records from the orders table
- Insert a new row into the customers table
- Update the email for user 7 in the users table
- Delete the record with id 99 from the logs table
- Find all tables in the ANALYTICS database
- Which warehouses are currently running?
- Show me all views in the PUBLIC schema
- What databases were created this month?
- Find all orders placed in the last 30 days
- Search for users with email ending in @example.com

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Databases | [List](./REFERENCE.md#databases-list) |
| Schemas | [List](./REFERENCE.md#schemas-list) |
| Tables | [List](./REFERENCE.md#tables-list) |
| Views | [List](./REFERENCE.md#views-list) |
| Warehouses | [List](./REFERENCE.md#warehouses-list) |
| Columns | [List](./REFERENCE.md#columns-list) |
| Record | [Get](./REFERENCE.md#record-get), [List](./REFERENCE.md#record-list), [Create](./REFERENCE.md#record-create), [Update](./REFERENCE.md#record-update), [Delete](./REFERENCE.md#record-delete) |
| Result Partitions | [Get](./REFERENCE.md#result-partitions-get) |


## Snowflake API docs

See the official [Snowflake API reference](https://docs.snowflake.com/en/developer-guide/sql-api/reference).

## Interfaces

Use the Snowflake connector through the Airbyte Agent CLI, the Python SDK, or the API.

### CLI

Install the CLI:

```bash
curl -fsSL https://airbyte.ai/install.sh | bash
```

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
  "entity": "databases",
  "action": "list"
}'
```

### Python SDK

#### Installation

```bash
uv pip install airbyte-agent-sdk
```

#### Usage

Connectors can run in hosted or open source mode.

##### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

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

##### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.snowflake import SnowflakeConnector
from airbyte_agent_sdk.connectors.snowflake.models import SnowflakeAuthConfig

connector = SnowflakeConnector(
    auth_config=SnowflakeAuthConfig(
        programmatic_access_token="<Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.>"
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
from airbyte_agent_sdk.connectors.snowflake.models import SnowflakeAuthConfig

connector = SnowflakeConnector(
    auth_config=SnowflakeAuthConfig(
        programmatic_access_token="<Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.>"
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
from airbyte_agent_sdk.connectors.snowflake.models import SnowflakeAuthConfig

connector = SnowflakeConnector(
    auth_config=SnowflakeAuthConfig(
        programmatic_access_token="<Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.>"
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
from airbyte_agent_sdk.connectors.snowflake.models import SnowflakeAuthConfig

connector = SnowflakeConnector(
    auth_config=SnowflakeAuthConfig(
        programmatic_access_token="<Snowflake Programmatic Access Token (PAT) for authentication. Generate one via ALTER USER ADD PROGRAMMATIC ACCESS TOKEN in Snowflake.>"
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

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.0