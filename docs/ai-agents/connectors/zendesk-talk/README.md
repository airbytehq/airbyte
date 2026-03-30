# Zendesk-Talk

The Zendesk-Talk agent connector is a Python package that equips AI agents to interact with Zendesk-Talk through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Zendesk Talk (Voice) API. Provides access to phone numbers,
addresses, greetings, IVR configurations, call data, and agent/account statistics
for Zendesk Talk voice support channels.


## Example questions

The Zendesk-Talk connector is optimized to handle prompts like these.

- List all phone numbers in our Zendesk Talk account
- Show all addresses on file
- List all IVR configurations
- Show all greetings
- List greeting categories
- Show agent activity statistics
- Show the account overview stats
- Show current queue activity
- Which phone numbers have SMS enabled?
- Find agents who have missed the most calls today
- What is the average call duration across all calls?
- Which phone numbers are toll-free?

## Unsupported questions

The Zendesk-Talk connector isn't currently able to handle prompts like these.

- Create a new phone number
- Delete an IVR configuration
- Update a greeting
- Make an outbound call

## Installation

```bash
uv pip install airbyte-agent-zendesk-talk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_zendesk_talk import ZendeskTalkConnector
from airbyte_agent_zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

connector = ZendeskTalkConnector(
    auth_config=ZendeskTalkApiTokenAuthConfig(
        email="<Your Zendesk account email address>",
        api_token="<Your Zendesk API token from Admin Center>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_zendesk_talk import ZendeskTalkConnector, AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskTalkConnector.tool_utils
async def zendesk_talk_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Phone Numbers | [List](./REFERENCE.md#phone-numbers-list), [Get](./REFERENCE.md#phone-numbers-get), [Search](./REFERENCE.md#phone-numbers-search) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Search](./REFERENCE.md#addresses-search) |
| Greetings | [List](./REFERENCE.md#greetings-list), [Get](./REFERENCE.md#greetings-get), [Search](./REFERENCE.md#greetings-search) |
| Greeting Categories | [List](./REFERENCE.md#greeting-categories-list), [Get](./REFERENCE.md#greeting-categories-get), [Search](./REFERENCE.md#greeting-categories-search) |
| Ivrs | [List](./REFERENCE.md#ivrs-list), [Get](./REFERENCE.md#ivrs-get), [Search](./REFERENCE.md#ivrs-search) |
| Agents Activity | [List](./REFERENCE.md#agents-activity-list), [Search](./REFERENCE.md#agents-activity-search) |
| Agents Overview | [List](./REFERENCE.md#agents-overview-list), [Search](./REFERENCE.md#agents-overview-search) |
| Account Overview | [List](./REFERENCE.md#account-overview-list), [Search](./REFERENCE.md#account-overview-search) |
| Current Queue Activity | [List](./REFERENCE.md#current-queue-activity-list), [Search](./REFERENCE.md#current-queue-activity-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Search](./REFERENCE.md#calls-search) |
| Call Legs | [List](./REFERENCE.md#call-legs-list), [Search](./REFERENCE.md#call-legs-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Zendesk-Talk API docs

See the official [Zendesk-Talk API reference](https://developer.zendesk.com/api-reference/voice/talk-api/introduction/).

## Version information

- **Package version:** 0.1.8
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** 75f388847745be753ab20224c66697e1d4a84347
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/zendesk-talk/CHANGELOG.md)