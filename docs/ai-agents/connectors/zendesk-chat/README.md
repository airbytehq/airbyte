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

```python
from airbyte_agent_zendesk_chat import ZendeskChatConnector, ZendeskChatAuthConfig

connector = ZendeskChatConnector(
  auth_config=ZendeskChatAuthConfig(
    access_token="..."
  )
)
result = await connector.accounts.get()
```


## Full documentation

This connector supports the following entities and actions.

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


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Zendesk-Chat API reference](https://developer.zendesk.com/api-reference/live-chat/chat-api/introduction/).

## Version information

- **Package version:** 0.1.1
- **Connector version:** 0.1.2
- **Generated with Connector SDK commit SHA:** d6d3159205e21eefdcc8ade281c9a9839218ca5c