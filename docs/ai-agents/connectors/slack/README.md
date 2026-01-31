# Slack agent connector

Slack is a business communication platform that offers messaging, file sharing, and integrations
with other tools. This connector provides read access to users, channels, channel members, channel
messages, and threads for workspace analytics. It also supports write operations including sending
and updating messages, creating and renaming channels, setting channel topics and purposes, and
adding reactions to messages.


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
- Send a message to channel \{channel_id\} saying 'Hello team!'
- Post a message in the general channel
- Update the message with timestamp \{ts\} in channel \{channel_id\}
- Create a new public channel called 'project-updates'
- Create a private channel named 'team-internal'
- Rename channel \{channel_id\} to 'new-channel-name'
- Set the topic for channel \{channel_id\} to 'Daily standup notes'
- Update the purpose of channel \{channel_id\}
- Add a thumbsup reaction to message \{ts\} in channel \{channel_id\}
- React with :rocket: to the latest message in channel \{channel_id\}
- Reply to thread \{ts\} in channel \{channel_id\} with 'Thanks for the update!'

## Unsupported questions

The Slack connector isn't currently able to handle prompts like these.

- Delete a message from channel \{channel_id\}
- Remove a reaction from a message
- Archive channel \{channel_id\}
- Invite user \{user_id\} to channel \{channel_id\}
- Remove user \{user_id\} from channel \{channel_id\}
- Delete channel \{channel_id\}
- Create a new user in the workspace
- Update user profile information

## Installation

```bash
uv pip install airbyte-agent-slack
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_slack import SlackConnector
from airbyte_agent_slack.models import SlackTokenAuthenticationAuthConfig

connector = SlackConnector(
    auth_config=SlackTokenAuthenticationAuthConfig(
        api_token="<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_slack import SlackConnector

connector = SlackConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Users | [List](./REFERENCE.md#users-list), [Get](./REFERENCE.md#users-get) |
| Channels | [List](./REFERENCE.md#channels-list), [Get](./REFERENCE.md#channels-get), [Create](./REFERENCE.md#channels-create), [Update](./REFERENCE.md#channels-update) |
| Channel Messages | [List](./REFERENCE.md#channel-messages-list) |
| Threads | [List](./REFERENCE.md#threads-list) |
| Messages | [Create](./REFERENCE.md#messages-create), [Update](./REFERENCE.md#messages-update) |
| Channel Topics | [Create](./REFERENCE.md#channel-topics-create) |
| Channel Purposes | [Create](./REFERENCE.md#channel-purposes-create) |
| Reactions | [Create](./REFERENCE.md#reactions-create) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Slack API docs

See the official [Slack API reference](https://api.slack.com/methods).

## Version information

- **Package version:** 0.1.39
- **Connector version:** 0.1.12
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/slack/CHANGELOG.md)