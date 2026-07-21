# Granola

The Granola agent connector is a Python package that equips AI agents to interact with Granola through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

The Granola API connector provides read access to meeting notes from Granola,
an AI-powered meeting notes platform. This connector integrates with the Granola
API to list and retrieve notes, including summaries, transcripts, attendees,
and calendar event details. Requires a Granola API key.


## Example prompts

The Granola connector is optimized to handle prompts like these.

- List all meeting notes from Granola
- Show me recent meeting notes
- Get the details of a specific note
- List notes created in the last week
- Find meeting notes from last month
- Which meetings had the most attendees?
- Show me notes that mention budget reviews
- What meetings happened this quarter?

## Unsupported prompts

The Granola connector isn't currently able to handle prompts like these.

- Create a new meeting note
- Delete a meeting note
- Update an existing note
- Share a note with someone

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [Context Store Search](./REFERENCE.md#notes-context-store-search) |


## Granola API docs

See the official [Granola API reference](https://docs.granola.ai/introduction).

## Interfaces

Use the Granola connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "granola"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "granola"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "granola",
  "entity": "notes",
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

The `connect()` factory returns a fully typed `GranolaConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Granola Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

mcp = FastMCP("Granola Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `GranolaConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

@tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GranolaConnector.tool_utils(framework="openai_agents")
async def granola_execute(entity: str, action: str, params: dict | None = None):
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Granola Assistant", tools=[granola_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.granola import GranolaConnector

connector = connect("granola", workspace_name="<your_workspace_name>")

mcp = FastMCP("Granola Agent")

@mcp.tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
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
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
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
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Granola Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GranolaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Granola Agent")

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
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
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
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Granola Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

mcp = FastMCP("Granola Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `GranolaConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

@tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GranolaConnector.tool_utils(framework="openai_agents")
async def granola_execute(entity: str, action: str, params: dict | None = None):
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Granola Assistant", tools=[granola_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.granola import GranolaConnector
from airbyte_agent_sdk.connectors.granola.models import GranolaAuthConfig

connector = GranolaConnector(
    auth_config=GranolaAuthConfig(
        api_key="<Granola API key. For a personal key, open the Granola desktop app and go to Settings > Connectors > API keys > Create new key. For an Enterprise API key, go to Settings > API > Create new key. On Enterprise plans, workspace admins must enable "Allow personal API keys" in Settings > Workspace > General before personal keys can be created.>"
    )
)

mcp = FastMCP("Granola Agent")

@mcp.tool
@GranolaConnector.tool_utils
async def granola_execute(entity: str, action: str, params: dict | None = None):
    """Execute Granola connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.7