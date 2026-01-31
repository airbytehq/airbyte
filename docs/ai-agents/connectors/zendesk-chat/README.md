# Zendesk-Chat agent connector

Zendesk Chat enables real-time customer support through live chat. This connector
provides access to chat transcripts, agents, departments, shortcuts, triggers,
and other chat configuration data for analytics and support insights.

## Supported Entities
- **accounts**: Account information and billing details
- **agents**: Chat agents with roles and department assignments
- **agent_timeline**: Agent activity timeline (incremental export)
- **bans**: Banned visitors (IP and visitor-based)
- **chats**: Chat transcripts with full conversation history (incremental export)
- **departments**: Chat departments for routing
- **goals**: Conversion goals for tracking
- **roles**: Agent role definitions
- **routing_settings**: Account-level routing configuration
- **shortcuts**: Canned responses for agents
- **skills**: Agent skills for skill-based routing
- **triggers**: Automated chat triggers

## Rate Limits
Zendesk Chat API uses the `Retry-After` header for rate limit backoff.
The connector handles this automatically.


## Example questions

The Zendesk-Chat connector is optimized to handle prompts like these.

- Show me all chats from last week
- List all agents in the support department
- What are the most used chat shortcuts?
- Show chat volume by department
- List all banned visitors
- What triggers are currently active?
- Show agent activity timeline for today
- List all departments with their settings

## Unsupported questions

The Zendesk-Chat connector isn't currently able to handle prompts like these.

- Start a new chat session
- Send a message to a visitor
- Create a new agent
- Update department settings
- Delete a shortcut

## Installation

```bash
uv pip install airbyte-agent-zendesk-chat
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_zendesk-chat import ZendeskChatConnector
from airbyte_agent_zendesk_chat.models import ZendeskChatAuthConfig

connector = ZendeskChatConnector(
    auth_config=ZendeskChatAuthConfig(
        access_token="<Your Zendesk Chat OAuth 2.0 access token>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskChatConnector.tool_utils
async def zendesk-chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_zendesk-chat import ZendeskChatConnector

connector = ZendeskChatConnector(
    external_user_id="<your_external_user_id>",
    airbyte_client_id="<your-client-id>",
    airbyte_client_secret="<your-client-secret>"
)

@agent.tool_plain # assumes you're using Pydantic AI
@ZendeskChatConnector.tool_utils
async def zendesk-chat_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [Get](./REFERENCE.md#accounts-get) |
| Agents | [List](./REFERENCE.md#agents-list), [Get](./REFERENCE.md#agents-get) |
| Agent Timeline | [List](./REFERENCE.md#agent-timeline-list) |
| Bans | [List](./REFERENCE.md#bans-list), [Get](./REFERENCE.md#bans-get) |
| Chats | [List](./REFERENCE.md#chats-list), [Get](./REFERENCE.md#chats-get) |
| Departments | [List](./REFERENCE.md#departments-list), [Get](./REFERENCE.md#departments-get) |
| Goals | [List](./REFERENCE.md#goals-list), [Get](./REFERENCE.md#goals-get) |
| Roles | [List](./REFERENCE.md#roles-list), [Get](./REFERENCE.md#roles-get) |
| Routing Settings | [Get](./REFERENCE.md#routing-settings-get) |
| Shortcuts | [List](./REFERENCE.md#shortcuts-list), [Get](./REFERENCE.md#shortcuts-get) |
| Skills | [List](./REFERENCE.md#skills-list), [Get](./REFERENCE.md#skills-get) |
| Triggers | [List](./REFERENCE.md#triggers-list) |


### Authentication and configuration

For all authentication and configuration options, see the connector's [authentication documentation](AUTH.md).

### Zendesk-Chat API docs

See the official [Zendesk-Chat API reference](https://developer.zendesk.com/api-reference/live-chat/chat-api/introduction/).

## Version information

- **Package version:** 0.1.26
- **Connector version:** 0.1.6
- **Generated with Connector SDK commit SHA:** b184da3e22ef8521d2eeebf3c96a0fe8da2424f5
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/zendesk-chat/CHANGELOG.md)