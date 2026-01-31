# Klaviyo agent connector

Klaviyo is a marketing automation platform that helps businesses build customer relationships
through personalized email, SMS, and push notifications. This connector provides access to
Klaviyo's core entities including profiles, lists, campaigns, events, metrics, flows, and
email templates for marketing analytics and customer engagement insights.


## Example questions

The Klaviyo connector is optimized to handle prompts like these.

- List all profiles in my Klaviyo account
- Get profile details for a specific contact
- Show me all email lists
- Get details for a specific email list
- What campaigns have been created?
- Get details for a specific campaign
- Show me all email campaigns
- List all events for tracking customer actions
- Show me all metrics (event types)
- Get details for a specific metric
- What automated flows are configured?
- Get details for a specific flow
- List all email templates
- Get details for a specific email template

## Unsupported questions

The Klaviyo connector isn't currently able to handle prompts like these.

- Create a new profile
- Update a profile's email address
- Delete a list
- Send an email campaign
- Add a profile to a list

## Installation

```bash
uv pip install airbyte-agent-klaviyo
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_klaviyo import KlaviyoConnector
from airbyte_agent_klaviyo.models import KlaviyoAuthConfig

connector = KlaviyoConnector(
    auth_config=KlaviyoAuthConfig(
        api_key="<Your Klaviyo private API key>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_klaviyo import KlaviyoConnector

connector = KlaviyoConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@KlaviyoConnector.tool_utils
async def klaviyo_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Profiles | [List](./REFERENCE.md#profiles-list), [Get](./REFERENCE.md#profiles-get) |
| Lists | [List](./REFERENCE.md#lists-list), [Get](./REFERENCE.md#lists-get) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Get](./REFERENCE.md#campaigns-get) |
| Events | [List](./REFERENCE.md#events-list) |
| Metrics | [List](./REFERENCE.md#metrics-list), [Get](./REFERENCE.md#metrics-get) |
| Flows | [List](./REFERENCE.md#flows-list), [Get](./REFERENCE.md#flows-get) |
| Email Templates | [List](./REFERENCE.md#email-templates-list), [Get](./REFERENCE.md#email-templates-get) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Klaviyo API docs

See the official [Klaviyo API reference](https://developers.klaviyo.com/en/reference/api_overview).

## Version information

- **Package version:** 0.1.3
- **Connector version:** 1.0.0
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/klaviyo/CHANGELOG.md)