# Gong

The Gong agent connector is a Python package that equips AI agents to interact with Gong through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Gong is a revenue intelligence platform that captures and analyzes customer interactions
across calls, emails, and web conferences. This connector provides access to users,
recorded calls with transcripts, activity statistics, scorecards, trackers, workspaces,
coaching metrics, and library content for sales performance analysis and revenue insights.


## Example prompts

The Gong connector is optimized to handle prompts like these.

- List all users in my Gong account
- Show me calls from last week
- Get the transcript for a recent call
- List all workspaces in Gong
- Show me the scorecard configurations
- What trackers are set up in my account?
- Get coaching metrics for a manager
- What are the activity stats for our sales team?
- Find calls mentioning \{keyword\} this month
- Show me calls for rep \{user_id\} in the last 30 days
- Which calls had the longest duration last week?

## Unsupported prompts

The Gong connector isn't currently able to handle prompts like these.

- Create a new user in Gong
- Delete a call recording
- Update scorecard questions
- Schedule a new meeting
- Send feedback to a team member
- Modify tracker keywords

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Calls Extensive | [List](./REFERENCE.md#calls-extensive-list), [Context Store Search](./REFERENCE.md#calls-extensive-context-store-search) |
| Call Audio | [Download](./REFERENCE.md#call-audio-download) |
| Call Video | [Download](./REFERENCE.md#call-video-download) |
| Workspaces | [List](./REFERENCE.md#workspaces-list) |
| Call Transcripts | [List](./REFERENCE.md#call-transcripts-list), [Context Store Search](./REFERENCE.md#call-transcripts-context-store-search) |
| Stats Activity Aggregate | [List](./REFERENCE.md#stats-activity-aggregate-list) |
| Stats Activity Day By Day | [List](./REFERENCE.md#stats-activity-day-by-day-list) |
| Stats Interaction | [List](./REFERENCE.md#stats-interaction-list) |
| Settings Scorecards | [List](./REFERENCE.md#settings-scorecards-list), [Context Store Search](./REFERENCE.md#settings-scorecards-context-store-search) |
| Settings Trackers | [List](./REFERENCE.md#settings-trackers-list) |
| Library Folders | [List](./REFERENCE.md#library-folders-list) |
| Library Folder Content | [List](./REFERENCE.md#library-folder-content-list) |
| Coaching | [List](./REFERENCE.md#coaching-list) |
| Stats Activity Scorecards | [List](./REFERENCE.md#stats-activity-scorecards-list), [Context Store Search](./REFERENCE.md#stats-activity-scorecards-context-store-search) |


## Gong API docs

See the official [Gong API reference](https://gong.app.gong.io/settings/api/documentation).

## Interfaces

Use the Gong connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "gong"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "gong"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "gong",
  "entity": "users",
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

The `connect()` factory returns a fully typed `GongConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Gong Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

mcp = FastMCP("Gong Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `GongConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

@tool
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GongConnector.tool_utils(framework="openai_agents")
async def gong_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Gong Assistant", tools=[gong_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

mcp = FastMCP("Gong Agent")

@mcp.tool
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GongConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GongConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GongConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Gong Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GongConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Gong Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Gong Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

mcp = FastMCP("Gong Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `GongConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

@tool
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GongConnector.tool_utils(framework="openai_agents")
async def gong_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Gong Assistant", tools=[gong_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

mcp = FastMCP("Gong Agent")

@mcp.tool
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.1.24