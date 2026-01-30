# Zendesk-Chat full reference

This is the full reference documentation for the Zendesk-Chat agent connector.

## Supported entities and actions

The Zendesk-Chat connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [Get](#accounts-get) |
| Agents | [List](#agents-list), [Get](#agents-get), [Search](#agents-search) |
| Agent Timeline | [List](#agent-timeline-list) |
| Bans | [List](#bans-list), [Get](#bans-get) |
| Chats | [List](#chats-list), [Get](#chats-get), [Search](#chats-search) |
| Departments | [List](#departments-list), [Get](#departments-get), [Search](#departments-search) |
| Goals | [List](#goals-list), [Get](#goals-get) |
| Roles | [List](#roles-list), [Get](#roles-get) |
| Routing Settings | [Get](#routing-settings-get) |
| Shortcuts | [List](#shortcuts-list), [Get](#shortcuts-get), [Search](#shortcuts-search) |
| Skills | [List](#skills-list), [Get](#skills-get) |
| Triggers | [List](#triggers-list), [Search](#triggers-search) |

## Accounts

### Accounts Get

Returns the account information for the authenticated user

#### Python SDK

```python
await zendesk_chat.accounts.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_key` | `string` |  |
| `status` | `string \| null` |  |
| `create_date` | `string \| null` |  |
| `billing` | `object \| any` |  |
| `plan` | `object \| any` |  |


</details>

## Agents

### Agents List

List all agents

#### Python SDK

```python
await zendesk_chat.agents.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `since_id` | `integer` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `email` | `string \| null` |  |
| `display_name` | `string \| null` |  |
| `first_name` | `string \| null` |  |
| `last_name` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `role_id` | `integer \| null` |  |
| `roles` | `object \| any` |  |
| `departments` | `array \| null` |  |
| `enabled_departments` | `array \| null` |  |
| `skills` | `array \| null` |  |
| `scope` | `string \| null` |  |
| `create_date` | `string \| null` |  |
| `last_login` | `string \| null` |  |
| `login_count` | `integer \| null` |  |


</details>

### Agents Get

Get an agent

#### Python SDK

```python
await zendesk_chat.agents.get(
    agent_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents",
    "action": "get",
    "params": {
        "agent_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `agent_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `email` | `string \| null` |  |
| `display_name` | `string \| null` |  |
| `first_name` | `string \| null` |  |
| `last_name` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `role_id` | `integer \| null` |  |
| `roles` | `object \| any` |  |
| `departments` | `array \| null` |  |
| `enabled_departments` | `array \| null` |  |
| `skills` | `array \| null` |  |
| `scope` | `string \| null` |  |
| `create_date` | `string \| null` |  |
| `last_login` | `string \| null` |  |
| `login_count` | `integer \| null` |  |


</details>

### Agents Search

Search and filter agents records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_chat.agents.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Unique agent identifier |
| `email` | `string` | Agent email address |
| `display_name` | `string` | Agent display name |
| `first_name` | `string` | Agent first name |
| `last_name` | `string` | Agent last name |
| `enabled` | `boolean` | Whether agent is enabled |
| `role_id` | `integer` | Agent role ID |
| `departments` | `array` | Department IDs agent belongs to |
| `create_date` | `string` | When agent was created |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `integer` | Unique agent identifier |
| `hits[].data.email` | `string` | Agent email address |
| `hits[].data.display_name` | `string` | Agent display name |
| `hits[].data.first_name` | `string` | Agent first name |
| `hits[].data.last_name` | `string` | Agent last name |
| `hits[].data.enabled` | `boolean` | Whether agent is enabled |
| `hits[].data.role_id` | `integer` | Agent role ID |
| `hits[].data.departments` | `array` | Department IDs agent belongs to |
| `hits[].data.create_date` | `string` | When agent was created |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Agent Timeline

### Agent Timeline List

List agent timeline (incremental export)

#### Python SDK

```python
await zendesk_chat.agent_timeline.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agent_timeline",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_time` | `integer` | No |  |
| `limit` | `integer` | No |  |
| `fields` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `agent_id` | `integer` |  |
| `start_time` | `string \| null` |  |
| `status` | `string \| null` |  |
| `duration` | `number \| null` |  |
| `engagement_count` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

## Bans

### Bans List

List all bans

#### Python SDK

```python
await zendesk_chat.bans.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bans",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No |  |
| `since_id` | `integer` | No |  |


### Bans Get

Get a ban

#### Python SDK

```python
await zendesk_chat.bans.get(
    ban_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bans",
    "action": "get",
    "params": {
        "ban_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ban_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `string \| null` |  |
| `ip_address` | `string \| null` |  |
| `visitor_id` | `string \| null` |  |
| `visitor_name` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `created_at` | `string \| null` |  |


</details>

## Chats

### Chats List

List chats (incremental export)

#### Python SDK

```python
await zendesk_chat.chats.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "chats",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_time` | `integer` | No |  |
| `limit` | `integer` | No |  |
| `fields` | `string` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `timestamp` | `string \| null` |  |
| `update_timestamp` | `string \| null` |  |
| `duration` | `integer \| null` |  |
| `department_id` | `integer \| null` |  |
| `department_name` | `string \| null` |  |
| `agent_ids` | `array \| null` |  |
| `agent_names` | `array \| null` |  |
| `visitor` | `object \| any` |  |
| `session` | `object \| any` |  |
| `history` | `array \| null` |  |
| `history[].type` | `string \| null` |  |
| `history[].timestamp` | `string \| null` |  |
| `history[].name` | `string \| null` |  |
| `history[].nick` | `string \| null` |  |
| `history[].msg` | `string \| null` |  |
| `history[].msg_id` | `string \| null` |  |
| `history[].channel` | `string \| null` |  |
| `history[].department_id` | `integer \| null` |  |
| `history[].department_name` | `string \| null` |  |
| `history[].rating` | `string \| null` |  |
| `history[].new_rating` | `string \| null` |  |
| `history[].tags` | `array \| null` |  |
| `history[].new_tags` | `array \| null` |  |
| `history[].options` | `string \| null` |  |
| `engagements` | `array \| null` |  |
| `engagements[].id` | `string \| null` |  |
| `engagements[].agent_id` | `string \| null` |  |
| `engagements[].agent_name` | `string \| null` |  |
| `engagements[].agent_full_name` | `string \| null` |  |
| `engagements[].department_id` | `integer \| null` |  |
| `engagements[].timestamp` | `string \| null` |  |
| `engagements[].duration` | `number \| null` |  |
| `engagements[].accepted` | `boolean \| null` |  |
| `engagements[].assigned` | `boolean \| null` |  |
| `engagements[].started_by` | `string \| null` |  |
| `engagements[].rating` | `string \| null` |  |
| `engagements[].comment` | `string \| null` |  |
| `engagements[].count` | `object \| any` |  |
| `engagements[].response_time` | `object \| any` |  |
| `engagements[].skills_requested` | `array \| null` |  |
| `engagements[].skills_fulfilled` | `boolean \| null` |  |
| `conversions` | `array \| null` |  |
| `conversions[].id` | `string \| null` |  |
| `conversions[].goal_id` | `integer \| null` |  |
| `conversions[].goal_name` | `string \| null` |  |
| `conversions[].timestamp` | `string \| null` |  |
| `conversions[].attribution` | `object \| any` |  |
| `count` | `object \| any` |  |
| `response_time` | `object \| any` |  |
| `rating` | `string \| null` |  |
| `comment` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `started_by` | `string \| null` |  |
| `triggered` | `boolean \| null` |  |
| `triggered_response` | `boolean \| null` |  |
| `missed` | `boolean \| null` |  |
| `unread` | `boolean \| null` |  |
| `deleted` | `boolean \| null` |  |
| `message` | `string \| null` |  |
| `webpath` | `array \| null` |  |
| `webpath[].from` | `string \| null` |  |
| `webpath[].timestamp` | `string \| null` |  |
| `zendesk_ticket_id` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Chats Get

Get a chat

#### Python SDK

```python
await zendesk_chat.chats.get(
    chat_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "chats",
    "action": "get",
    "params": {
        "chat_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `chat_id` | `string` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `timestamp` | `string \| null` |  |
| `update_timestamp` | `string \| null` |  |
| `duration` | `integer \| null` |  |
| `department_id` | `integer \| null` |  |
| `department_name` | `string \| null` |  |
| `agent_ids` | `array \| null` |  |
| `agent_names` | `array \| null` |  |
| `visitor` | `object \| any` |  |
| `session` | `object \| any` |  |
| `history` | `array \| null` |  |
| `history[].type` | `string \| null` |  |
| `history[].timestamp` | `string \| null` |  |
| `history[].name` | `string \| null` |  |
| `history[].nick` | `string \| null` |  |
| `history[].msg` | `string \| null` |  |
| `history[].msg_id` | `string \| null` |  |
| `history[].channel` | `string \| null` |  |
| `history[].department_id` | `integer \| null` |  |
| `history[].department_name` | `string \| null` |  |
| `history[].rating` | `string \| null` |  |
| `history[].new_rating` | `string \| null` |  |
| `history[].tags` | `array \| null` |  |
| `history[].new_tags` | `array \| null` |  |
| `history[].options` | `string \| null` |  |
| `engagements` | `array \| null` |  |
| `engagements[].id` | `string \| null` |  |
| `engagements[].agent_id` | `string \| null` |  |
| `engagements[].agent_name` | `string \| null` |  |
| `engagements[].agent_full_name` | `string \| null` |  |
| `engagements[].department_id` | `integer \| null` |  |
| `engagements[].timestamp` | `string \| null` |  |
| `engagements[].duration` | `number \| null` |  |
| `engagements[].accepted` | `boolean \| null` |  |
| `engagements[].assigned` | `boolean \| null` |  |
| `engagements[].started_by` | `string \| null` |  |
| `engagements[].rating` | `string \| null` |  |
| `engagements[].comment` | `string \| null` |  |
| `engagements[].count` | `object \| any` |  |
| `engagements[].response_time` | `object \| any` |  |
| `engagements[].skills_requested` | `array \| null` |  |
| `engagements[].skills_fulfilled` | `boolean \| null` |  |
| `conversions` | `array \| null` |  |
| `conversions[].id` | `string \| null` |  |
| `conversions[].goal_id` | `integer \| null` |  |
| `conversions[].goal_name` | `string \| null` |  |
| `conversions[].timestamp` | `string \| null` |  |
| `conversions[].attribution` | `object \| any` |  |
| `count` | `object \| any` |  |
| `response_time` | `object \| any` |  |
| `rating` | `string \| null` |  |
| `comment` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `started_by` | `string \| null` |  |
| `triggered` | `boolean \| null` |  |
| `triggered_response` | `boolean \| null` |  |
| `missed` | `boolean \| null` |  |
| `unread` | `boolean \| null` |  |
| `deleted` | `boolean \| null` |  |
| `message` | `string \| null` |  |
| `webpath` | `array \| null` |  |
| `webpath[].from` | `string \| null` |  |
| `webpath[].timestamp` | `string \| null` |  |
| `zendesk_ticket_id` | `integer \| null` |  |


</details>

### Chats Search

Search and filter chats records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_chat.chats.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "chats",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique chat identifier |
| `timestamp` | `string` | Chat start timestamp |
| `update_timestamp` | `string` | Last update timestamp |
| `department_id` | `integer` | Department ID |
| `department_name` | `string` | Department name |
| `duration` | `integer` | Chat duration in seconds |
| `rating` | `string` | Satisfaction rating |
| `missed` | `boolean` | Whether chat was missed |
| `agent_ids` | `array` | IDs of agents in chat |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Unique chat identifier |
| `hits[].data.timestamp` | `string` | Chat start timestamp |
| `hits[].data.update_timestamp` | `string` | Last update timestamp |
| `hits[].data.department_id` | `integer` | Department ID |
| `hits[].data.department_name` | `string` | Department name |
| `hits[].data.duration` | `integer` | Chat duration in seconds |
| `hits[].data.rating` | `string` | Satisfaction rating |
| `hits[].data.missed` | `boolean` | Whether chat was missed |
| `hits[].data.agent_ids` | `array` | IDs of agents in chat |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Departments

### Departments List

List all departments

#### Python SDK

```python
await zendesk_chat.departments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `members` | `array \| null` |  |
| `settings` | `object \| any` |  |


</details>

### Departments Get

Get a department

#### Python SDK

```python
await zendesk_chat.departments.get(
    department_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "get",
    "params": {
        "department_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `department_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `members` | `array \| null` |  |
| `settings` | `object \| any` |  |


</details>

### Departments Search

Search and filter departments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_chat.departments.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Department ID |
| `name` | `string` | Department name |
| `enabled` | `boolean` | Whether department is enabled |
| `members` | `array` | Agent IDs in department |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `integer` | Department ID |
| `hits[].data.name` | `string` | Department name |
| `hits[].data.enabled` | `boolean` | Whether department is enabled |
| `hits[].data.members` | `array` | Agent IDs in department |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Goals

### Goals List

List all goals

#### Python SDK

```python
await zendesk_chat.goals.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "goals",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `attribution_model` | `string \| null` |  |
| `attribution_window` | `integer \| null` |  |
| `attribution_period` | `integer \| null` |  |
| `settings` | `object \| null` |  |


</details>

### Goals Get

Get a goal

#### Python SDK

```python
await zendesk_chat.goals.get(
    goal_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "goals",
    "action": "get",
    "params": {
        "goal_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `goal_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `attribution_model` | `string \| null` |  |
| `attribution_window` | `integer \| null` |  |
| `attribution_period` | `integer \| null` |  |
| `settings` | `object \| null` |  |


</details>

## Roles

### Roles List

List all roles

#### Python SDK

```python
await zendesk_chat.roles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "roles",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `permissions` | `object \| null` |  |
| `members_count` | `integer \| null` |  |


</details>

### Roles Get

Get a role

#### Python SDK

```python
await zendesk_chat.roles.get(
    role_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "roles",
    "action": "get",
    "params": {
        "role_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `role_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `permissions` | `object \| null` |  |
| `members_count` | `integer \| null` |  |


</details>

## Routing Settings

### Routing Settings Get

Get routing settings

#### Python SDK

```python
await zendesk_chat.routing_settings.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "routing_settings",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `routing_mode` | `string \| null` |  |
| `chat_limit` | `object \| null` |  |
| `skill_routing` | `object \| null` |  |
| `reassignment` | `object \| null` |  |
| `auto_idle` | `object \| null` |  |
| `auto_accept` | `object \| null` |  |


</details>

## Shortcuts

### Shortcuts List

List all shortcuts

#### Python SDK

```python
await zendesk_chat.shortcuts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shortcuts",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `message` | `string \| null` |  |
| `options` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `departments` | `array \| null` |  |
| `agents` | `array \| null` |  |
| `scope` | `string \| null` |  |


</details>

### Shortcuts Get

Get a shortcut

#### Python SDK

```python
await zendesk_chat.shortcuts.get(
    shortcut_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shortcuts",
    "action": "get",
    "params": {
        "shortcut_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `shortcut_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `message` | `string \| null` |  |
| `options` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `departments` | `array \| null` |  |
| `agents` | `array \| null` |  |
| `scope` | `string \| null` |  |


</details>

### Shortcuts Search

Search and filter shortcuts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_chat.shortcuts.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "shortcuts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Shortcut ID |
| `name` | `string` | Shortcut name/trigger |
| `message` | `string` | Shortcut message content |
| `tags` | `array` | Tags applied when shortcut is used |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `integer` | Shortcut ID |
| `hits[].data.name` | `string` | Shortcut name/trigger |
| `hits[].data.message` | `string` | Shortcut message content |
| `hits[].data.tags` | `array` | Tags applied when shortcut is used |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Skills

### Skills List

List all skills

#### Python SDK

```python
await zendesk_chat.skills.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "skills",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `members` | `array \| null` |  |


</details>

### Skills Get

Get a skill

#### Python SDK

```python
await zendesk_chat.skills.get(
    skill_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "skills",
    "action": "get",
    "params": {
        "skill_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `skill_id` | `integer` | Yes |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `members` | `array \| null` |  |


</details>

## Triggers

### Triggers List

List all triggers

#### Python SDK

```python
await zendesk_chat.triggers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "triggers",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `description` | `string \| null` |  |
| `enabled` | `boolean \| null` |  |
| `run_once` | `boolean \| null` |  |
| `conditions` | `array \| null` |  |
| `actions` | `array \| null` |  |
| `departments` | `array \| null` |  |
| `definition` | `object \| null` |  |


</details>

### Triggers Search

Search and filter triggers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_chat.triggers.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "triggers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Trigger ID |
| `name` | `string` | Trigger name |
| `enabled` | `boolean` | Whether trigger is enabled |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `integer` | Trigger ID |
| `hits[].data.name` | `string` | Trigger name |
| `hits[].data.enabled` | `boolean` | Whether trigger is enabled |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

