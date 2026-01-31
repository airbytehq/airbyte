# Intercom agent connector

Intercom is a customer messaging platform that enables businesses to communicate with
customers through chat, email, and in-app messaging. This connector provides read-only
access to core Intercom entities including contacts, conversations, companies, teams,
admins, tags, and segments for customer support analytics and insights.


## Example questions

The Intercom connector is optimized to handle prompts like these.

- List all contacts in my Intercom workspace
- Show me conversations from the last week
- List all companies in Intercom
- What teams are configured in my workspace?
- Show me all admins in my Intercom account
- List all tags used in Intercom
- Get details for contact \{contact_id\}
- Show me all customer segments
- Get company details for \{company_id\}
- List conversations assigned to team \{team_id\}
- Show me open conversations
- Get conversation details for \{conversation_id\}

## Unsupported questions

The Intercom connector isn't currently able to handle prompts like these.

- Create a new contact in Intercom
- Send a message to a customer
- Delete a conversation
- Update company information
- Assign a conversation to an admin
- Create a new tag

## Installation

```bash
uv pip install airbyte-agent-intercom
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_intercom import IntercomConnector
from airbyte_agent_intercom.models import IntercomAuthConfig

connector = IntercomConnector(
    auth_config=IntercomAuthConfig(
        access_token="<Your Intercom API Access Token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_intercom import IntercomConnector

connector = IntercomConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@IntercomConnector.tool_utils
async def intercom_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get) |
| Conversations | [List](./REFERENCE.md#conversations-list), [Get](./REFERENCE.md#conversations-get) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |
| Admins | [List](./REFERENCE.md#admins-list), [Get](./REFERENCE.md#admins-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Intercom API docs

See the official [Intercom API reference](https://developers.intercom.com/docs/references/rest-api/api.intercom.io).

## Version information

- **Package version:** 0.1.46
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/intercom/CHANGELOG.md)