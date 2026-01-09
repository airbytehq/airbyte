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

```python
from airbyte_agent_intercom import IntercomConnector, IntercomAuthConfig

connector = IntercomConnector(
  auth_config=IntercomAuthConfig(
    access_token="..."
  )
)
result = await connector.contacts.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](./REFERENCE.md#contacts-list), [Get](./REFERENCE.md#contacts-get) |
| Conversations | [List](./REFERENCE.md#conversations-list), [Get](./REFERENCE.md#conversations-get) |
| Companies | [List](./REFERENCE.md#companies-list), [Get](./REFERENCE.md#companies-get) |
| Teams | [List](./REFERENCE.md#teams-list), [Get](./REFERENCE.md#teams-get) |
| Admins | [List](./REFERENCE.md#admins-list), [Get](./REFERENCE.md#admins-get) |
| Tags | [List](./REFERENCE.md#tags-list), [Get](./REFERENCE.md#tags-get) |
| Segments | [List](./REFERENCE.md#segments-list), [Get](./REFERENCE.md#segments-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Intercom API reference](https://developers.intercom.com/docs/references/rest-api/api.intercom.io).

## Version information

- **Package version:** 0.1.0
- **Connector version:** 0.1.1
- **Generated with Connector SDK commit SHA:** 463eef2ee0e9c32a4495aebeb757f2ed42ddb56e