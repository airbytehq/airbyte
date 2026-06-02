# Salesforce

The Salesforce agent connector is a Python package that equips AI agents to interact with Salesforce through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Salesforce is a cloud-based CRM platform that helps businesses manage customer
relationships, sales pipelines, and business operations. This connector provides
access to accounts, contacts, leads, opportunities, tasks, events, campaigns, cases,
notes, and attachments for sales analytics and customer relationship management.


## Example prompts

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

## Unsupported prompts

The Salesforce connector isn't currently able to handle prompts like these.

- Create a new lead for \{person\}
- Update the status of my sales opportunity
- Schedule a follow-up meeting with \{customer\}
- Delete this old contact record
- Send an email to all contacts in this campaign

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Sobjects | [List](./REFERENCE.md#sobjects-list), [Create](./REFERENCE.md#sobjects-create), [Get](./REFERENCE.md#sobjects-get), [Update](./REFERENCE.md#sobjects-update), [Delete](./REFERENCE.md#sobjects-delete) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Create](./REFERENCE.md#accounts-create), [Get](./REFERENCE.md#accounts-get), [Update](./REFERENCE.md#accounts-update), [Delete](./REFERENCE.md#accounts-delete), [API Search](./REFERENCE.md#accounts-api_search), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Contacts | [List](./REFERENCE.md#contacts-list), [Create](./REFERENCE.md#contacts-create), [Get](./REFERENCE.md#contacts-get), [Update](./REFERENCE.md#contacts-update), [Delete](./REFERENCE.md#contacts-delete), [API Search](./REFERENCE.md#contacts-api_search), [Context Store Search](./REFERENCE.md#contacts-context-store-search) |
| Leads | [List](./REFERENCE.md#leads-list), [Create](./REFERENCE.md#leads-create), [Get](./REFERENCE.md#leads-get), [Update](./REFERENCE.md#leads-update), [Delete](./REFERENCE.md#leads-delete), [API Search](./REFERENCE.md#leads-api_search), [Context Store Search](./REFERENCE.md#leads-context-store-search) |
| Opportunities | [List](./REFERENCE.md#opportunities-list), [Create](./REFERENCE.md#opportunities-create), [Get](./REFERENCE.md#opportunities-get), [Update](./REFERENCE.md#opportunities-update), [Delete](./REFERENCE.md#opportunities-delete), [API Search](./REFERENCE.md#opportunities-api_search), [Context Store Search](./REFERENCE.md#opportunities-context-store-search) |
| Tasks | [List](./REFERENCE.md#tasks-list), [Create](./REFERENCE.md#tasks-create), [Get](./REFERENCE.md#tasks-get), [Update](./REFERENCE.md#tasks-update), [Delete](./REFERENCE.md#tasks-delete), [API Search](./REFERENCE.md#tasks-api_search), [Context Store Search](./REFERENCE.md#tasks-context-store-search) |
| Events | [List](./REFERENCE.md#events-list), [Create](./REFERENCE.md#events-create), [Get](./REFERENCE.md#events-get), [Update](./REFERENCE.md#events-update), [Delete](./REFERENCE.md#events-delete), [API Search](./REFERENCE.md#events-api_search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Create](./REFERENCE.md#campaigns-create), [Get](./REFERENCE.md#campaigns-get), [Update](./REFERENCE.md#campaigns-update), [Delete](./REFERENCE.md#campaigns-delete), [API Search](./REFERENCE.md#campaigns-api_search) |
| Cases | [List](./REFERENCE.md#cases-list), [Create](./REFERENCE.md#cases-create), [Get](./REFERENCE.md#cases-get), [Update](./REFERENCE.md#cases-update), [Delete](./REFERENCE.md#cases-delete), [API Search](./REFERENCE.md#cases-api_search) |
| Notes | [List](./REFERENCE.md#notes-list), [Create](./REFERENCE.md#notes-create), [Get](./REFERENCE.md#notes-get), [Update](./REFERENCE.md#notes-update), [Delete](./REFERENCE.md#notes-delete), [API Search](./REFERENCE.md#notes-api_search) |
| Content Versions | [List](./REFERENCE.md#content-versions-list), [Get](./REFERENCE.md#content-versions-get), [Download](./REFERENCE.md#content-versions-download) |
| Attachments | [List](./REFERENCE.md#attachments-list), [Get](./REFERENCE.md#attachments-get), [Download](./REFERENCE.md#attachments-download) |
| Reports | [List](./REFERENCE.md#reports-list), [Get](./REFERENCE.md#reports-get) |
| Users | [List](./REFERENCE.md#users-list), [Create](./REFERENCE.md#users-create), [Get](./REFERENCE.md#users-get), [Update](./REFERENCE.md#users-update), [Context Store Search](./REFERENCE.md#users-context-store-search) |
| Opportunity Stages | [List](./REFERENCE.md#opportunity-stages-list), [Get](./REFERENCE.md#opportunity-stages-get), [Context Store Search](./REFERENCE.md#opportunity-stages-context-store-search) |
| Query | [List](./REFERENCE.md#query-list) |


## Salesforce API docs

See the official [Salesforce API reference](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm).

## Interfaces

Use the Salesforce connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "salesforce"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "salesforce",
  "entity": "sobjects",
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

The `connect()` factory returns a fully typed `SalesforceConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

@tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SalesforceConnector.tool_utils(framework="openai_agents")
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Salesforce Assistant", tools=[salesforce_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector

connector = connect("salesforce", workspace_name="<your_workspace_name>")

mcp = FastMCP("Salesforce Agent")

@mcp.tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
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

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
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
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
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

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SalesforceConnector.tool_utils(framework="openai_agents")
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Salesforce Assistant", tools=[salesforce_execute])
```

**FastMCP**

```python title="FastMCP"
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

@mcp.tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

##### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.connectors.salesforce.models import SalesforceAuthConfig

connector = SalesforceConnector(
    auth_config=SalesforceAuthConfig(
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
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
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.salesforce import SalesforceConnector
from airbyte_agent_sdk.connectors.salesforce.models import SalesforceAuthConfig

connector = SalesforceConnector(
    auth_config=SalesforceAuthConfig(
        refresh_token="<OAuth refresh token for automatic token renewal>",
        client_id="<Connected App Consumer Key>",
        client_secret="<Connected App Consumer Secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@SalesforceConnector.tool_utils(framework="openai_agents")
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Salesforce Assistant", tools=[salesforce_execute])
```

**FastMCP**

```python title="FastMCP"
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

@mcp.tool
@SalesforceConnector.tool_utils
async def salesforce_execute(entity: str, action: str, params: dict | None = None):
    """Execute Salesforce connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.2.0