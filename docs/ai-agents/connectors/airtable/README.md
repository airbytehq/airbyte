# Airtable

The Airtable agent connector is a Python package that equips AI agents to interact with Airtable through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Airtable is a cloud-based platform that combines the simplicity of a spreadsheet with the 
power of a database. This connector provides access to bases, tables, and records for 
data analysis and workflow automation.


## Example prompts

The Airtable connector is optimized to handle prompts like these.

- List all my Airtable bases
- What tables are in my first base?
- Show me the schema for tables in a base
- List records from a table in my base
- Show me recent records from a table
- What fields are in a table?
- List records where Status is 'Done' in table tblXXX
- Find records created last week in table tblXXX
- Show me records updated in the last 30 days in base appXXX

## Unsupported prompts

The Airtable connector isn't currently able to handle prompts like these.

- Create a new record in Airtable
- Update a record in Airtable
- Delete a record from Airtable
- Create a new table
- Modify table schema

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Bases | [List](./REFERENCE.md#bases-list), [Context Store Search](./REFERENCE.md#bases-context-store-search) |
| Tables | [List](./REFERENCE.md#tables-list), [Context Store Search](./REFERENCE.md#tables-context-store-search) |
| Records | [List](./REFERENCE.md#records-list), [Get](./REFERENCE.md#records-get) |


## Airtable API docs

See the official [Airtable API reference](https://airtable.com/developers/web/api/introduction).

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

The `connect()` factory returns a fully typed `AirtableConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.airtable import AirtableConnector

connector = connect("airtable", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.airtable import AirtableConnector

connector = connect("airtable", workspace_name="<your_workspace_name>")

@tool
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.airtable import AirtableConnector

connector = connect("airtable", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AirtableConnector.tool_utils(framework="openai_agents")
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Airtable Assistant", tools=[airtable_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.airtable import AirtableConnector

connector = connect("airtable", workspace_name="<your_workspace_name>")

mcp = FastMCP("Airtable Agent")

@mcp.tool
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AirtableConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AirtableConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AirtableConnector(
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
@AirtableConnector.tool_utils(framework="openai_agents")
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Airtable Assistant", tools=[airtable_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AirtableConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Airtable Agent")

@mcp.tool
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.connectors.airtable.models import AirtableAuthConfig

connector = AirtableConnector(
    auth_config=AirtableAuthConfig(
        personal_access_token="<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.connectors.airtable.models import AirtableAuthConfig

connector = AirtableConnector(
    auth_config=AirtableAuthConfig(
        personal_access_token="<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
    )
)

@tool
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.connectors.airtable.models import AirtableAuthConfig

connector = AirtableConnector(
    auth_config=AirtableAuthConfig(
        personal_access_token="<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AirtableConnector.tool_utils(framework="openai_agents")
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Airtable Assistant", tools=[airtable_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.airtable import AirtableConnector
from airbyte_agent_sdk.connectors.airtable.models import AirtableAuthConfig

connector = AirtableConnector(
    auth_config=AirtableAuthConfig(
        personal_access_token="<Airtable Personal Access Token. See https://airtable.com/developers/web/guides/personal-access-tokens>"
    )
)

mcp = FastMCP("Airtable Agent")

@mcp.tool
@AirtableConnector.tool_utils
async def airtable_execute(entity: str, action: str, params: dict | None = None):
    """Execute Airtable connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.8
