# Facebook-Marketing agent connector

Facebook Marketing API connector for managing ad campaigns, ad sets, ads, creatives,
and accessing performance insights. This connector provides read access to Facebook
Ads Manager data for analytics and reporting purposes.


## Example questions

The Facebook-Marketing connector is optimized to handle prompts like these.

- List all active campaigns in my ad account
- Show me the ad sets with the highest daily budget
- What ads are currently running in campaign \{campaign_name\}?
- Show me the performance insights for the last 7 days
- Which campaigns have the most spend this month?
- List all ad creatives in my account
- What is the status of my campaigns?
- Show me ads with the highest click-through rate
- List all custom conversion events in my account
- Show me all ad images in my account
- What videos are available in my ad account?

## Unsupported questions

The Facebook-Marketing connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update the budget for this ad set
- Pause all ads in this campaign
- Delete this ad creative

## Installation

```bash
uv pip install airbyte-agent-facebook-marketing
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_facebook-marketing import FacebookMarketingConnector
from airbyte_agent_facebook_marketing.models import FacebookMarketingAuthConfig

connector = FacebookMarketingConnector(
    auth_config=FacebookMarketingAuthConfig(
        access_token="<Facebook OAuth2 Access Token>",
        client_id="<Facebook App Client ID>",
        client_secret="<Facebook App Client Secret>",
        account_id="<Facebook Ad Account ID (without act_ prefix)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@FacebookMarketingConnector.tool_utils
async def facebook-marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_facebook-marketing import FacebookMarketingConnector

connector = FacebookMarketingConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@FacebookMarketingConnector.tool_utils
async def facebook-marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get) |
| Ad Sets | [List](./REFERENCE.md#ad-sets-list), [Get](./REFERENCE.md#ad-sets-get) |
| Ads | [List](./REFERENCE.md#ads-list), [Get](./REFERENCE.md#ads-get) |
| Ad Creatives | [List](./REFERENCE.md#ad-creatives-list) |
| Ads Insights | [List](./REFERENCE.md#ads-insights-list) |
| Custom Conversions | [List](./REFERENCE.md#custom-conversions-list) |
| Images | [List](./REFERENCE.md#images-list) |
| Videos | [List](./REFERENCE.md#videos-list) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Facebook-Marketing API docs

See the official [Facebook-Marketing API reference](https://developers.facebook.com/docs/marketing-api/).

## Version information

- **Package version:** 0.1.5
- **Connector version:** 1.0.3
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/facebook-marketing/CHANGELOG.md)