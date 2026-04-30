# Salesforce

The Salesforce agent connector is a Python package that equips AI agents to interact with Salesforce through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Salesforce is a cloud-based CRM platform that helps businesses manage customer
relationships, sales pipelines, and business operations. This connector provides
access to accounts, contacts, leads, opportunities, tasks, events, campaigns, cases,
notes, and attachments for sales analytics and customer relationship management.


## Example questions

The Salesforce connector is optimized to handle prompts like these.

- List recent contacts in my Salesforce account
- List open cases in my Salesforce account
- Show me the notes and attachments for a recent account
- List all available reports in Salesforce
- Run my quarterly revenue report and show the results
- Show me my top 5 opportunities this month
- List all contacts from \{company\} in the last quarter
- Search for leads in the technology sector with revenue over $10M
- What trends can you identify in my recent sales pipeline?
- Summarize the open cases for my key accounts
- Find upcoming events related to my most important opportunities
- Analyze the performance of my recent marketing campaigns
- Identify the highest value opportunities I'm currently tracking

## Unsupported questions

The Salesforce connector isn't currently able to handle prompts like these.

- Create a new lead for \{person\}
- Update the status of my sales opportunity
- Schedule a follow-up meeting with \{customer\}
- Delete this old contact record
- Send an email to all contacts in this campaign

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
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.connectors.salesforce.models import SalesforceAuthConfig

connector = SalesforceConnector(
    auth_config=SalesforceAuthConfig(
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)

@agent.tool_plain
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.connectors.salesforce.models import SalesforceAuthConfig

connector = SalesforceConnector(
    auth_config=SalesforceAuthConfig(
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)

@tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.connectors.salesforce.models import SalesforceAuthConfig

connector = SalesforceConnector(
    auth_config=SalesforceAuthConfig(
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)

mcp = FastMCP("Salesforce Agent")

@mcp.tool()
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `SalesforceConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

@agent.tool_plain
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

@tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

mcp = FastMCP("Salesforce Agent")

@mcp.tool()
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SalesforceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SalesforceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = SalesforceConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Salesforce Agent")

@mcp.tool()
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Sobjects | [List](./REFERENCE.md#sobjects-list) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [API Search](./REFERENCE.md#accounts-api_search), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get), [API Search](./REFERENCE.md#contacts-api_search), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Leads | [List](./REFERENCE.md#leads-list), [Get](./REFERENCE.md#leads-get), [API Search](./REFERENCE.md#leads-api_search), [Context Store Search](./REFERENCE.md#leads-context-store-search) |
| Opportunities | [List](./REFERENCE.md#opportunities-list), [Get](./REFERENCE.md#opportunities-get), [API Search](./REFERENCE.md#opportunities-api_search), [Context Store Search](./REFERENCE.md#opportunities-context-store-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Get](./REFERENCE.md#tasks-get), [API Search](./REFERENCE.md#tasks-api_search), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Events | [List](./REFERENCE.md#events-list), [Get](./REFERENCE.md#events-get), [API Search](./REFERENCE.md#events-api_search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [API Search](./REFERENCE.md#campaigns-api_search) |
| Cases | [List](./REFERENCE.md#cases-list), [Get](./REFERENCE.md#cases-get), [API Search](./REFERENCE.md#cases-api_search) |
| Notes | [List](./REFERENCE.md#notes-list), [Get](./REFERENCE.md#notes-get), [API Search](./REFERENCE.md#notes-api_search) |
| Content Versions | [List](./REFERENCE.md#content-versions-list), [Get](./REFERENCE.md#content-versions-get), [Download](./REFERENCE.md#content-versions-download) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Reports | [List](./REFERENCE.md#reports-list), [Get](./REFERENCE.md#reports-get) |
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Opportunity Stages | [List](./REFERENCE.md#opportunity-stages-list), [Get](./REFERENCE.md#opportunity-stages-get), [Context Store Search](./REFERENCE.md#opportunity-stages-context-store-search) |
| Query | [List](./REFERENCE.md#query-list) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Salesforce API docs

See the official [Salesforce API reference](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm).

## Version information

- **Package version:** 1.0.17
- **Connector version:** 1.0.17
- **Generated with Connector SDK commit SHA:** unknown