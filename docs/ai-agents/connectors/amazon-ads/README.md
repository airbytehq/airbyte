# Amazon-Ads

The Amazon-Ads agent connector is a Python package that equips AI agents to interact with Amazon-Ads through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Amazon Ads is Amazon's advertising platform that enables sellers and vendors to promote their
products across Amazon's marketplace. This connector provides access to advertising profiles,
portfolios, Sponsored Products campaigns (including ad groups, keywords, product ads, targets,
and negative keywords/targets), and Sponsored Brands campaigns and ad groups for managing and
analyzing advertising campaigns across different marketplaces.


## Example questions

The Amazon-Ads connector is optimized to handle prompts like these.

- List all my advertising profiles across marketplaces
- Show me the profiles for my seller accounts
- What marketplaces do I have advertising profiles in?
- List all portfolios for one of my profiles
- Show me all sponsored product campaigns
- List all ad groups in my SP campaigns
- Show me all keywords in my sponsored product campaigns
- What product ads are currently running?
- Show me all targeting clauses for my campaigns
- List negative keywords across my ad groups
- Show me all sponsored brands campaigns
- List ad groups in my sponsored brands campaigns
- What campaigns are currently enabled?
- Find campaigns with a specific targeting type
- Which ad groups have the highest default bid?
- What keywords are using broad match type?

## Unsupported questions

The Amazon-Ads connector isn't currently able to handle prompts like these.

- Create a new advertising campaign
- Update my campaign budget
- Delete an ad group
- Generate a performance report

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
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.connectors.amazon_ads.models import AmazonAdsAuthConfig

connector = AmazonAdsConnector(
    auth_config=AmazonAdsAuthConfig(
        client_id="<The client ID of your Amazon Ads API application>",
        client_secret="<The client secret of your Amazon Ads API application>",
        refresh_token="<The refresh token obtained from the OAuth authorization flow>"
    )
)

@agent.tool_plain
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.connectors.amazon_ads.models import AmazonAdsAuthConfig

connector = AmazonAdsConnector(
    auth_config=AmazonAdsAuthConfig(
        client_id="<The client ID of your Amazon Ads API application>",
        client_secret="<The client secret of your Amazon Ads API application>",
        refresh_token="<The refresh token obtained from the OAuth authorization flow>"
    )
)

@tool
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.connectors.amazon_ads.models import AmazonAdsAuthConfig

connector = AmazonAdsConnector(
    auth_config=AmazonAdsAuthConfig(
        client_id="<The client ID of your Amazon Ads API application>",
        client_secret="<The client secret of your Amazon Ads API application>",
        refresh_token="<The refresh token obtained from the OAuth authorization flow>"
    )
)

mcp = FastMCP("Amazon-Ads Agent")

@mcp.tool()
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `AmazonAdsConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

@agent.tool_plain
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

@tool
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector

connector = connect("amazon-ads", workspace_name="<your_workspace_name>")

mcp = FastMCP("Amazon-Ads Agent")

@mcp.tool()
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.amazon_ads import AmazonAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = AmazonAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Amazon-Ads Agent")

@mcp.tool()
@AmazonAdsConnector.tool_utils
async def amazon_ads_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Amazon-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Profiles | [List](./REFERENCE.md#profiles-list), [Get](./REFERENCE.md#profiles-get), [Context Store Search](./REFERENCE.md#profiles-context-store-search) |
| Portfolios | [List](./REFERENCE.md#portfolios-list), [Get](./REFERENCE.md#portfolios-get) |
| Sponsored Product Campaigns | [List](./REFERENCE.md#sponsored-product-campaigns-list), [Get](./REFERENCE.md#sponsored-product-campaigns-get) |
| Sponsored Product Ad Groups | [List](./REFERENCE.md#sponsored-product-ad-groups-list) |
| Sponsored Product Keywords | [List](./REFERENCE.md#sponsored-product-keywords-list) |
| Sponsored Product Product Ads | [List](./REFERENCE.md#sponsored-product-product-ads-list) |
| Sponsored Product Targets | [List](./REFERENCE.md#sponsored-product-targets-list) |
| Sponsored Product Negative Keywords | [List](./REFERENCE.md#sponsored-product-negative-keywords-list) |
| Sponsored Product Negative Targets | [List](./REFERENCE.md#sponsored-product-negative-targets-list) |
| Sponsored Brands Campaigns | [List](./REFERENCE.md#sponsored-brands-campaigns-list) |
| Sponsored Brands Ad Groups | [List](./REFERENCE.md#sponsored-brands-ad-groups-list) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Amazon-Ads API docs

See the official [Amazon-Ads API reference](https://advertising.amazon.com/API/docs/en-us).

## Version information

- **Package version:** 1.0.10
- **Connector version:** 1.0.10
- **Generated with Connector SDK commit SHA:** unknown