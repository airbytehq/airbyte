# Incident-Io

The Incident-Io agent connector is a Python package that equips AI agents to interact with Incident-Io through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connect to the incident.io API to access incident management data including
incidents, alerts, escalations, users, schedules, and more. incident.io is an
on-call, status pages, and incident response platform. This connector provides
read-only access to core incident management entities via the v1 and v2 APIs.
Requires an API key from your incident.io dashboard (Pro plan or above).


## Example prompts

The Incident-Io connector is optimized to handle prompts like these.

- List all incidents
- Show all open incidents
- List all alerts
- Show all users
- List all escalations
- Show all on-call schedules
- List all severities
- Show all incident statuses
- List all custom fields
- Which incidents were created this week?
- What are the most recent high-severity incidents?
- Who is currently on-call?
- How many incidents are in triage status?
- What incidents were updated today?

## Unsupported prompts

The Incident-Io connector isn't currently able to handle prompts like these.

- Create a new incident
- Update an incident's severity
- Delete an alert
- Assign someone to an incident role

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Incidents | [List](./REFERENCE.md#incidents-list), [Get](./REFERENCE.md#incidents-get), [Context Store Search](./REFERENCE.md#incidents-context-store-search) |
| Alerts | [List](./REFERENCE.md#alerts-list), [Get](./REFERENCE.md#alerts-get), [Context Store Search](./REFERENCE.md#alerts-context-store-search) |
| Escalations | [List](./REFERENCE.md#escalations-list), [Get](./REFERENCE.md#escalations-get), [Context Store Search](./REFERENCE.md#escalations-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Incident Updates | [List](./REFERENCE.md#incident-updates-list), [Context Store Search](./REFERENCE.md#incident-updates-context-store-search) |
| Incident Roles | [List](./REFERENCE.md#incident-roles-list), [Get](./REFERENCE.md#incident-roles-get), [Context Store Search](./REFERENCE.md#incident-roles-context-store-search) |
| Incident Statuses | [List](./REFERENCE.md#incident-statuses-list), [Get](./REFERENCE.md#incident-statuses-get), [Context Store Search](./REFERENCE.md#incident-statuses-context-store-search) |
| Incident Timestamps | [List](./REFERENCE.md#incident-timestamps-list), [Get](./REFERENCE.md#incident-timestamps-get), [Context Store Search](./REFERENCE.md#incident-timestamps-context-store-search) |
| Severities | [List](./REFERENCE.md#severities-list), [Get](./REFERENCE.md#severities-get), [Context Store Search](./REFERENCE.md#severities-context-store-search) |
| Custom Fields | [List](./REFERENCE.md#custom-fields-list), [Get](./REFERENCE.md#custom-fields-get), [Context Store Search](./REFERENCE.md#custom-fields-context-store-search) |
| Catalog Types | [List](./REFERENCE.md#catalog-types-list), [Get](./REFERENCE.md#catalog-types-get), [Context Store Search](./REFERENCE.md#catalog-types-context-store-search) |
| Schedules | [List](./REFERENCE.md#schedules-list), [Get](./REFERENCE.md#schedules-get), [Context Store Search](./REFERENCE.md#schedules-context-store-search) |


## Incident-Io API docs

See the official [Incident-Io API reference](https://api-docs.incident.io/).

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

The `connect()` factory returns a fully typed `IncidentIoConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector

connector = connect("incident-io", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector

connector = connect("incident-io", workspace_name="<your_workspace_name>")

@tool
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector

connector = connect("incident-io", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@IncidentIoConnector.tool_utils(framework="openai_agents")
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Incident-Io Assistant", tools=[incident_io_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector

connector = connect("incident-io", workspace_name="<your_workspace_name>")

mcp = FastMCP("Incident-Io Agent")

@mcp.tool
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IncidentIoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IncidentIoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IncidentIoConnector(
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
@IncidentIoConnector.tool_utils(framework="openai_agents")
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Incident-Io Assistant", tools=[incident_io_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = IncidentIoConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Incident-Io Agent")

@mcp.tool
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.connectors.incident_io.models import IncidentIoAuthConfig

connector = IncidentIoConnector(
    auth_config=IncidentIoAuthConfig(
        api_key="<Your incident.io API key. Create one at https://app.incident.io/settings/api-keys>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.connectors.incident_io.models import IncidentIoAuthConfig

connector = IncidentIoConnector(
    auth_config=IncidentIoAuthConfig(
        api_key="<Your incident.io API key. Create one at https://app.incident.io/settings/api-keys>"
    )
)

@tool
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.connectors.incident_io.models import IncidentIoAuthConfig

connector = IncidentIoConnector(
    auth_config=IncidentIoAuthConfig(
        api_key="<Your incident.io API key. Create one at https://app.incident.io/settings/api-keys>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@IncidentIoConnector.tool_utils(framework="openai_agents")
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Incident-Io Assistant", tools=[incident_io_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.incident_io import IncidentIoConnector
from airbyte_agent_sdk.connectors.incident_io.models import IncidentIoAuthConfig

connector = IncidentIoConnector(
    auth_config=IncidentIoAuthConfig(
        api_key="<Your incident.io API key. Create one at https://app.incident.io/settings/api-keys>"
    )
)

mcp = FastMCP("Incident-Io Agent")

@mcp.tool
@IncidentIoConnector.tool_utils
async def incident_io_execute(entity: str, action: str, params: dict | None = None):
    """Execute Incident-Io connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 1.0.4
