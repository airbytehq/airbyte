# Google-Ads

The Google-Ads agent connector is a Python package that equips AI agents to interact with Google-Ads through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Google Ads API connector for accessing advertising account data including campaigns, ad groups, ads, and labels. This connector uses the Google Ads Query Language (GAQL) via the REST search endpoint to retrieve structured advertising data. Requires OAuth2 credentials and a Google Ads developer token for authentication. All data retrieval is read-only.

## Example questions

The Google-Ads connector is optimized to handle prompts like these.

- List all accessible Google Ads customer accounts
- Show me all campaigns and their statuses
- List all ad groups across my campaigns
- What ads are running in my ad groups?
- Show me campaign labels
- List all ad group labels
- What labels are applied to my ads?
- Pause campaign 'Summer Sale 2025'
- Enable the ad group 'Brand Keywords'
- Create a label called 'High Priority'
- Apply the 'Q4 Campaigns' label to my search campaign
- Update the name of campaign 123456 to 'Winter Promo'
- Which campaigns have the highest cost this month?
- Show me all paused campaigns
- Find ad groups with the most impressions
- What are my top performing ads by click-through rate?
- Show campaigns with budget over $100 per day

## Unsupported questions

The Google-Ads connector isn't currently able to handle prompts like these.

- Create a new campaign
- Delete an ad
- Delete a campaign
- Delete a label

## Installation

```bash
uv pip install airbyte-agent-google-ads
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_google_ads import GoogleAdsConnector
from airbyte_agent_google_ads.models import GoogleAdsAuthConfig

connector = GoogleAdsConnector(
    auth_config=GoogleAdsAuthConfig(
        client_id="<OAuth2 client ID from Google Cloud Console>",
        client_secret="<OAuth2 client secret from Google Cloud Console>",
        refresh_token="<OAuth2 refresh token>",
        developer_token="<Google Ads API developer token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleAdsConnector.tool_utils
async def google_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_google_ads import GoogleAdsConnector, AirbyteAuthConfig

connector = GoogleAdsConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleAdsConnector.tool_utils
async def google_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accessible Customers | [List](./REFERENCE.md#accessible-customers-list) |
| Accounts | [List](./REFERENCE.md#accounts-list), [Search](./REFERENCE.md#accounts-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Update](./REFERENCE.md#campaigns-update), [Search](./REFERENCE.md#campaigns-search) |
| Ad Groups | [List](./REFERENCE.md#ad-groups-list), [Update](./REFERENCE.md#ad-groups-update), [Search](./REFERENCE.md#ad-groups-search) |
| Ad Group Ads | [List](./REFERENCE.md#ad-group-ads-list), [Search](./REFERENCE.md#ad-group-ads-search) |
| Campaign Labels | [List](./REFERENCE.md#campaign-labels-list), [Create](./REFERENCE.md#campaign-labels-create), [Search](./REFERENCE.md#campaign-labels-search) |
| Ad Group Labels | [List](./REFERENCE.md#ad-group-labels-list), [Create](./REFERENCE.md#ad-group-labels-create), [Search](./REFERENCE.md#ad-group-labels-search) |
| Ad Group Ad Labels | [List](./REFERENCE.md#ad-group-ad-labels-list), [Search](./REFERENCE.md#ad-group-ad-labels-search) |
| Labels | [Create](./REFERENCE.md#labels-create) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Google-Ads API docs

See the official [Google-Ads API reference](https://developers.google.com/google-ads/api/rest/reference/rest).

## Version information

- **Package version:** 0.1.4
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 7bd29cadd2220a5f26191e78acd5832fac497c81
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/google-ads/CHANGELOG.md)