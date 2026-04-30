# Gong

The Gong agent connector is a Python package that equips AI agents to interact with Gong through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Gong is a revenue intelligence platform that captures and analyzes customer interactions
across calls, emails, and web conferences. This connector provides access to users,
recorded calls with transcripts, activity statistics, scorecards, trackers, workspaces,
coaching metrics, and library content for sales performance analysis and revenue insights.


## Example questions

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

## Unsupported questions

The Gong connector isn't currently able to handle prompts like these.

- Create a new user in Gong
- Delete a call recording
- Update scorecard questions
- Schedule a new meeting
- Send feedback to a team member
- Modify tracker keywords

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.gong import GongConnector
from airbyte_agent_sdk.connectors.gong.models import GongAccessKeyAuthenticationAuthConfig

connector = GongConnector(
    auth_config=GongAccessKeyAuthenticationAuthConfig(
        access_key="<Your Gong API Access Key>",
        access_key_secret="<Your Gong API Access Key Secret>"
    )
)

@agent.tool_plain
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

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
async def gong_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

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

@mcp.tool()
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `GongConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

@agent.tool_plain
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

@tool
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.gong import GongConnector

connector = connect("gong", workspace_name="<your_workspace_name>")

mcp = FastMCP("Gong Agent")

@mcp.tool()
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
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

@agent.tool_plain
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
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

@tool
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

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

@mcp.tool()
@GongConnector.tool_utils
async def gong_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Gong connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Calls Extensive | [List](./REFERENCE.md#calls-extensive-list), [Context Store Search](./REFERENCE.md#calls-extensive-context-store-search) |
| Call Audio | [Download](./REFERENCE.md#call-audio-download) |
| Call Video | [Download](./REFERENCE.md#call-video-download) |
| Workspaces | [List](./REFERENCE.md#workspaces-list) |
| Call Transcripts | [List](./REFERENCE.md#call-transcripts-list) |
| Stats Activity Aggregate | [List](./REFERENCE.md#stats-activity-aggregate-list) |
| Stats Activity Day By Day | [List](./REFERENCE.md#stats-activity-day-by-day-list) |
| Stats Interaction | [List](./REFERENCE.md#stats-interaction-list) |
| Settings Scorecards | [List](./REFERENCE.md#settings-scorecards-list), [Context Store Search](./REFERENCE.md#settings-scorecards-context-store-search) |
| Settings Trackers | [List](./REFERENCE.md#settings-trackers-list) |
| Library Folders | [List](./REFERENCE.md#library-folders-list) |
| Library Folder Content | [List](./REFERENCE.md#library-folder-content-list) |
| Coaching | [List](./REFERENCE.md#coaching-list) |
| Stats Activity Scorecards | [List](./REFERENCE.md#stats-activity-scorecards-list), [Context Store Search](./REFERENCE.md#stats-activity-scorecards-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Gong API docs

See the official [Gong API reference](https://gong.app.gong.io/settings/api/documentation).

## Version information

- **Package version:** 0.1.23
- **Connector version:** 0.1.23
- **Generated with Connector SDK commit SHA:** unknown