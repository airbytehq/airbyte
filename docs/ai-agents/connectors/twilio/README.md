# Twilio

The Twilio agent connector is a Python package that equips AI agents to interact with Twilio through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Twilio REST API. Provides read access to core Twilio resources including accounts, calls, messages, recordings, conferences, incoming phone numbers, usage records, addresses, queues, transcriptions, and outgoing caller IDs. Uses HTTP Basic authentication with Account SID and Auth Token.


## Example questions

The Twilio connector is optimized to handle prompts like these.

- List all calls from the last 7 days
- Show me recent inbound SMS messages
- List all active phone numbers on my account
- Show me details for a specific call
- List all recordings
- Show me conference calls
- List usage records for my account
- Show me all queues
- List outgoing caller IDs
- Show me addresses on my account
- List transcriptions
- What are my top 10 most expensive calls this month?
- How many SMS messages did I send vs receive in the last 30 days?
- Summarize my usage costs by category
- Which phone numbers have the most incoming calls?
- Show me all failed messages and their error codes
- What is the average call duration for outbound calls?

## Unsupported questions

The Twilio connector isn't currently able to handle prompts like these.

- Send a new SMS message
- Make a phone call
- Purchase a new phone number
- Delete a recording
- Create a new queue

## Installation

```bash
uv pip install airbyte-agent-twilio
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_twilio import TwilioConnector
from airbyte_agent_twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_twilio import TwilioConnector, AirbyteAuthConfig

connector = TwilioConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Search](./REFERENCE.md#accounts-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Get](./REFERENCE.md#calls-get), [Search](./REFERENCE.md#calls-search) |
| Messages | [List](./REFERENCE.md#messages-list), [Get](./REFERENCE.md#messages-get), [Search](./REFERENCE.md#messages-search) |
| Incoming Phone Numbers | [List](./REFERENCE.md#incoming-phone-numbers-list), [Get](./REFERENCE.md#incoming-phone-numbers-get), [Search](./REFERENCE.md#incoming-phone-numbers-search) |
| Recordings | [List](./REFERENCE.md#recordings-list), [Get](./REFERENCE.md#recordings-get), [Search](./REFERENCE.md#recordings-search) |
| Conferences | [List](./REFERENCE.md#conferences-list), [Get](./REFERENCE.md#conferences-get), [Search](./REFERENCE.md#conferences-search) |
| Usage Records | [List](./REFERENCE.md#usage-records-list), [Search](./REFERENCE.md#usage-records-search) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Search](./REFERENCE.md#addresses-search) |
| Queues | [List](./REFERENCE.md#queues-list), [Get](./REFERENCE.md#queues-get), [Search](./REFERENCE.md#queues-search) |
| Transcriptions | [List](./REFERENCE.md#transcriptions-list), [Get](./REFERENCE.md#transcriptions-get), [Search](./REFERENCE.md#transcriptions-search) |
| Outgoing Caller Ids | [List](./REFERENCE.md#outgoing-caller-ids-list), [Get](./REFERENCE.md#outgoing-caller-ids-get), [Search](./REFERENCE.md#outgoing-caller-ids-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Twilio API docs

See the official [Twilio API reference](https://www.twilio.com/docs/usage/api).

## Version information

- **Package version:** 0.1.9
- **Connector version:** 1.0.2
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/twilio/CHANGELOG.md)