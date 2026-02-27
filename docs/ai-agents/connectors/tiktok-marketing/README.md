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
uv pip install airbyte-agent-tiktok-marketing
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_tiktok_marketing import TiktokMarketingConnector
from airbyte_agent_tiktok_marketing.models import TiktokMarketingAuthConfig

connector = TiktokMarketingConnector(
    auth_config=TiktokMarketingAuthConfig(
        access_token="<Your TikTok Marketing API access token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_tiktok_marketing import TiktokMarketingConnector, AirbyteAuthConfig

connector = TiktokMarketingConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@TiktokMarketingConnector.tool_utils
async def tiktok_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Advertisers | [List](./REFERENCE.md#advertisers-list), [Search](./REFERENCE.md#advertisers-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Search](./REFERENCE.md#campaigns-search) |
| Ad Groups | [List](./REFERENCE.md#ad-groups-list), [Search](./REFERENCE.md#ad-groups-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Search](./REFERENCE.md#ads-search) |
| Audiences | [List](./REFERENCE.md#audiences-list), [Search](./REFERENCE.md#audiences-search) |
| Creative Assets Images | [List](./REFERENCE.md#creative-assets-images-list), [Search](./REFERENCE.md#creative-assets-images-search) |
| Creative Assets Videos | [List](./REFERENCE.md#creative-assets-videos-list), [Search](./REFERENCE.md#creative-assets-videos-search) |
| Advertisers Reports Daily | [List](./REFERENCE.md#advertisers-reports-daily-list), [Search](./REFERENCE.md#advertisers-reports-daily-search) |
| Campaigns Reports Daily | [List](./REFERENCE.md#campaigns-reports-daily-list), [Search](./REFERENCE.md#campaigns-reports-daily-search) |
| Ad Groups Reports Daily | [List](./REFERENCE.md#ad-groups-reports-daily-list), [Search](./REFERENCE.md#ad-groups-reports-daily-search) |
| Ads Reports Daily | [List](./REFERENCE.md#ads-reports-daily-list), [Search](./REFERENCE.md#ads-reports-daily-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Tiktok-Marketing API docs

See the official [Tiktok-Marketing API reference](https://business-api.tiktok.com/portal/docs?id=1740302848670722).

## Version information

- **Package version:** 0.1.11
- **Connector version:** 1.1.2
- **Generated with Connector SDK commit SHA:** a735c402798904c84a7f4df7969653341d95b11d
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/tiktok-marketing/CHANGELOG.md)