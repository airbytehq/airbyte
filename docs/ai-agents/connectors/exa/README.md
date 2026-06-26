# Exa

The Exa agent connector is a Python package that equips AI agents to interact with Exa through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Exa is an AI-powered search engine that finds the exact content you're looking
for on the web using embeddings-based search. This connector provides access to
Exa's search, contents retrieval, and find-similar endpoints. All endpoints use
POST requests with JSON bodies. Requires an Exa API key from dashboard.exa.ai.


## Example prompts

The Exa connector is optimized to handle prompts like these.

- Search for latest news on Airbyte
- Find web pages similar to https://airbyte.com
- Get the full text content of https://airbyte.com
- Search for AI research papers published this year
- Find company pages related to data integration startups

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Search Results | [List](./REFERENCE.md#search-results-list) |
| Contents | [List](./REFERENCE.md#contents-list) |
| Similar Results | [List](./REFERENCE.md#similar-results-list) |


## Exa API docs

See the official [Exa API reference](https://docs.exa.ai/reference/getting-started).

## Interfaces

Use the Exa connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "exa"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "exa"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "exa",
  "entity": "search_results",
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

The `connect()` factory returns a fully typed `ExaConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.exa import ExaConnector

connector = connect("exa", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.exa import ExaConnector

connector = connect("exa", workspace_name="<your_workspace_name>")

@tool
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.exa import ExaConnector

connector = connect("exa", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ExaConnector.tool_utils(framework="openai_agents")
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Exa Assistant", tools=[exa_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.exa import ExaConnector

connector = connect("exa", workspace_name="<your_workspace_name>")

mcp = FastMCP("Exa Agent")

@mcp.tool
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ExaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ExaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ExaConnector(
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
@ExaConnector.tool_utils(framework="openai_agents")
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Exa Assistant", tools=[exa_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = ExaConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Exa Agent")

@mcp.tool
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

##### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.connectors.exa.models import ExaAuthConfig

connector = ExaConnector(
    auth_config=ExaAuthConfig(
        api_key="<Your Exa API key from dashboard.exa.ai/api-keys>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.connectors.exa.models import ExaAuthConfig

connector = ExaConnector(
    auth_config=ExaAuthConfig(
        api_key="<Your Exa API key from dashboard.exa.ai/api-keys>"
    )
)

@tool
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.connectors.exa.models import ExaAuthConfig

connector = ExaConnector(
    auth_config=ExaAuthConfig(
        api_key="<Your Exa API key from dashboard.exa.ai/api-keys>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@ExaConnector.tool_utils(framework="openai_agents")
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Exa Assistant", tools=[exa_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.exa import ExaConnector
from airbyte_agent_sdk.connectors.exa.models import ExaAuthConfig

connector = ExaConnector(
    auth_config=ExaAuthConfig(
        api_key="<Your Exa API key from dashboard.exa.ai/api-keys>"
    )
)

mcp = FastMCP("Exa Agent")

@mcp.tool
@ExaConnector.tool_utils
async def exa_execute(entity: str, action: str, params: dict | None = None):
    """Execute Exa connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.0