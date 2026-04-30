# Tiktok-Marketing

The Tiktok-Marketing agent connector is a Python package that equips AI agents to interact with Tiktok-Marketing through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the TikTok Marketing API (Business API v1.3). Provides access to advertiser accounts, campaigns, ad groups, ads, audiences, creative assets (images and videos), and daily performance reports at the advertiser, campaign, ad group, and ad levels. Requires an Access Token from the TikTok for Business platform. All list operations require an advertiser_id parameter to scope results to a specific advertiser account.

## Example questions

The Tiktok-Marketing connector is optimized to handle prompts like these.

- List all my TikTok advertisers
- Show me all campaigns for my advertiser account
- List all ad groups
- Show me all ads
- List my custom audiences
- Show me all creative asset images
- List creative asset videos
- Show me daily ad performance reports
- Get campaign performance metrics for the last 30 days
- Show me advertiser spend reports
- Which campaigns have the highest budget?
- Find all paused ad groups
- What ads were created last month?
- Show campaigns with lifetime budget mode
- Which ads had the most impressions yesterday?
- What is my total ad spend this month?
- Which campaigns have the highest click-through rate?

## Unsupported questions

The Tiktok-Marketing connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update ad group targeting
- Delete an ad

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
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

@agent.tool_plain
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

@tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.connectors.tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

mcp = FastMCP("Tiktok-Marketing Agent")

@mcp.tool()
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `TiktokMarketingConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

@agent.tool_plain
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

@tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector

connector = connect("tiktok-marketing", workspace_name="<your_workspace_name>")

mcp = FastMCP("Tiktok-Marketing Agent")

@mcp.tool()
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TiktokMarketingConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Tiktok-Marketing Agent")

@mcp.tool()
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Tiktok-Marketing connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Advertisers | [List](./REFERENCE.md#advertisers-list), [Context Store Search](./REFERENCE.md#advertisers-context-store-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Context Store Search](./REFERENCE.md#campaigns-context-store-search) |
| Ad Groups | [List](./REFERENCE.md#ad-groups-list), [Context Store Search](./REFERENCE.md#ad-groups-context-store-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Context Store Search](./REFERENCE.md#ads-context-store-search) |
| Audiences | [List](./REFERENCE.md#audiences-list), [Context Store Search](./REFERENCE.md#audiences-context-store-search) |
| Creative Assets Images | [List](./REFERENCE.md#creative-assets-images-list), [Context Store Search](./REFERENCE.md#creative-assets-images-context-store-search) |
| Creative Assets Videos | [List](./REFERENCE.md#creative-assets-videos-list), [Context Store Search](./REFERENCE.md#creative-assets-videos-context-store-search) |
| Advertisers Reports Daily | [List](./REFERENCE.md#advertisers-reports-daily-list), [Context Store Search](./REFERENCE.md#advertisers-reports-daily-context-store-search) |
| Campaigns Reports Daily | [List](./REFERENCE.md#campaigns-reports-daily-list), [Context Store Search](./REFERENCE.md#campaigns-reports-daily-context-store-search) |
| Ad Groups Reports Daily | [List](./REFERENCE.md#ad-groups-reports-daily-list), [Context Store Search](./REFERENCE.md#ad-groups-reports-daily-context-store-search) |
| Ads Reports Daily | [List](./REFERENCE.md#ads-reports-daily-list), [Context Store Search](./REFERENCE.md#ads-reports-daily-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Tiktok-Marketing API docs

See the official [Tiktok-Marketing API reference](https://business-api.tiktok.com/portal/docs?id=1740302848670722).

## Version information

- **Package version:** 1.1.5
- **Connector version:** 1.1.5
- **Generated with Connector SDK commit SHA:** unknown