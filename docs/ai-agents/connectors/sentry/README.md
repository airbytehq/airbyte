# Sentry

The Sentry agent connector is a Python package that equips AI agents to interact with Sentry through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Sentry error monitoring and performance tracking API. Provides access to projects, issues, events, and releases within your Sentry organization. Supports listing and retrieving detailed information about error tracking data, project configurations, and software releases.

## Example prompts

The Sentry connector is optimized to handle prompts like these.

- List all projects in my Sentry organization
- Show me the issues for a specific project
- List recent events from a project
- Show me all releases for my organization
- Get the details of a specific project
- What are the most common unresolved issues?
- Which projects have the most events?
- Show me issues that were first seen this week
- Find releases created in the last month

## Unsupported prompts

The Sentry connector isn't currently able to handle prompts like these.

- Create a new project in Sentry
- Delete an issue
- Update a release
- Resolve all issues in a project

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Projects | [List](./REFERENCE.md#projects-list), [Get](./REFERENCE.md#projects-get), [Context Store Search](./REFERENCE.md#projects-context-store-search) |
| Issues | [List](./REFERENCE.md#issues-list), [Get](./REFERENCE.md#issues-get), [Context Store Search](./REFERENCE.md#issues-context-store-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [Context Store Search](./REFERENCE.md#events-context-store-search) |
| Releases | [List](./REFERENCE.md#releases-list), [Get](./REFERENCE.md#releases-get), [Context Store Search](./REFERENCE.md#releases-context-store-search) |
| Project Detail | [Get](./REFERENCE.md#project-detail-get) |


## Sentry API docs

See the official [Sentry API reference](https://docs.sentry.io/api/).

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

The `connect()` factory returns a fully typed `SentryConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sentry import SentryConnector

connector = connect("sentry", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sentry import SentryConnector

connector = connect("sentry", workspace_name="<your_workspace_name>")

@tool
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sentry import SentryConnector

connector = connect("sentry", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SentryConnector.tool_utils(framework="openai_agents")
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Sentry Assistant", tools=[sentry_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sentry import SentryConnector

connector = connect("sentry", workspace_name="<your_workspace_name>")

mcp = FastMCP("Sentry Agent")

@mcp.tool
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SentryConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SentryConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SentryConnector(
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
@SentryConnector.tool_utils(framework="openai_agents")
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Sentry Assistant", tools=[sentry_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SentryConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Sentry Agent")

@mcp.tool
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.connectors.sentry.models import SentryAuthConfig

connector = SentryConnector(
    auth_config=SentryAuthConfig(
        auth_token="<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.connectors.sentry.models import SentryAuthConfig

connector = SentryConnector(
    auth_config=SentryAuthConfig(
        auth_token="<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    )
)

@tool
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.connectors.sentry.models import SentryAuthConfig

connector = SentryConnector(
    auth_config=SentryAuthConfig(
        auth_token="<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SentryConnector.tool_utils(framework="openai_agents")
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Sentry Assistant", tools=[sentry_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.sentry import SentryConnector
from airbyte_agent_sdk.connectors.sentry.models import SentryAuthConfig

connector = SentryConnector(
    auth_config=SentryAuthConfig(
        auth_token="<Sentry authentication token. Log into Sentry and create one at Settings > Account > API > Auth Tokens.>"
    )
)

mcp = FastMCP("Sentry Agent")

@mcp.tool
@SentryConnector.tool_utils
async def sentry_execute(entity: str, action: str, params: dict | None = None):
    """Execute Sentry connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.4
