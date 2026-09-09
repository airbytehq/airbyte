# Amplitude

The Amplitude agent connector is a Python package that equips AI agents to interact with Amplitude through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Amplitude Analytics API. Provides access to core analytics data including event exports, cohort definitions, chart annotations, event type listings, active user counts, and average session length metrics. Authentication uses HTTP Basic with your Amplitude API key and secret key.


## Example prompts

The Amplitude connector is optimized to handle prompts like these.

- List all chart annotations in Amplitude
- Show me all cohorts
- List all event types
- Which cohorts have more than 1000 users?
- What are the most popular event types by total count?
- Show me annotations created in the last month

## Unsupported prompts

The Amplitude connector isn't currently able to handle prompts like these.

- Create a new annotation
- Delete a cohort
- Export raw event data

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Annotations | [List](./REFERENCE.md#annotations-list), [Get](./REFERENCE.md#annotations-get), [Context Store Search](./REFERENCE.md#annotations-context-store-search) |
| Cohorts | [List](./REFERENCE.md#cohorts-list), [Get](./REFERENCE.md#cohorts-get), [Context Store Search](./REFERENCE.md#cohorts-context-store-search) |
| Events List | [List](./REFERENCE.md#events-list-list), [Context Store Search](./REFERENCE.md#events-list-context-store-search) |
| Active Users | [List](./REFERENCE.md#active-users-list), [Context Store Search](./REFERENCE.md#active-users-context-store-search) |
| Average Session Length | [List](./REFERENCE.md#average-session-length-list), [Context Store Search](./REFERENCE.md#average-session-length-context-store-search) |


## Amplitude API docs

See the official [Amplitude API reference](https://www.docs.developers.amplitude.com/analytics/apis/).

## Interfaces

Use the Amplitude connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "amplitude"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "amplitude"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "amplitude",
  "entity": "annotations",
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

The `connect()` factory returns a fully typed `AmplitudeConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amplitude Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amplitude Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `AmplitudeConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

@tool
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amplitude connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AmplitudeConnector.tool_utils(framework="openai_agents")
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amplitude connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amplitude Assistant", tools=[amplitude_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector

connector = connect("amplitude", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amplitude Agent")

@mcp.tool
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amplitude connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmplitudeConnector(
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
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmplitudeConnector(
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
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmplitudeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amplitude Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmplitudeConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Amplitude Agent")

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
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
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
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Amplitude Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

mcp = FastMCP("Amplitude Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `AmplitudeConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

@tool
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amplitude connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@AmplitudeConnector.tool_utils(framework="openai_agents")
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amplitude connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Amplitude Assistant", tools=[amplitude_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amplitude import AmplitudeConnector
from airbyte_agent_sdk.connectors.amplitude.models import AmplitudeAuthConfig

connector = AmplitudeConnector(
    auth_config=AmplitudeAuthConfig(
        api_key="<Your Amplitude project API key. Find it in Settings > Projects in your Amplitude account.
>",
        secret_key="<Your Amplitude project secret key. Find it in Settings > Projects in your Amplitude account.
>"
    )
)

mcp = FastMCP("Amplitude Agent")

@mcp.tool
@AmplitudeConnector.tool_utils
async def amplitude_execute(entity: str, action: str, params: dict | None = None):
    """Execute Amplitude connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.3