# Sendgrid

The Sendgrid agent connector is a Python package that equips AI agents to interact with Sendgrid through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Twilio SendGrid v3 API. Provides read access to marketing campaigns, contacts, lists, segments, single sends, transactional templates, and suppression management (bounces, blocks, spam reports, invalid emails, global suppressions, suppression groups, and suppression group members).


## Example questions

The Sendgrid connector is optimized to handle prompts like these.

- List all marketing contacts
- Get the details of a specific contact
- Show me all marketing lists
- List all transactional templates
- Show all single sends
- List all bounced emails
- Show all blocked email addresses
- List all spam reports
- Show all suppression groups
- How many contacts are in each marketing list?
- Which single sends were scheduled in the last month?
- What are the most common bounce reasons?
- Show me contacts created in the last 7 days

## Unsupported questions

The Sendgrid connector isn't currently able to handle prompts like these.

- Send an email
- Create a new contact
- Delete a bounce record
- Update a marketing list

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
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector
from airbyte_agent_sdk.connectors.sendgrid.models import SendgridAuthConfig

connector = SendgridConnector(
    auth_config=SendgridAuthConfig(
        api_key="<Your SendGrid API key (generated at https://app.sendgrid.com/settings/api_keys)>"
    )
)

@agent.tool_plain
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector
from airbyte_agent_sdk.connectors.sendgrid.models import SendgridAuthConfig

connector = SendgridConnector(
    auth_config=SendgridAuthConfig(
        api_key="<Your SendGrid API key (generated at https://app.sendgrid.com/settings/api_keys)>"
    )
)

@tool
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Sendgrid connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector
from airbyte_agent_sdk.connectors.sendgrid.models import SendgridAuthConfig

connector = SendgridConnector(
    auth_config=SendgridAuthConfig(
        api_key="<Your SendGrid API key (generated at https://app.sendgrid.com/settings/api_keys)>"
    )
)

mcp = FastMCP("Sendgrid Agent")

@mcp.tool()
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Sendgrid connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `SendgridConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector

connector = connect("sendgrid", workspace_name="<your_workspace_name>")

@agent.tool_plain
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector

connector = connect("sendgrid", workspace_name="<your_workspace_name>")

@tool
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Sendgrid connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector

connector = connect("sendgrid", workspace_name="<your_workspace_name>")

mcp = FastMCP("Sendgrid Agent")

@mcp.tool()
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Sendgrid connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SendgridConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SendgridConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Sendgrid connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.sendgrid import SendgridConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SendgridConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Sendgrid Agent")

@mcp.tool()
@SendgridConnector.tool_utils
async def sendgrid_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Sendgrid connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get), [Context Store Search](./REFERENCE.md#lists-context-store-search) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get), [Context Store Search](./REFERENCE.md#segments-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Singlesends | [List](./REFERENCE.md#singlesends-list), [Get](./REFERENCE.md#singlesends-get), [Context Store Search](./REFERENCE.md#singlesends-context-store-search) |
| Templates | [List](./REFERENCE.md#templates-list), [Get](./REFERENCE.md#templates-get), [Context Store Search](./REFERENCE.md#templates-context-store-search) |
| Singlesend Stats | [List](./REFERENCE.md#singlesend-stats-list), [Context Store Search](./REFERENCE.md#singlesend-stats-context-store-search) |
| Bounces | [List](./REFERENCE.md#bounces-list), [Context Store Search](./REFERENCE.md#bounces-context-store-search) |
| Blocks | [List](./REFERENCE.md#blocks-list), [Context Store Search](./REFERENCE.md#blocks-context-store-search) |
| Spam Reports | [List](./REFERENCE.md#spam-reports-list) |
| Invalid Emails | [List](./REFERENCE.md#invalid-emails-list), [Context Store Search](./REFERENCE.md#invalid-emails-context-store-search) |
| Global Suppressions | [List](./REFERENCE.md#global-suppressions-list), [Context Store Search](./REFERENCE.md#global-suppressions-context-store-search) |
| Suppression Groups | [List](./REFERENCE.md#suppression-groups-list), [Get](./REFERENCE.md#suppression-groups-get), [Context Store Search](./REFERENCE.md#suppression-groups-context-store-search) |
| Suppression Group Members | [List](./REFERENCE.md#suppression-group-members-list), [Context Store Search](./REFERENCE.md#suppression-group-members-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Sendgrid API docs

See the official [Sendgrid API reference](https://docs.sendgrid.com/api-reference).

## Version information

- **Package version:** 1.0.3
- **Connector version:** 1.0.3
- **Generated with Connector SDK commit SHA:** unknown