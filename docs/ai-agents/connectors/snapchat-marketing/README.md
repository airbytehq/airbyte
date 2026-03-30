# Snapchat-Marketing

The Snapchat-Marketing agent connector is a Python package that equips AI agents to interact with Snapchat-Marketing through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Snapchat Marketing API (Ads API). Provides access to Snapchat advertising entities including organizations, ad accounts, campaigns, ad squads, ads, creatives, media, and audience segments. Supports OAuth2 authentication with automatic token refresh.


## Example questions

The Snapchat-Marketing connector is optimized to handle prompts like these.

- List all organizations I belong to
- Show me all ad accounts for my organization
- List all campaigns in my ad account
- Show me the ad squads for my ad account
- List all ads in my ad account
- Show me the creatives for my ad account
- List all media files in my ad account
- Show me the audience segments in my ad account
- Which campaigns are currently active?
- What ad squads have the highest daily budget?
- Show me ads that are pending review
- Find campaigns created in the last month

## Unsupported questions

The Snapchat-Marketing connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update an ad's status
- Delete a creative
- Show me ad performance statistics

## Installation

```bash
uv pip install airbyte-agent-snapchat-marketing
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_snapchat_marketing import SnapchatMarketingConnector
from airbyte_agent_snapchat_marketing.models import SnapchatMarketingAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=SnapchatMarketingAuthConfig(
        client_id="<The Client ID of your Snapchat developer application>",
        client_secret="<The Client Secret of your Snapchat developer application>",
        refresh_token="<Refresh Token to renew the expired Access Token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_snapchat_marketing import SnapchatMarketingConnector, AirbyteAuthConfig

connector = SnapchatMarketingConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SnapchatMarketingConnector.tool_utils
async def snapchat_marketing_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Organizations | [List](./REFERENCE.md#organizations-list), [Get](./REFERENCE.md#organizations-get), [Search](./REFERENCE.md#organizations-search) |
| Adaccounts | [List](./REFERENCE.md#adaccounts-list), [Get](./REFERENCE.md#adaccounts-get), [Search](./REFERENCE.md#adaccounts-search) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get), [Search](./REFERENCE.md#campaigns-search) |
| Adsquads | [List](./REFERENCE.md#adsquads-list), [Get](./REFERENCE.md#adsquads-get), [Search](./REFERENCE.md#adsquads-search) |
| Ads | [List](./REFERENCE.md#ads-list), [Get](./REFERENCE.md#ads-get), [Search](./REFERENCE.md#ads-search) |
| Creatives | [List](./REFERENCE.md#creatives-list), [Get](./REFERENCE.md#creatives-get), [Search](./REFERENCE.md#creatives-search) |
| Media | [List](./REFERENCE.md#media-list), [Get](./REFERENCE.md#media-get), [Search](./REFERENCE.md#media-search) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get), [Search](./REFERENCE.md#segments-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Snapchat-Marketing API docs

See the official [Snapchat-Marketing API reference](https://developers.snap.com/api/marketing-api/Ads-API/introduction).

## Version information

- **Package version:** 0.1.8
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/snapchat-marketing/CHANGELOG.md)