# Linkedin-Ads

The Linkedin-Ads agent connector is a Python package that equips AI agents to interact with Linkedin-Ads through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the LinkedIn Ads Marketing API. Provides access to ad accounts, campaigns, campaign groups, creatives, conversions, and ad analytics data. Supports OAuth 2.0 and direct access token authentication. Use this connector to retrieve advertising performance metrics, manage campaign structures, and monitor creative assets across your LinkedIn advertising accounts.


## Example questions

The Linkedin-Ads connector is optimized to handle prompts like these.

- List all my LinkedIn ad accounts
- Show me all campaigns in my ad account
- List all campaign groups
- Show me the creatives for my campaigns
- List all conversions configured for my ad accounts
- Show me account users for my LinkedIn ads accounts
- Which campaigns have the highest click-through rate?
- What is the total ad spend across all campaigns this month?
- Show me campaigns with status ACTIVE
- Which creatives have the most impressions?
- Compare campaign performance by cost type

## Unsupported questions

The Linkedin-Ads connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update campaign budgets
- Delete an ad creative
- Pause a campaign

## Installation

```bash
uv pip install airbyte-agent-linkedin-ads
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_linkedin_ads import LinkedinAdsConnector
from airbyte_agent_linkedin_ads.models import LinkedinAdsAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAuthConfig(
        refresh_token="<OAuth 2.0 refresh token for automatic renewal>",
        client_id="<OAuth 2.0 application client ID>",
        client_secret="<OAuth 2.0 application client secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_linkedin_ads import LinkedinAdsConnector, AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Search](./REFERENCE.md#accounts-search) |
| Account Users | [List](./REFERENCE.md#account-users-list), [Search](./REFERENCE.md#account-users-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Search](./REFERENCE.md#campaigns-search) |
| Campaign Groups | [List](./REFERENCE.md#campaign-groups-list), [Get](./REFERENCE.md#campaign-groups-get), [Search](./REFERENCE.md#campaign-groups-search) |
| Creatives | [List](./REFERENCE.md#creatives-list), [Get](./REFERENCE.md#creatives-get), [Search](./REFERENCE.md#creatives-search) |
| Conversions | [List](./REFERENCE.md#conversions-list), [Get](./REFERENCE.md#conversions-get), [Search](./REFERENCE.md#conversions-search) |
| Ad Campaign Analytics | [List](./REFERENCE.md#ad-campaign-analytics-list), [Search](./REFERENCE.md#ad-campaign-analytics-search) |
| Ad Creative Analytics | [List](./REFERENCE.md#ad-creative-analytics-list), [Search](./REFERENCE.md#ad-creative-analytics-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Linkedin-Ads API docs

See the official [Linkedin-Ads API reference](https://learn.microsoft.com/en-us/linkedin/marketing/).

## Version information

- **Package version:** 0.1.9
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/linkedin-ads/CHANGELOG.md)