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
- List members of a public channel
- Show me recent messages in a public channel
- Show me thread replies for a recent message
- List all channels I have access to
- Show me user details for a workspace member
- List channel members for a public channel
- Send a message to a channel saying 'Hello team!'
- Post a message in the general channel
- Update the most recent message in a channel
- Create a new public channel called 'project-updates'
- Create a private channel named 'team-internal'
- Rename a channel to 'new-channel-name'
- Set the topic for a channel to 'Daily standup notes'
- Update the purpose of a channel
- Add a thumbsup reaction to the latest message in a channel
- React with :rocket: to the latest message in a channel
- Reply to a recent thread with 'Thanks for the update!'
- What messages were posted in channel \{channel_id\} last week?
- Show me the conversation history for channel \{channel_id\}
- Search for messages mentioning \{keyword\} in channel \{channel_id\}

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
from airbyte_agent_slack import SlackConnector, AirbyteAuthConfig

connector = SlackConnector(
    auth_config=AirbyteAuthConfig(
        external_user_id="<your_external_user_id>",
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
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

- **Package version:** 0.1.57
- **Connector version:** 0.1.14
- **Generated with Connector SDK commit SHA:** e4f3b9c8a8118bfaa9d57578c64868c91cb9b3a4
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/slack/CHANGELOG.md)