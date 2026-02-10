# Facebook-Marketing agent connector

Facebook Marketing API connector for managing ad campaigns, ad sets, ads, creatives,
and accessing performance insights. This connector provides read access to Facebook
Ads Manager data for analytics and reporting purposes.


## Example questions

The Facebook-Marketing connector is optimized to handle prompts like these.

- List all active campaigns in my ad account
- What ads are currently running in a recent campaign?
- List all ad creatives in my account
- What is the status of my campaigns?
- List all custom conversion events in my account
- Show me all ad images in my account
- What videos are available in my ad account?
- Create a new campaign called 'Summer Sale 2026' with traffic objective
- Pause my most recent campaign
- Create a new ad set with a $50 daily budget in my latest campaign
- Update the daily budget of my top performing ad set to $100
- Rename my most recent ad set to 'Holiday Promo'
- Create a new ad in my latest ad set
- Pause all ads in my most recent ad set
- Show me the ad sets with the highest daily budget
- Show me the performance insights for the last 7 days
- Which campaigns have the most spend this month?
- Show me ads with the highest click-through rate

## Unsupported questions

The Facebook-Marketing connector isn't currently able to handle prompts like these.

- Delete this ad creative
- Delete this campaign
- Delete this ad set
- Delete this ad

## Installation

```bash
uv pip install airbyte-agent-facebook-marketing
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_facebook_marketing import FacebookMarketingConnector
from airbyte_agent_facebook_marketing.models import FacebookMarketingServiceAccountKeyAuthenticationAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(
        account_key="<Facebook long-lived access token for Service Account authentication>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_facebook_marketing import FacebookMarketingConnector, AirbyteAuthConfig

connector = FacebookMarketingConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@FacebookMarketingConnector.tool_utils
async def facebook_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Current User | [Get](./REFERENCE.md#current-user-get) |
| Ad Accounts | [List](./REFERENCE.md#ad-accounts-list), [Search](./REFERENCE.md#ad-accounts-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Create](./REFERENCE.md#campaigns-create), [Get](./REFERENCE.md#campaigns-get), [Update](./REFERENCE.md#campaigns-update), [Search](./REFERENCE.md#campaigns-search) |
| Ad Sets | [List](./REFERENCE.md#ad-sets-list), [Create](./REFERENCE.md#ad-sets-create), [Get](./REFERENCE.md#ad-sets-get), [Update](./REFERENCE.md#ad-sets-update), [Search](./REFERENCE.md#ad-sets-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Create](./REFERENCE.md#ads-create), [Get](./REFERENCE.md#ads-get), [Update](./REFERENCE.md#ads-update), [Search](./REFERENCE.md#ads-search) |
| Ad Creatives | [List](./REFERENCE.md#ad-creatives-list), [Search](./REFERENCE.md#ad-creatives-search) |
| Ads Insights | [List](./REFERENCE.md#ads-insights-list), [Search](./REFERENCE.md#ads-insights-search) |
| Ad Account | [Get](./REFERENCE.md#ad-account-get), [Search](./REFERENCE.md#ad-account-search) |
| Custom Conversions | [List](./REFERENCE.md#custom-conversions-list), [Search](./REFERENCE.md#custom-conversions-search) |
| Images | [List](./REFERENCE.md#images-list), [Search](./REFERENCE.md#images-search) |
| Videos | [List](./REFERENCE.md#videos-list), [Search](./REFERENCE.md#videos-search) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Facebook-Marketing API docs

See the official [Facebook-Marketing API reference](https://developers.facebook.com/docs/marketing-api/).

## Version information

- **Package version:** 0.1.31
- **Connector version:** 1.0.16
- **Generated with Connector SDK commit SHA:** 450a5458564a3e578f8590134ec3a2b00b2abe88
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/facebook-marketing/CHANGELOG.md)