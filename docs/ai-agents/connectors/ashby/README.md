# Ashby

The Ashby agent connector is a Python package that equips AI agents to interact with Ashby through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Ashby is a modern applicant tracking system (ATS) and recruiting platform that helps companies manage their hiring process. This connector provides access to candidates, applications, jobs, departments, locations, users, job postings, sources, archive reasons, candidate tags, custom fields, and feedback form definitions for talent acquisition analytics and hiring insights.


## Example prompts

The Ashby connector is optimized to handle prompts like these.

- List all open jobs
- Show me all candidates
- List recent applications
- List all departments
- Show me all job postings
- List all users in the organization
- Show me candidates who applied last month
- What are the top sources for job applications?
- Compare the number of applications across different departments
- Find candidates with multiple applications
- Summarize the candidate pipeline for our latest job posting
- Find the most active departments in recruiting this month

## Unsupported prompts

The Ashby connector isn't currently able to handle prompts like these.

- Create a new job posting
- Schedule an interview for a candidate
- Update a candidates application status
- Delete a candidate profile
- Send an offer letter to a candidate

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Candidates | [List](./REFERENCE.md#candidates-list), [Get](./REFERENCE.md#candidates-get), [Context Store Search](./REFERENCE.md#candidates-context-store-search) |
| Applications | [List](./REFERENCE.md#applications-list), [Get](./REFERENCE.md#applications-get), [Context Store Search](./REFERENCE.md#applications-context-store-search) |
| Jobs | [List](./REFERENCE.md#jobs-list), [Get](./REFERENCE.md#jobs-get), [Context Store Search](./REFERENCE.md#jobs-context-store-search) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get) |
| Locations | [List](./REFERENCE.md#locations-list), [Get](./REFERENCE.md#locations-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Job Postings | [List](./REFERENCE.md#job-postings-list), [Get](./REFERENCE.md#job-postings-get), [Context Store Search](./REFERENCE.md#job-postings-context-store-search) |
| Sources | [List](./REFERENCE.md#sources-list) |
| Archive Reasons | [List](./REFERENCE.md#archive-reasons-list) |
| Candidate Tags | [List](./REFERENCE.md#candidate-tags-list) |
| Custom Fields | [List](./REFERENCE.md#custom-fields-list) |
| Feedback Form Definitions | [List](./REFERENCE.md#feedback-form-definitions-list) |


## Ashby API docs

See the official [Ashby API reference](https://developers.ashbyhq.com/reference).

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

The `connect()` factory returns a fully typed `AshbyConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

@tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AshbyConnector.tool_utils(framework="openai_agents")
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Ashby Assistant", tools=[ashby_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.ashby import AshbyConnector

connector = connect("ashby", workspace_name="<your_workspace_name>")

mcp = FastMCP("Ashby Agent")

@mcp.tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
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
@AshbyConnector.tool_utils(framework="openai_agents")
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Ashby Assistant", tools=[ashby_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AshbyConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Ashby Agent")

@mcp.tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.connectors.ashby.models import AshbyAuthConfig

connector = AshbyConnector(
    auth_config=AshbyAuthConfig(
        api_key="<Your Ashby API key>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.connectors.ashby.models import AshbyAuthConfig

connector = AshbyConnector(
    auth_config=AshbyAuthConfig(
        api_key="<Your Ashby API key>"
    )
)

@tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.connectors.ashby.models import AshbyAuthConfig

connector = AshbyConnector(
    auth_config=AshbyAuthConfig(
        api_key="<Your Ashby API key>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AshbyConnector.tool_utils(framework="openai_agents")
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Ashby Assistant", tools=[ashby_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.ashby import AshbyConnector
from airbyte_agent_sdk.connectors.ashby.models import AshbyAuthConfig

connector = AshbyConnector(
    auth_config=AshbyAuthConfig(
        api_key="<Your Ashby API key>"
    )
)

mcp = FastMCP("Ashby Agent")

@mcp.tool
@AshbyConnector.tool_utils
async def ashby_execute(entity: str, action: str, params: dict | None = None):
    """Execute Ashby connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.4
