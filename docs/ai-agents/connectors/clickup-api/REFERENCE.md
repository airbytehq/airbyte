# Clickup-Api full reference

This is the full reference documentation for the Clickup-Api agent connector.

## Supported entities and actions

The Clickup-Api connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| User | [Get](#user-get), [Context Store Search](#user-context-store-search) |
| Teams | [List](#teams-list), [Context Store Search](#teams-context-store-search) |
| Spaces | [List](#spaces-list), [Get](#spaces-get), [Context Store Search](#spaces-context-store-search) |
| Folders | [List](#folders-list), [Get](#folders-get), [Context Store Search](#folders-context-store-search) |
| Lists | [List](#lists-list), [Get](#lists-get), [Context Store Search](#lists-context-store-search) |
| Tasks | [List](#tasks-list), [Get](#tasks-get), [API Search](#tasks-api-search), [Context Store Search](#tasks-context-store-search) |
| Comments | [List](#comments-list), [Create](#comments-create), [Get](#comments-get), [Update](#comments-update), [Context Store Search](#comments-context-store-search) |
| Goals | [List](#goals-list), [Get](#goals-get), [Context Store Search](#goals-context-store-search) |
| Views | [List](#views-list), [Get](#views-get) |
| View Tasks | [List](#view-tasks-list) |
| Time Tracking | [List](#time-tracking-list), [Get](#time-tracking-get), [Context Store Search](#time-tracking-context-store-search) |
| Members | [List](#members-list) |
| Docs | [List](#docs-list), [Get](#docs-get) |

## User

### User Get

View the details of the authenticated user's ClickUp account

#### Python SDK

```python
await clickup_api.user.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `email` | `string` |  |
| `color` | `string \| null` |  |
| `profilePicture` | `string \| null` |  |
| `initials` | `string \| null` |  |
| `week_start_day` | `integer \| null` |  |
| `global_font_support` | `boolean \| null` |  |
| `timezone` | `string \| null` |  |


</details>

### User Context Store Search

Search and filter user records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.user.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Unique identifier for the user |
| `username` | `string` | Display name of the user |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique identifier for the user |
| `data[].username` | `string` | Display name of the user |

</details>

## Teams

### Teams List

Get the workspaces (teams) available to the authenticated user

#### Python SDK

```python
await clickup_api.teams.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `color` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `members` | `array<object>` |  |


</details>

### Teams Context Store Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.teams.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the team (workspace) |
| `name` | `string` | Name of the team |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the team (workspace) |
| `data[].name` | `string` | Name of the team |

</details>

## Spaces

### Spaces List

Get the spaces available in a workspace

#### Python SDK

```python
await clickup_api.spaces.list(
    team_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spaces",
    "action": "list",
    "params": {
        "team_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the workspace |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `private` | `boolean` |  |
| `color` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `admin_can_manage` | `boolean \| null` |  |
| `statuses` | `array<object>` |  |
| `multiple_assignees` | `boolean` |  |
| `features` | `object` |  |
| `archived` | `boolean` |  |


</details>

### Spaces Get

Get a single space by ID

#### Python SDK

```python
await clickup_api.spaces.get(
    space_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spaces",
    "action": "get",
    "params": {
        "space_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `space_id` | `string` | Yes | The ID of the space |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `private` | `boolean` |  |
| `color` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `admin_can_manage` | `boolean \| null` |  |
| `statuses` | `array<object>` |  |
| `multiple_assignees` | `boolean` |  |
| `features` | `object` |  |
| `archived` | `boolean` |  |


</details>

### Spaces Context Store Search

Search and filter spaces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.spaces.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spaces",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the space |
| `name` | `string` | Name of the space |
| `private` | `boolean` | Whether the space is private |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the space |
| `data[].name` | `string` | Name of the space |
| `data[].private` | `boolean` | Whether the space is private |

</details>

## Folders

### Folders List

Get the folders in a space

#### Python SDK

```python
await clickup_api.folders.list(
    space_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "folders",
    "action": "list",
    "params": {
        "space_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `space_id` | `string` | Yes | The ID of the space |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `orderindex` | `integer \| null` |  |
| `override_statuses` | `boolean` |  |
| `hidden` | `boolean` |  |
| `space` | `object` |  |
| `task_count` | `string \| null` |  |
| `archived` | `boolean` |  |
| `statuses` | `array<object>` |  |
| `deleted` | `boolean \| null` |  |
| `lists` | `array<object>` |  |
| `permission_level` | `string \| null` |  |


</details>

### Folders Get

Get a single folder by ID

#### Python SDK

```python
await clickup_api.folders.get(
    folder_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "folders",
    "action": "get",
    "params": {
        "folder_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `folder_id` | `string` | Yes | The ID of the folder |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `orderindex` | `integer \| null` |  |
| `override_statuses` | `boolean` |  |
| `hidden` | `boolean` |  |
| `space` | `object` |  |
| `task_count` | `string \| null` |  |
| `archived` | `boolean` |  |
| `statuses` | `array<object>` |  |
| `deleted` | `boolean \| null` |  |
| `lists` | `array<object>` |  |
| `permission_level` | `string \| null` |  |


</details>

### Folders Context Store Search

Search and filter folders records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.folders.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "folders",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the folder |
| `name` | `string` | Name of the folder |
| `hidden` | `boolean` | Whether the folder is hidden from the sidebar |
| `task_count` | `string` | Number of tasks contained in the folder |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the folder |
| `data[].name` | `string` | Name of the folder |
| `data[].hidden` | `boolean` | Whether the folder is hidden from the sidebar |
| `data[].task_count` | `string` | Number of tasks contained in the folder |

</details>

## Lists

### Lists List

Get the lists in a folder

#### Python SDK

```python
await clickup_api.lists.list(
    folder_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "list",
    "params": {
        "folder_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `folder_id` | `string` | Yes | The ID of the folder |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `orderindex` | `integer \| null` |  |
| `status` | `object \| null` |  |
| `priority` | `object \| null` |  |
| `assignee` | `object \| null` |  |
| `task_count` | `integer \| null` |  |
| `due_date` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `folder` | `object` |  |
| `space` | `object` |  |
| `archived` | `boolean` |  |
| `override_statuses` | `boolean \| null` |  |
| `content` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `inbound_address` | `string \| null` |  |
| `statuses` | `array<object>` |  |
| `permission_level` | `string \| null` |  |


</details>

### Lists Get

Get a single list by ID

#### Python SDK

```python
await clickup_api.lists.get(
    list_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "get",
    "params": {
        "list_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The ID of the list |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `orderindex` | `integer \| null` |  |
| `status` | `object \| null` |  |
| `priority` | `object \| null` |  |
| `assignee` | `object \| null` |  |
| `task_count` | `integer \| null` |  |
| `due_date` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `folder` | `object` |  |
| `space` | `object` |  |
| `archived` | `boolean` |  |
| `override_statuses` | `boolean \| null` |  |
| `content` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `inbound_address` | `string \| null` |  |
| `statuses` | `array<object>` |  |
| `permission_level` | `string \| null` |  |


</details>

### Lists Context Store Search

Search and filter lists records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.lists.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the list |
| `name` | `string` | Name of the list |
| `archived` | `boolean` | Whether the list has been archived |
| `due_date` | `string` | Due date for the list, in ClickUp timestamp format |
| `start_date` | `string` | Start date for the list, in ClickUp timestamp format |
| `priority` | `string` | Priority assigned to the list |
| `task_count` | `integer` | Number of tasks contained in the list |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the list |
| `data[].name` | `string` | Name of the list |
| `data[].archived` | `boolean` | Whether the list has been archived |
| `data[].due_date` | `string` | Due date for the list, in ClickUp timestamp format |
| `data[].start_date` | `string` | Start date for the list, in ClickUp timestamp format |
| `data[].priority` | `string` | Priority assigned to the list |
| `data[].task_count` | `integer` | Number of tasks contained in the list |

</details>

## Tasks

### Tasks List

Get the tasks in a list

#### Python SDK

```python
await clickup_api.tasks.list(
    list_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list",
    "params": {
        "list_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The ID of the list |
| `page` | `integer` | No | Page number (0-indexed) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `custom_id` | `string \| null` |  |
| `custom_item_id` | `integer \| null` |  |
| `name` | `string` |  |
| `text_content` | `string \| null` |  |
| `description` | `string \| null` |  |
| `status` | `object` |  |
| `orderindex` | `string \| null` |  |
| `date_created` | `string \| null` |  |
| `date_updated` | `string \| null` |  |
| `date_closed` | `string \| null` |  |
| `date_done` | `string \| null` |  |
| `archived` | `boolean` |  |
| `creator` | `object` |  |
| `assignees` | `array<object>` |  |
| `group_assignees` | `array<object>` |  |
| `watchers` | `array<object>` |  |
| `checklists` | `array<object>` |  |
| `tags` | `array<object>` |  |
| `parent` | `string \| null` |  |
| `priority` | `object \| null` |  |
| `due_date` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `points` | `number \| null` |  |
| `time_estimate` | `integer \| null` |  |
| `time_spent` | `integer \| null` |  |
| `custom_fields` | `array<object>` |  |
| `dependencies` | `array<object>` |  |
| `linked_tasks` | `array<object>` |  |
| `team_id` | `string \| null` |  |
| `url` | `string` |  |
| `list` | `object \| null` |  |
| `project` | `object \| null` |  |
| `folder` | `object \| null` |  |
| `space` | `object \| null` |  |
| `top_level_parent` | `string \| null` |  |
| `locations` | `array<object>` |  |
| `sharing` | `object \| null` |  |
| `permission_level` | `string \| null` |  |
| `attachments` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `last_page` | `boolean \| null` |  |

</details>

### Tasks Get

Get a single task by ID

#### Python SDK

```python
await clickup_api.tasks.get(
    task_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "get",
    "params": {
        "task_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_id` | `string` | Yes | The ID of the task |
| `custom_task_ids` | `boolean` | No | Set to true to use a custom task ID |
| `include_subtasks` | `boolean` | No | Include subtasks |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `custom_id` | `string \| null` |  |
| `custom_item_id` | `integer \| null` |  |
| `name` | `string` |  |
| `text_content` | `string \| null` |  |
| `description` | `string \| null` |  |
| `status` | `object` |  |
| `orderindex` | `string \| null` |  |
| `date_created` | `string \| null` |  |
| `date_updated` | `string \| null` |  |
| `date_closed` | `string \| null` |  |
| `date_done` | `string \| null` |  |
| `archived` | `boolean` |  |
| `creator` | `object` |  |
| `assignees` | `array<object>` |  |
| `group_assignees` | `array<object>` |  |
| `watchers` | `array<object>` |  |
| `checklists` | `array<object>` |  |
| `tags` | `array<object>` |  |
| `parent` | `string \| null` |  |
| `priority` | `object \| null` |  |
| `due_date` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `points` | `number \| null` |  |
| `time_estimate` | `integer \| null` |  |
| `time_spent` | `integer \| null` |  |
| `custom_fields` | `array<object>` |  |
| `dependencies` | `array<object>` |  |
| `linked_tasks` | `array<object>` |  |
| `team_id` | `string \| null` |  |
| `url` | `string` |  |
| `list` | `object \| null` |  |
| `project` | `object \| null` |  |
| `folder` | `object \| null` |  |
| `space` | `object \| null` |  |
| `top_level_parent` | `string \| null` |  |
| `locations` | `array<object>` |  |
| `sharing` | `object \| null` |  |
| `permission_level` | `string \| null` |  |
| `attachments` | `array<object>` |  |


</details>

### Tasks API Search

View the tasks that meet specific criteria from a workspace. Supports free-text search
and structured filters including status, assignee, tags, priority, and date ranges.
Responses are limited to 100 tasks per page.


#### Python SDK

```python
await clickup_api.tasks.api_search(
    team_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "api_search",
    "params": {
        "team_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_id` | `string` | Yes | The workspace ID to search within |
| `search` | `string` | No | Free-text search across task name, description, and custom field text |
| `statuses[]` | `array<string>` | No | Filter by status names (e.g. "in progress", "done") |
| `assignees[]` | `array<string>` | No | Filter by user IDs |
| `tags[]` | `array<string>` | No | Filter by tag names |
| `priority` | `integer` | No | Filter by priority: 1=Urgent, 2=High, 3=Normal, 4=Low |
| `due_date_gt` | `integer` | No | Due date after (Unix ms) |
| `due_date_lt` | `integer` | No | Due date before (Unix ms) |
| `date_created_gt` | `integer` | No | Created after (Unix ms) |
| `date_created_lt` | `integer` | No | Created before (Unix ms) |
| `date_updated_gt` | `integer` | No | Updated after (Unix ms) |
| `date_updated_lt` | `integer` | No | Updated before (Unix ms) |
| `custom_fields` | `array<object>` | No | JSON array of custom field filters. Each object: \{"field_id": "\<UUID\>", "operator": "\<OP\>", "value": "\<DATA\>"\}.
Operators: = (contains), == (exact), \<, \<=, \>, \>=, !=, !==, IS NULL, IS NOT NULL, RANGE, ANY, ALL, NOT ANY, NOT ALL
 |
| `include_closed` | `boolean` | No | Include closed tasks (excluded by default) |
| `page` | `integer` | No | Page number (0-indexed), results capped at 100/page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `custom_id` | `string \| null` |  |
| `custom_item_id` | `integer \| null` |  |
| `name` | `string` |  |
| `text_content` | `string \| null` |  |
| `description` | `string \| null` |  |
| `status` | `object` |  |
| `orderindex` | `string \| null` |  |
| `date_created` | `string \| null` |  |
| `date_updated` | `string \| null` |  |
| `date_closed` | `string \| null` |  |
| `date_done` | `string \| null` |  |
| `archived` | `boolean` |  |
| `creator` | `object` |  |
| `assignees` | `array<object>` |  |
| `group_assignees` | `array<object>` |  |
| `watchers` | `array<object>` |  |
| `checklists` | `array<object>` |  |
| `tags` | `array<object>` |  |
| `parent` | `string \| null` |  |
| `priority` | `object \| null` |  |
| `due_date` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `points` | `number \| null` |  |
| `time_estimate` | `integer \| null` |  |
| `time_spent` | `integer \| null` |  |
| `custom_fields` | `array<object>` |  |
| `dependencies` | `array<object>` |  |
| `linked_tasks` | `array<object>` |  |
| `team_id` | `string \| null` |  |
| `url` | `string` |  |
| `list` | `object \| null` |  |
| `project` | `object \| null` |  |
| `folder` | `object \| null` |  |
| `space` | `object \| null` |  |
| `top_level_parent` | `string \| null` |  |
| `locations` | `array<object>` |  |
| `sharing` | `object \| null` |  |
| `permission_level` | `string \| null` |  |
| `attachments` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `last_page` | `boolean \| null` |  |

</details>

### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.tasks.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the task |
| `name` | `string` | Name of the task |
| `date_created` | `string` | Creation timestamp of the task, in ClickUp timestamp format |
| `date_updated` | `string` | Last update timestamp of the task, in ClickUp timestamp format |
| `date_closed` | `string` | Timestamp when the task was closed, in ClickUp timestamp format |
| `due_date` | `string` | Due date for the task, in ClickUp timestamp format |
| `start_date` | `string` | Start date for the task, in ClickUp timestamp format |
| `parent` | `string` | ID of the parent task, if this task is a subtask |
| `url` | `string` | Permalink URL to view the task in ClickUp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the task |
| `data[].name` | `string` | Name of the task |
| `data[].date_created` | `string` | Creation timestamp of the task, in ClickUp timestamp format |
| `data[].date_updated` | `string` | Last update timestamp of the task, in ClickUp timestamp format |
| `data[].date_closed` | `string` | Timestamp when the task was closed, in ClickUp timestamp format |
| `data[].due_date` | `string` | Due date for the task, in ClickUp timestamp format |
| `data[].start_date` | `string` | Start date for the task, in ClickUp timestamp format |
| `data[].parent` | `string` | ID of the parent task, if this task is a subtask |
| `data[].url` | `string` | Permalink URL to view the task in ClickUp |

</details>

## Comments

### Comments List

Get the comments on a task

#### Python SDK

```python
await clickup_api.comments.list(
    task_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "list",
    "params": {
        "task_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_id` | `string` | Yes | The ID of the task |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `comment` | `array<object>` |  |
| `comment_text` | `string` |  |
| `user` | `object` |  |
| `resolved` | `boolean` |  |
| `assignee` | `object \| null` |  |
| `assigned_by` | `object \| null` |  |
| `reactions` | `array<object>` |  |
| `date` | `string` |  |


</details>

### Comments Create

Create a comment on a task

#### Python SDK

```python
await clickup_api.comments.create(
    comment_text="<str>",
    assignee=0,
    notify_all=True,
    task_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "create",
    "params": {
        "comment_text": "<str>",
        "assignee": 0,
        "notify_all": True,
        "task_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `comment_text` | `string` | Yes | The comment text |
| `assignee` | `integer` | No | User ID to assign |
| `notify_all` | `boolean` | No | Notify all assignees and watchers |
| `task_id` | `string` | Yes | The ID of the task |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `hist_id` | `string` |  |
| `date` | `integer` |  |
| `version` | `object \| null` |  |


</details>

### Comments Get

Get threaded replies on a comment

#### Python SDK

```python
await clickup_api.comments.get(
    comment_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "get",
    "params": {
        "comment_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `comment_id` | `string` | Yes | The ID of the comment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `comment` | `array<object>` |  |
| `comment_text` | `string` |  |
| `user` | `object` |  |
| `resolved` | `boolean` |  |
| `assignee` | `object \| null` |  |
| `assigned_by` | `object \| null` |  |
| `reactions` | `array<object>` |  |
| `date` | `string` |  |


</details>

### Comments Update

Update an existing comment

#### Python SDK

```python
await clickup_api.comments.update(
    comment_text="<str>",
    assignee=0,
    resolved=True,
    comment_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "update",
    "params": {
        "comment_text": "<str>",
        "assignee": 0,
        "resolved": True,
        "comment_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `comment_text` | `string` | No | Updated comment text |
| `assignee` | `integer` | No | User ID to assign |
| `resolved` | `boolean` | No | Whether the comment is resolved |
| `comment_id` | `string` | Yes | The ID of the comment |


### Comments Context Store Search

Search and filter comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.comments.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the comment |
| `comment_text` | `string` | Plain-text content of the comment |
| `date` | `string` | Timestamp when the comment was posted, in ClickUp timestamp format |
| `reply_count` | `number` | Number of replies on the comment |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the comment |
| `data[].comment_text` | `string` | Plain-text content of the comment |
| `data[].date` | `string` | Timestamp when the comment was posted, in ClickUp timestamp format |
| `data[].reply_count` | `number` | Number of replies on the comment |

</details>

## Goals

### Goals List

Get the goals in a workspace

#### Python SDK

```python
await clickup_api.goals.list(
    team_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "goals",
    "action": "list",
    "params": {
        "team_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the workspace |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `pretty_id` | `string \| null` |  |
| `name` | `string` |  |
| `team_id` | `string` |  |
| `creator` | `integer \| null` |  |
| `owner` | `object \| null` |  |
| `color` | `string` |  |
| `date_created` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `due_date` | `string \| null` |  |
| `description` | `string \| null` |  |
| `private` | `boolean` |  |
| `archived` | `boolean` |  |
| `multiple_owners` | `boolean` |  |
| `members` | `array<object>` |  |
| `key_results` | `array<object>` |  |
| `percent_completed` | `integer \| null` |  |
| `history` | `array<object>` |  |
| `pretty_url` | `string \| null` |  |


</details>

### Goals Get

Get a single goal by ID

#### Python SDK

```python
await clickup_api.goals.get(
    goal_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "goals",
    "action": "get",
    "params": {
        "goal_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `goal_id` | `string` | Yes | The ID of the goal |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `pretty_id` | `string \| null` |  |
| `name` | `string` |  |
| `team_id` | `string` |  |
| `creator` | `integer \| null` |  |
| `owner` | `object \| null` |  |
| `color` | `string` |  |
| `date_created` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `due_date` | `string \| null` |  |
| `description` | `string \| null` |  |
| `private` | `boolean` |  |
| `archived` | `boolean` |  |
| `multiple_owners` | `boolean` |  |
| `members` | `array<object>` |  |
| `key_results` | `array<object>` |  |
| `percent_completed` | `integer \| null` |  |
| `history` | `array<object>` |  |
| `pretty_url` | `string \| null` |  |


</details>

### Goals Context Store Search

Search and filter goals records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.goals.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "goals",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the goal |
| `name` | `string` | Name of the goal |
| `description` | `string` | Description of the goal |
| `archived` | `boolean` | Whether the goal has been archived |
| `pinned` | `boolean` | Whether the goal is pinned to the top of the list |
| `private` | `boolean` | Whether the goal is private to its owners |
| `date_created` | `string` | Creation timestamp of the goal, in ClickUp timestamp format |
| `due_date` | `string` | Due date for the goal, in ClickUp timestamp format |
| `percent_completed` | `number` | Completion percentage of the goal, between 0 and 100 |
| `team_id` | `string` | Identifier of the team that owns the goal |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the goal |
| `data[].name` | `string` | Name of the goal |
| `data[].description` | `string` | Description of the goal |
| `data[].archived` | `boolean` | Whether the goal has been archived |
| `data[].pinned` | `boolean` | Whether the goal is pinned to the top of the list |
| `data[].private` | `boolean` | Whether the goal is private to its owners |
| `data[].date_created` | `string` | Creation timestamp of the goal, in ClickUp timestamp format |
| `data[].due_date` | `string` | Due date for the goal, in ClickUp timestamp format |
| `data[].percent_completed` | `number` | Completion percentage of the goal, between 0 and 100 |
| `data[].team_id` | `string` | Identifier of the team that owns the goal |

</details>

## Views

### Views List

Get the workspace-level (Everything level) views

#### Python SDK

```python
await clickup_api.views.list(
    team_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "views",
    "action": "list",
    "params": {
        "team_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the workspace |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `parent` | `object` |  |
| `grouping` | `object` |  |
| `divide` | `object` |  |
| `sorting` | `object` |  |
| `filters` | `object` |  |
| `columns` | `object` |  |
| `team_sidebar` | `object` |  |
| `settings` | `object` |  |
| `date_created` | `string \| null` |  |
| `creator` | `integer \| null` |  |
| `visibility` | `string \| null` |  |
| `protected` | `boolean \| null` |  |
| `protected_note` | `string \| null` |  |
| `protected_by` | `integer \| null` |  |
| `date_protected` | `string \| null` |  |
| `orderindex` | `integer` |  |
| `public` | `boolean` |  |


</details>

### Views Get

Get a single view by ID

#### Python SDK

```python
await clickup_api.views.get(
    view_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "views",
    "action": "get",
    "params": {
        "view_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `view_id` | `string` | Yes | The ID of the view |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `parent` | `object` |  |
| `grouping` | `object` |  |
| `divide` | `object` |  |
| `sorting` | `object` |  |
| `filters` | `object` |  |
| `columns` | `object` |  |
| `team_sidebar` | `object` |  |
| `settings` | `object` |  |
| `date_created` | `string \| null` |  |
| `creator` | `integer \| null` |  |
| `visibility` | `string \| null` |  |
| `protected` | `boolean \| null` |  |
| `protected_note` | `string \| null` |  |
| `protected_by` | `integer \| null` |  |
| `date_protected` | `string \| null` |  |
| `orderindex` | `integer` |  |
| `public` | `boolean` |  |


</details>

## View Tasks

### View Tasks List

Get tasks matching a view's pre-configured filters — useful as a secondary search mechanism

#### Python SDK

```python
await clickup_api.view_tasks.list(
    view_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "view_tasks",
    "action": "list",
    "params": {
        "view_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `view_id` | `string` | Yes | The ID of the view |
| `page` | `integer` | No | Page number (0-indexed) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `custom_id` | `string \| null` |  |
| `custom_item_id` | `integer \| null` |  |
| `name` | `string` |  |
| `text_content` | `string \| null` |  |
| `description` | `string \| null` |  |
| `status` | `object` |  |
| `orderindex` | `string \| null` |  |
| `date_created` | `string \| null` |  |
| `date_updated` | `string \| null` |  |
| `date_closed` | `string \| null` |  |
| `date_done` | `string \| null` |  |
| `archived` | `boolean` |  |
| `creator` | `object` |  |
| `assignees` | `array<object>` |  |
| `group_assignees` | `array<object>` |  |
| `watchers` | `array<object>` |  |
| `checklists` | `array<object>` |  |
| `tags` | `array<object>` |  |
| `parent` | `string \| null` |  |
| `priority` | `object \| null` |  |
| `due_date` | `string \| null` |  |
| `start_date` | `string \| null` |  |
| `points` | `number \| null` |  |
| `time_estimate` | `integer \| null` |  |
| `time_spent` | `integer \| null` |  |
| `custom_fields` | `array<object>` |  |
| `dependencies` | `array<object>` |  |
| `linked_tasks` | `array<object>` |  |
| `team_id` | `string \| null` |  |
| `url` | `string` |  |
| `list` | `object \| null` |  |
| `project` | `object \| null` |  |
| `folder` | `object \| null` |  |
| `space` | `object \| null` |  |
| `top_level_parent` | `string \| null` |  |
| `locations` | `array<object>` |  |
| `sharing` | `object \| null` |  |
| `permission_level` | `string \| null` |  |
| `attachments` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `last_page` | `boolean \| null` |  |

</details>

## Time Tracking

### Time Tracking List

Get time entries within a date range for a workspace

#### Python SDK

```python
await clickup_api.time_tracking.list(
    team_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_tracking",
    "action": "list",
    "params": {
        "team_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the workspace |
| `start_date` | `integer` | No | Start date (Unix ms) |
| `end_date` | `integer` | No | End date (Unix ms) |
| `assignee` | `string` | No | Filter by user ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `task` | `object \| null` |  |
| `wid` | `string \| null` |  |
| `user` | `object` |  |
| `billable` | `boolean` |  |
| `start` | `string` |  |
| `end` | `string \| null` |  |
| `duration` | `string` |  |
| `description` | `string \| null` |  |
| `tags` | `array<object>` |  |
| `at` | `string \| null` |  |


</details>

### Time Tracking Get

Get a single time entry by ID

#### Python SDK

```python
await clickup_api.time_tracking.get(
    team_id="<str>",
    time_entry_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_tracking",
    "action": "get",
    "params": {
        "team_id": "<str>",
        "time_entry_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_id` | `string` | Yes | The ID of the workspace |
| `time_entry_id` | `string` | Yes | The ID of the time entry |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `task` | `object \| null` |  |
| `wid` | `string \| null` |  |
| `user` | `object` |  |
| `billable` | `boolean` |  |
| `start` | `string` |  |
| `end` | `string \| null` |  |
| `duration` | `string` |  |
| `description` | `string \| null` |  |
| `tags` | `array<object>` |  |
| `at` | `string \| null` |  |


</details>

### Time Tracking Context Store Search

Search and filter time tracking records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await clickup_api.time_tracking.context_store_search(
    query={"filter": {"eq": {"time": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_tracking",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"time": 0.0}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `time` | `number` | Total tracked time in milliseconds |
| `user` | `object` | User who tracked the time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].time` | `number` | Total tracked time in milliseconds |
| `data[].user` | `object` | User who tracked the time |

</details>

## Members

### Members List

Get the members assigned to a task

#### Python SDK

```python
await clickup_api.members.list(
    task_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "members",
    "action": "list",
    "params": {
        "task_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_id` | `string` | Yes | The ID of the task |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `email` | `string` |  |
| `color` | `string \| null` |  |
| `profilePicture` | `string \| null` |  |
| `initials` | `string \| null` |  |


</details>

## Docs

### Docs List

Search for docs in a workspace

#### Python SDK

```python
await clickup_api.docs.list(
    workspace_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "docs",
    "action": "list",
    "params": {
        "workspace_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_id` | `string` | Yes | The ID of the workspace |
| `cursor` | `string` | No | Cursor for pagination to the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `integer \| null` |  |
| `parent` | `object \| null` |  |
| `creator` | `integer \| null` |  |
| `deleted` | `boolean \| null` |  |
| `public` | `boolean \| null` |  |
| `date_created` | `integer \| null` |  |
| `date_updated` | `integer \| null` |  |
| `workspace_id` | `integer \| null` |  |
| `content` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Docs Get

Fetch a single doc by ID

#### Python SDK

```python
await clickup_api.docs.get(
    workspace_id="<str>",
    doc_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "docs",
    "action": "get",
    "params": {
        "workspace_id": "<str>",
        "doc_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_id` | `string` | Yes | The ID of the workspace |
| `doc_id` | `string` | Yes | The ID of the doc |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `integer \| null` |  |
| `parent` | `object \| null` |  |
| `creator` | `integer \| null` |  |
| `deleted` | `boolean \| null` |  |
| `public` | `boolean \| null` |  |
| `date_created` | `integer \| null` |  |
| `date_updated` | `integer \| null` |  |
| `workspace_id` | `integer \| null` |  |
| `content` | `string \| null` |  |


</details>

