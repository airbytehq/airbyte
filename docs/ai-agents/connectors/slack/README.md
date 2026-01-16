# Slack agent connector

Slack is a business communication platform that offers messaging, file sharing, and integrations
with other tools. This connector provides access to users, channels, channel members, channel
messages, and threads for workspace analytics and communication insights.


## Example questions

The Slack connector is optimized to handle prompts like these.

- List all users in my Slack workspace
- Show me all public channels
- Who are the members of channel \{channel_id\}?
- Get messages from channel \{channel_id\}
- Show me the thread replies for message \{ts\} in channel \{channel_id\}
- List all channels I have access to
- Get user details for user \{user_id\}
- What messages were posted in channel \{channel_id\} last week?
- Show me the conversation history for channel \{channel_id\}
- List channel members for the general channel

## Unsupported questions

The Slack connector isn't currently able to handle prompts like these.

- Create a new channel
- Delete a message
- Send a message to a channel
- Update a channel topic
- Invite a user to a channel
- Archive a channel

## Installation

```bash
uv pip install airbyte-agent-slack
```

## Usage

This connector supports multiple authentication methods:

### Token Authentication

```python
from airbyte_agent_slack import SlackConnector
from airbyte_agent_slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
  auth_config=SlackTokenAuthenticationAuthConfig(
    access_token="..."
  )
)
result = await connector.users.list()
```

### OAuth 2.0 Authentication

```python
from airbyte_agent_slack import SlackConnector
from airbyte_agent_slack.models import SlackOauth20AuthenticationAuthConfig

connector = SlackConnector(
  auth_config=SlackOauth20AuthenticationAuthConfig(
    client_id="...",
    client_secret="...",
    access_token="..."
  )
)
result = await connector.users.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Channels | [List](./REFERENCE.md#channels-list), [Get](./REFERENCE.md#channels-get) |
| Channel Messages | [List](./REFERENCE.md#channel-messages-list) |
| Threads | [List](./REFERENCE.md#threads-list) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Slack API reference](https://api.slack.com/methods).

## Version information

- **Package version:** 0.1.4
- **Connector version:** 0.1.1
- **Generated with Connector SDK commit SHA:** ca5acdda8030d8292c059c82f498a95b2227c106