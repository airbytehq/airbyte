# Greenhouse

The Greenhouse agent connector is a Python package that equips AI agents to interact with Greenhouse through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Greenhouse is an applicant tracking system (ATS) that helps companies manage their
hiring process. This connector provides access to candidates, applications, jobs,
offers, users, departments, offices, job posts, sources, and scheduled interviews
for recruiting analytics and talent acquisition insights.


## Example prompts

The Greenhouse connector is optimized to handle prompts like these.

- List all open jobs
- Show me upcoming interviews this week
- Show me recent job offers
- List recent applications
- Show me candidates from \{company\} who applied last month
- What are the top 5 sources for our job applications this quarter?
- Analyze the interview schedules for our engineering candidates this week
- Compare the number of applications across different offices
- Identify candidates who have multiple applications in our system
- Summarize the candidate pipeline for our latest job posting
- Find the most active departments in recruiting this month

## Unsupported prompts

The Greenhouse connector isn't currently able to handle prompts like these.

- Create a new job posting for the marketing team
- Schedule an interview for \{candidate\}
- Update the status of \{candidate\}'s application
- Delete a candidate profile
- Send an offer letter to \{candidate\}
- Edit the details of a job description

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Candidates | [List](./REFERENCE.md#candidates-list), [Get](./REFERENCE.md#candidates-get), [Context Store Search](./REFERENCE.md#candidates-context-store-search) |
| Applications | [List](./REFERENCE.md#applications-list), [Get](./REFERENCE.md#applications-get), [Context Store Search](./REFERENCE.md#applications-context-store-search) |
| Jobs | [List](./REFERENCE.md#jobs-list), [Get](./REFERENCE.md#jobs-get), [Context Store Search](./REFERENCE.md#jobs-context-store-search) |
| Offers | [List](./REFERENCE.md#offers-list), [Get](./REFERENCE.md#offers-get), [Context Store Search](./REFERENCE.md#offers-context-store-search) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get), [Context Store Search](./REFERENCE.md#departments-context-store-search) |
| Offices | [List](./REFERENCE.md#offices-list), [Get](./REFERENCE.md#offices-get), [Context Store Search](./REFERENCE.md#offices-context-store-search) |
| Job Posts | [List](./REFERENCE.md#job-posts-list), [Get](./REFERENCE.md#job-posts-get), [Context Store Search](./REFERENCE.md#job-posts-context-store-search) |
| Sources | [List](./REFERENCE.md#sources-list), [Context Store Search](./REFERENCE.md#sources-context-store-search) |
| Scheduled Interviews | [List](./REFERENCE.md#scheduled-interviews-list), [Get](./REFERENCE.md#scheduled-interviews-get) |
| Application Attachment | [Download](./REFERENCE.md#application-attachment-download) |
| Candidate Attachment | [Download](./REFERENCE.md#candidate-attachment-download) |


## Greenhouse API docs

See the official [Greenhouse API reference](https://developers.greenhouse.io/harvest.html).

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

The `connect()` factory returns a fully typed `GreenhouseConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector

connector = connect("greenhouse", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector

connector = connect("greenhouse", workspace_name="<your_workspace_name>")

@tool
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector

connector = connect("greenhouse", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GreenhouseConnector.tool_utils(framework="openai_agents")
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Greenhouse Assistant", tools=[greenhouse_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector

connector = connect("greenhouse", workspace_name="<your_workspace_name>")

mcp = FastMCP("Greenhouse Agent")

@mcp.tool
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GreenhouseConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GreenhouseConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GreenhouseConnector(
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
@GreenhouseConnector.tool_utils(framework="openai_agents")
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Greenhouse Assistant", tools=[greenhouse_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GreenhouseConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Greenhouse Agent")

@mcp.tool
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.connectors.greenhouse.models import GreenhouseAuthConfig

connector = GreenhouseConnector(
    auth_config=GreenhouseAuthConfig(
        api_key="<Your Greenhouse Harvest API Key from the Dev Center>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.connectors.greenhouse.models import GreenhouseAuthConfig

connector = GreenhouseConnector(
    auth_config=GreenhouseAuthConfig(
        api_key="<Your Greenhouse Harvest API Key from the Dev Center>"
    )
)

@tool
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.connectors.greenhouse.models import GreenhouseAuthConfig

connector = GreenhouseConnector(
    auth_config=GreenhouseAuthConfig(
        api_key="<Your Greenhouse Harvest API Key from the Dev Center>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GreenhouseConnector.tool_utils(framework="openai_agents")
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Greenhouse Assistant", tools=[greenhouse_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.greenhouse import GreenhouseConnector
from airbyte_agent_sdk.connectors.greenhouse.models import GreenhouseAuthConfig

connector = GreenhouseConnector(
    auth_config=GreenhouseAuthConfig(
        api_key="<Your Greenhouse Harvest API Key from the Dev Center>"
    )
)

mcp = FastMCP("Greenhouse Agent")

@mcp.tool
@GreenhouseConnector.tool_utils
async def greenhouse_execute(entity: str, action: str, params: dict | None = None):
    """Execute Greenhouse connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.8
