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
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector
from airbyte_agent_sdk.connectors.zendesk_talk.models import ZendeskTalkApiTokenAuthConfig

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
from airbyte_agent_sdk.connectors.zendesk_talk import ZendeskTalkConnector, AirbyteAuthConfig

connector = ZendeskTalkConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
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
| Phone Numbers | [List](./REFERENCE.md#phone-numbers-list), [Get](./REFERENCE.md#phone-numbers-get), [Context Store Search](./REFERENCE.md#phone-numbers-context-store-search) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Context Store Search](./REFERENCE.md#addresses-context-store-search) |
| Greetings | [List](./REFERENCE.md#greetings-list), [Get](./REFERENCE.md#greetings-get), [Context Store Search](./REFERENCE.md#greetings-context-store-search) |
| Greeting Categories | [List](./REFERENCE.md#greeting-categories-list), [Get](./REFERENCE.md#greeting-categories-get), [Context Store Search](./REFERENCE.md#greeting-categories-context-store-search) |
| Ivrs | [List](./REFERENCE.md#ivrs-list), [Get](./REFERENCE.md#ivrs-get), [Context Store Search](./REFERENCE.md#ivrs-context-store-search) |
| Agents Activity | [List](./REFERENCE.md#agents-activity-list), [Context Store Search](./REFERENCE.md#agents-activity-context-store-search) |
| Agents Overview | [List](./REFERENCE.md#agents-overview-list), [Context Store Search](./REFERENCE.md#agents-overview-context-store-search) |
| Account Overview | [List](./REFERENCE.md#account-overview-list), [Context Store Search](./REFERENCE.md#account-overview-context-store-search) |
| Current Queue Activity | [List](./REFERENCE.md#current-queue-activity-list), [Context Store Search](./REFERENCE.md#current-queue-activity-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Call Legs | [List](./REFERENCE.md#call-legs-list), [Context Store Search](./REFERENCE.md#call-legs-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Zendesk-Talk API docs

See the official [Zendesk-Talk API reference](https://developer.zendesk.com/api-reference/voice/talk-api/introduction/).

## Version information

- **Package version:** 1.0.2
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** unknown