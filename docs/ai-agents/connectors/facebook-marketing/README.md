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
- Show me the ad sets with the highest daily budget
- Show me the performance insights for the last 7 days
- Which campaigns have the most spend this month?
- Show me ads with the highest click-through rate

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
| Ad Accounts | [List](./REFERENCE.md#ad-accounts-list) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get) |
| Ad Sets | [List](./REFERENCE.md#ad-sets-list), [Get](./REFERENCE.md#ad-sets-get) |
| Ads | [List](./REFERENCE.md#ads-list), [Get](./REFERENCE.md#ads-get) |
| Ad Creatives | [List](./REFERENCE.md#ad-creatives-list) |
| Ads Insights | [List](./REFERENCE.md#ads-insights-list) |
| Ad Account | [Get](./REFERENCE.md#ad-account-get) |
| Custom Conversions | [List](./REFERENCE.md#custom-conversions-list) |
| Images | [List](./REFERENCE.md#images-list) |
| Videos | [List](./REFERENCE.md#videos-list) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Facebook-Marketing API docs

See the official [Facebook-Marketing API reference](https://developers.facebook.com/docs/marketing-api/).

## Version information

- **Package version:** 0.1.26
- **Connector version:** 1.0.14
- **Generated with Connector SDK commit SHA:** cddf6b9fb41e981bb489b71675cc4a9059e55608
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/facebook-marketing/CHANGELOG.md)