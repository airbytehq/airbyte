# Google-Drive

The Google-Drive agent connector is a Python package that equips AI agents to interact with Google-Drive through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Google Drive is a cloud-based file storage and synchronization service that allows users
to store files, share content, and collaborate on documents. This connector provides
access to files, shared drives, permissions, comments, replies, revisions,
and change tracking, including the ability to create, update, delete, and upload files.


## Example prompts

The Google-Drive connector is optimized to handle prompts like these.

- List all files in my Google Drive
- Show me details for a recent file
- Download a recent file from my Drive
- Export a recent Google Doc as PDF
- Export a recent Google Sheet as CSV
- Show me the content of a recent file
- List all shared drives I have access to
- Show me details for a shared drive I have access to
- Show permissions for a recent file
- List comments on a recent file
- Show replies to a recent comment on a file
- Show revision history for a recent file
- Get my Drive storage quota and user info
- List files in a folder I have access to
- Create a new file in Google Drive
- Upload a document to Drive
- Delete a file from Drive
- Move a file to a different folder
- Show me files modified in the last week
- What changes have been made since my last sync?

## Unsupported prompts

The Google-Drive connector isn't currently able to handle prompts like these.

- Update file permissions
- Add a comment to a file

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Files | [List](./REFERENCE.md#files-list), [Get](./REFERENCE.md#files-get), [Create](./REFERENCE.md#files-create), [Update](./REFERENCE.md#files-update), [Delete](./REFERENCE.md#files-delete), [Download](./REFERENCE.md#files-download), [Context Store Search](./REFERENCE.md#files-context-store-search), [Context Store SQL Query](./REFERENCE.md#files-context-store-sql-query), [Semantic Search](./REFERENCE.md#files-semantic-search) |
| Files Upload | [Create](./REFERENCE.md#files-upload-create) |
| Files Export | [Download](./REFERENCE.md#files-export-download) |
| Drives | [List](./REFERENCE.md#drives-list), [Get](./REFERENCE.md#drives-get) |
| Permissions | [List](./REFERENCE.md#permissions-list), [Get](./REFERENCE.md#permissions-get) |
| Comments | [List](./REFERENCE.md#comments-list), [Get](./REFERENCE.md#comments-get) |
| Replies | [List](./REFERENCE.md#replies-list), [Get](./REFERENCE.md#replies-get) |
| Revisions | [List](./REFERENCE.md#revisions-list), [Get](./REFERENCE.md#revisions-get) |
| Changes | [List](./REFERENCE.md#changes-list) |
| Changes Start Page Token | [Get](./REFERENCE.md#changes-start-page-token-get) |
| About | [Get](./REFERENCE.md#about-get) |


## Google-Drive API docs

See the official [Google-Drive API reference](https://developers.google.com/workspace/drive/api/reference/rest/v3).

## Interfaces

Use the Google-Drive connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "google-drive"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "google-drive"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "google-drive",
  "entity": "files",
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

The `connect()` factory returns a fully typed `GoogleDriveConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Google-Drive Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Drive Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `GoogleDriveConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleDriveConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="google_drive_inspect",
    docs_tool="google_drive_read_docs",
)
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@GoogleDriveConnector.agent_tool(framework="pydantic_ai")
async def google_drive_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@GoogleDriveConnector.agent_tool(framework="pydantic_ai")
async def google_drive_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

@GoogleDriveConnector.agent_tool(
    inspect_tool="google_drive_inspect",
    docs_tool="google_drive_read_docs",
)
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@GoogleDriveConnector.agent_tool()
async def google_drive_inspect():
    return await connector.inspect_connector()

@GoogleDriveConnector.agent_tool()
async def google_drive_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (google_drive_inspect, google_drive_read_docs, google_drive_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `GoogleDriveConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `GoogleDriveConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

@tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleDriveConnector.tool_utils(framework="openai_agents")
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Drive Assistant", tools=[google_drive_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector

connector = connect("google-drive", workspace_name="<your_workspace_name>")

mcp = FastMCP("Google-Drive Agent")

@mcp.tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
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
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
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
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Google-Drive Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = GoogleDriveConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Google-Drive Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
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
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Google-Drive Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

mcp = FastMCP("Google-Drive Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `GoogleDriveConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleDriveConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="google_drive_inspect",
    docs_tool="google_drive_read_docs",
)
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@GoogleDriveConnector.agent_tool(framework="pydantic_ai")
async def google_drive_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@GoogleDriveConnector.agent_tool(framework="pydantic_ai")
async def google_drive_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

@GoogleDriveConnector.agent_tool(
    inspect_tool="google_drive_inspect",
    docs_tool="google_drive_read_docs",
)
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@GoogleDriveConnector.agent_tool()
async def google_drive_inspect():
    return await connector.inspect_connector()

@GoogleDriveConnector.agent_tool()
async def google_drive_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (google_drive_inspect, google_drive_read_docs, google_drive_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `GoogleDriveConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `GoogleDriveConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

@tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@GoogleDriveConnector.tool_utils(framework="openai_agents")
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Google-Drive Assistant", tools=[google_drive_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.google_drive import GoogleDriveConnector
from airbyte_agent_sdk.connectors.google_drive.models import GoogleDriveAuthConfig

connector = GoogleDriveConnector(
    auth_config=GoogleDriveAuthConfig(
        access_token="<Your Google OAuth2 Access Token (optional, will be obtained via refresh)>",
        refresh_token="<Your Google OAuth2 Refresh Token>",
        client_id="<Your Google OAuth2 Client ID>",
        client_secret="<Your Google OAuth2 Client Secret>"
    )
)

mcp = FastMCP("Google-Drive Agent")

@mcp.tool
@GoogleDriveConnector.tool_utils
async def google_drive_execute(entity: str, action: str, params: dict | None = None):
    """Execute Google-Drive connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 0.2.5