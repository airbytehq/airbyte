# Asana full reference

This is the full reference documentation for the Asana agent connector.

## Supported entities and actions

The Asana connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Tasks | [List](#tasks-list), [Get](#tasks-get), [Search](#tasks-search) |
| Project Tasks | [List](#project-tasks-list) |
| Workspace Task Search | [List](#workspace-task-search-list) |
| Projects | [List](#projects-list), [Get](#projects-get), [Search](#projects-search) |
| Task Projects | [List](#task-projects-list) |
| Team Projects | [List](#team-projects-list) |
| Workspace Projects | [List](#workspace-projects-list) |
| Workspaces | [List](#workspaces-list), [Get](#workspaces-get), [Search](#workspaces-search) |
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Workspace Users | [List](#workspace-users-list) |
| Team Users | [List](#team-users-list) |
| Teams | [Get](#teams-get), [Search](#teams-search) |
| Workspace Teams | [List](#workspace-teams-list) |
| User Teams | [List](#user-teams-list) |
| Attachments | [List](#attachments-list), [Get](#attachments-get), [Download](#attachments-download), [Search](#attachments-search) |
| Workspace Tags | [List](#workspace-tags-list) |
| Tags | [Get](#tags-get), [Search](#tags-search) |
| Project Sections | [List](#project-sections-list) |
| Sections | [Get](#sections-get), [Search](#sections-search) |
| Task Subtasks | [List](#task-subtasks-list) |
| Task Dependencies | [List](#task-dependencies-list) |
| Task Dependents | [List](#task-dependents-list) |

## Tasks

### Tasks List

Returns a paginated list of tasks. Must include either a project OR a section OR a workspace AND assignee parameter.

#### Python SDK

```python
await asana.tasks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `project` | `string` | No | The project to filter tasks on |
| `workspace` | `string` | No | The workspace to filter tasks on |
| `section` | `string` | No | The workspace to filter tasks on |
| `assignee` | `string` | No | The assignee to filter tasks on |
| `completed_since` | `string` | No | Only return tasks that have been completed since this time |
| `modified_since` | `string` | No | Only return tasks that have been completed since this time |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Tasks Get

Get a single task by its ID

#### Python SDK

```python
await asana.tasks.get(
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "get",
    "params": {
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |


</details>

### Tasks Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.tasks.search(
    query={"filter": {"eq": {"actual_time_minutes": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"actual_time_minutes": 0}}}
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
| `actual_time_minutes` | `integer` | The actual time spent on the task in minutes |
| `approval_status` | `string` |  |
| `assignee` | `object` |  |
| `completed` | `boolean` |  |
| `completed_at` | `string` |  |
| `completed_by` | `object` |  |
| `created_at` | `string` |  |
| `custom_fields` | `array` |  |
| `dependencies` | `array` |  |
| `dependents` | `array` |  |
| `due_at` | `string` |  |
| `due_on` | `string` |  |
| `external` | `object` |  |
| `followers` | `array` |  |
| `gid` | `string` |  |
| `hearted` | `boolean` |  |
| `hearts` | `array` |  |
| `html_notes` | `string` |  |
| `is_rendered_as_separator` | `boolean` |  |
| `liked` | `boolean` |  |
| `likes` | `array` |  |
| `memberships` | `array` |  |
| `modified_at` | `string` |  |
| `name` | `string` |  |
| `notes` | `string` |  |
| `num_hearts` | `integer` |  |
| `num_likes` | `integer` |  |
| `num_subtasks` | `integer` |  |
| `parent` | `object` |  |
| `permalink_url` | `string` |  |
| `projects` | `array` |  |
| `resource_subtype` | `string` |  |
| `resource_type` | `string` |  |
| `start_on` | `string` |  |
| `tags` | `array` |  |
| `workspace` | `object` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.actual_time_minutes` | `integer` | The actual time spent on the task in minutes |
| `hits[].data.approval_status` | `string` |  |
| `hits[].data.assignee` | `object` |  |
| `hits[].data.completed` | `boolean` |  |
| `hits[].data.completed_at` | `string` |  |
| `hits[].data.completed_by` | `object` |  |
| `hits[].data.created_at` | `string` |  |
| `hits[].data.custom_fields` | `array` |  |
| `hits[].data.dependencies` | `array` |  |
| `hits[].data.dependents` | `array` |  |
| `hits[].data.due_at` | `string` |  |
| `hits[].data.due_on` | `string` |  |
| `hits[].data.external` | `object` |  |
| `hits[].data.followers` | `array` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.hearted` | `boolean` |  |
| `hits[].data.hearts` | `array` |  |
| `hits[].data.html_notes` | `string` |  |
| `hits[].data.is_rendered_as_separator` | `boolean` |  |
| `hits[].data.liked` | `boolean` |  |
| `hits[].data.likes` | `array` |  |
| `hits[].data.memberships` | `array` |  |
| `hits[].data.modified_at` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.notes` | `string` |  |
| `hits[].data.num_hearts` | `integer` |  |
| `hits[].data.num_likes` | `integer` |  |
| `hits[].data.num_subtasks` | `integer` |  |
| `hits[].data.parent` | `object` |  |
| `hits[].data.permalink_url` | `string` |  |
| `hits[].data.projects` | `array` |  |
| `hits[].data.resource_subtype` | `string` |  |
| `hits[].data.resource_type` | `string` |  |
| `hits[].data.start_on` | `string` |  |
| `hits[].data.tags` | `array` |  |
| `hits[].data.workspace` | `object` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Project Tasks

### Project Tasks List

Returns all tasks in a project

#### Python SDK

```python
await asana.project_tasks.list(
    project_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_tasks",
    "action": "list",
    "params": {
        "project_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | Project GID to list tasks from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `completed_since` | `string` | No | Only return tasks that have been completed since this time |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Workspace Task Search

### Workspace Task Search List

Returns tasks that match the specified search criteria. This endpoint requires a premium Asana account.

IMPORTANT: At least one search filter parameter must be provided. Valid filter parameters include: text, completed, assignee.any, projects.any, sections.any, teams.any, followers.any, created_at.after, created_at.before, modified_at.after, modified_at.before, due_on.after, due_on.before, and resource_subtype. The sort_by and sort_ascending parameters are for ordering results and do not count as search filters.


#### Python SDK

```python
await asana.workspace_task_search.list(
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_task_search",
    "action": "list",
    "params": {
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to search tasks in |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `text` | `string` | No | Search text to filter tasks |
| `completed` | `boolean` | No | Filter by completion status |
| `assignee.any` | `string` | No | Comma-separated list of assignee GIDs |
| `projects.any` | `string` | No | Comma-separated list of project GIDs |
| `sections.any` | `string` | No | Comma-separated list of section GIDs |
| `teams.any` | `string` | No | Comma-separated list of team GIDs |
| `followers.any` | `string` | No | Comma-separated list of follower GIDs |
| `created_at.after` | `string` | No | Filter tasks created after this date (ISO 8601 format) |
| `created_at.before` | `string` | No | Filter tasks created before this date (ISO 8601 format) |
| `modified_at.after` | `string` | No | Filter tasks modified after this date (ISO 8601 format) |
| `modified_at.before` | `string` | No | Filter tasks modified before this date (ISO 8601 format) |
| `due_on.after` | `string` | No | Filter tasks due after this date (ISO 8601 date format) |
| `due_on.before` | `string` | No | Filter tasks due before this date (ISO 8601 date format) |
| `resource_subtype` | `string` | No | Filter by task resource subtype (e.g., default_task, milestone) |
| `sort_by` | `string` | No | Field to sort by (e.g., created_at, modified_at, due_date) |
| `sort_ascending` | `boolean` | No | Sort order (true for ascending, false for descending) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Projects

### Projects List

Returns a paginated list of projects

#### Python SDK

```python
await asana.projects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `workspace` | `string` | No | The workspace to filter projects on |
| `team` | `string` | No | The team to filter projects on |
| `archived` | `boolean` | No | Filter by archived status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Projects Get

Get a single project by its ID

#### Python SDK

```python
await asana.projects.get(
    project_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "project_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | Project GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `archived` | `boolean` |  |
| `color` | `string \| null` |  |
| `completed` | `boolean` |  |
| `completed_at` | `string \| null` |  |
| `created_at` | `string` |  |
| `current_status` | `object \| null` |  |
| `current_status_update` | `object \| null` |  |
| `custom_fields` | `array` |  |
| `default_access_level` | `string` |  |
| `default_view` | `string` |  |
| `due_on` | `string \| null` |  |
| `due_date` | `string \| null` |  |
| `followers` | `array<object>` |  |
| `members` | `array<object>` |  |
| `minimum_access_level_for_customization` | `string` |  |
| `minimum_access_level_for_sharing` | `string` |  |
| `modified_at` | `string` |  |
| `name` | `string` |  |
| `notes` | `string` |  |
| `owner` | `object` |  |
| `permalink_url` | `string` |  |
| `privacy_setting` | `string` |  |
| `public` | `boolean` |  |
| `resource_type` | `string` |  |
| `start_on` | `string \| null` |  |
| `team` | `object` |  |
| `workspace` | `object` |  |


</details>

### Projects Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.projects.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` |  |
| `color` | `string` |  |
| `created_at` | `string` |  |
| `current_status` | `object` |  |
| `custom_field_settings` | `array` |  |
| `custom_fields` | `array` |  |
| `default_view` | `string` |  |
| `due_date` | `string` |  |
| `due_on` | `string` |  |
| `followers` | `array` |  |
| `gid` | `string` |  |
| `html_notes` | `string` |  |
| `icon` | `string` |  |
| `is_template` | `boolean` |  |
| `members` | `array` |  |
| `modified_at` | `string` |  |
| `name` | `string` |  |
| `notes` | `string` |  |
| `owner` | `object` |  |
| `permalink_url` | `string` |  |
| `public` | `boolean` |  |
| `resource_type` | `string` |  |
| `start_on` | `string` |  |
| `team` | `object` |  |
| `workspace` | `object` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.archived` | `boolean` |  |
| `hits[].data.color` | `string` |  |
| `hits[].data.created_at` | `string` |  |
| `hits[].data.current_status` | `object` |  |
| `hits[].data.custom_field_settings` | `array` |  |
| `hits[].data.custom_fields` | `array` |  |
| `hits[].data.default_view` | `string` |  |
| `hits[].data.due_date` | `string` |  |
| `hits[].data.due_on` | `string` |  |
| `hits[].data.followers` | `array` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.html_notes` | `string` |  |
| `hits[].data.icon` | `string` |  |
| `hits[].data.is_template` | `boolean` |  |
| `hits[].data.members` | `array` |  |
| `hits[].data.modified_at` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.notes` | `string` |  |
| `hits[].data.owner` | `object` |  |
| `hits[].data.permalink_url` | `string` |  |
| `hits[].data.public` | `boolean` |  |
| `hits[].data.resource_type` | `string` |  |
| `hits[].data.start_on` | `string` |  |
| `hits[].data.team` | `object` |  |
| `hits[].data.workspace` | `object` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Task Projects

### Task Projects List

Returns all projects a task is in

#### Python SDK

```python
await asana.task_projects.list(
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_projects",
    "action": "list",
    "params": {
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list projects from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Team Projects

### Team Projects List

Returns all projects for a team

#### Python SDK

```python
await asana.team_projects.list(
    team_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "team_projects",
    "action": "list",
    "params": {
        "team_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_gid` | `string` | Yes | Team GID to list projects from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `archived` | `boolean` | No | Filter by archived status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Workspace Projects

### Workspace Projects List

Returns all projects in a workspace

#### Python SDK

```python
await asana.workspace_projects.list(
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_projects",
    "action": "list",
    "params": {
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list projects from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `archived` | `boolean` | No | Filter by archived status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Workspaces

### Workspaces List

Returns a paginated list of workspaces

#### Python SDK

```python
await asana.workspaces.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Workspaces Get

Get a single workspace by its ID

#### Python SDK

```python
await asana.workspaces.get(
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "get",
    "params": {
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `email_domains` | `array<string>` |  |
| `is_organization` | `boolean` |  |


</details>

### Workspaces Search

Search and filter workspaces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.workspaces.search(
    query={"filter": {"eq": {"email_domains": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"email_domains": []}}}
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
| `email_domains` | `array` |  |
| `gid` | `string` |  |
| `is_organization` | `boolean` |  |
| `name` | `string` |  |
| `resource_type` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.email_domains` | `array` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.is_organization` | `boolean` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.resource_type` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Users

### Users List

Returns a paginated list of users

#### Python SDK

```python
await asana.users.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `workspace` | `string` | No | The workspace to filter users on |
| `team` | `string` | No | The team to filter users on |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Users Get

Get a single user by their ID

#### Python SDK

```python
await asana.users.get(
    user_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "user_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_gid` | `string` | Yes | User GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `email` | `string` |  |
| `name` | `string` |  |
| `photo` | `object \| null` |  |
| `resource_type` | `string` |  |
| `workspaces` | `array<object>` |  |


</details>

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.users.search(
    query={"filter": {"eq": {"email": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"email": "<str>"}}}
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
| `email` | `string` |  |
| `gid` | `string` |  |
| `name` | `string` |  |
| `photo` | `object` |  |
| `resource_type` | `string` |  |
| `workspaces` | `array` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.email` | `string` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.photo` | `object` |  |
| `hits[].data.resource_type` | `string` |  |
| `hits[].data.workspaces` | `array` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Workspace Users

### Workspace Users List

Returns all users in a workspace

#### Python SDK

```python
await asana.workspace_users.list(
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_users",
    "action": "list",
    "params": {
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list users from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Team Users

### Team Users List

Returns all users in a team

#### Python SDK

```python
await asana.team_users.list(
    team_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "team_users",
    "action": "list",
    "params": {
        "team_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_gid` | `string` | Yes | Team GID to list users from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Teams

### Teams Get

Get a single team by its ID

#### Python SDK

```python
await asana.teams.get(
    team_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "get",
    "params": {
        "team_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_gid` | `string` | Yes | Team GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `name` | `string` |  |
| `organization` | `object` |  |
| `permalink_url` | `string` |  |
| `resource_type` | `string` |  |


</details>

### Teams Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.teams.search(
    query={"filter": {"eq": {"description": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"description": "<str>"}}}
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
| `description` | `string` |  |
| `gid` | `string` |  |
| `html_description` | `string` |  |
| `name` | `string` |  |
| `organization` | `object` |  |
| `permalink_url` | `string` |  |
| `resource_type` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.description` | `string` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.html_description` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.organization` | `object` |  |
| `hits[].data.permalink_url` | `string` |  |
| `hits[].data.resource_type` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Workspace Teams

### Workspace Teams List

Returns all teams in a workspace

#### Python SDK

```python
await asana.workspace_teams.list(
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_teams",
    "action": "list",
    "params": {
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list teams from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## User Teams

### User Teams List

Returns all teams a user is a member of

#### Python SDK

```python
await asana.user_teams.list(
    user_gid="<str>",
    organization="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user_teams",
    "action": "list",
    "params": {
        "user_gid": "<str>",
        "organization": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_gid` | `string` | Yes | User GID to list teams from |
| `organization` | `string` | Yes | The workspace or organization to filter teams on |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Attachments

### Attachments List

Returns a list of attachments for an object (task, project, etc.)

#### Python SDK

```python
await asana.attachments.list(
    parent="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "list",
    "params": {
        "parent": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `parent` | `string` | Yes | Globally unique identifier for the object to fetch attachments for (e.g., a task GID) |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Attachments Get

Get details for a single attachment by its GID

#### Python SDK

```python
await asana.attachments.get(
    attachment_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "get",
    "params": {
        "attachment_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_gid` | `string` | Yes | Globally unique identifier for the attachment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_at` | `string` |  |
| `download_url` | `string \| null` |  |
| `permanent_url` | `string \| null` |  |
| `host` | `string` |  |
| `parent` | `object` |  |
| `view_url` | `string \| null` |  |
| `size` | `integer \| null` |  |


</details>

### Attachments Download

Downloads the file content of an attachment. This operation first retrieves the attachment
metadata to get the download_url, then downloads the file from that URL.


#### Python SDK

```python
async for chunk in asana.attachments.download(    attachment_gid="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "download",
    "params": {
        "attachment_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_gid` | `string` | Yes | Globally unique identifier for the attachment |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Attachments Search

Search and filter attachments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.attachments.search(
    query={"filter": {"eq": {"connected_to_app": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"connected_to_app": True}}}
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
| `connected_to_app` | `boolean` |  |
| `created_at` | `string` |  |
| `download_url` | `string` |  |
| `gid` | `string` |  |
| `host` | `string` |  |
| `name` | `string` |  |
| `parent` | `object` |  |
| `permanent_url` | `string` |  |
| `resource_subtype` | `string` |  |
| `resource_type` | `string` |  |
| `size` | `integer` |  |
| `view_url` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.connected_to_app` | `boolean` |  |
| `hits[].data.created_at` | `string` |  |
| `hits[].data.download_url` | `string` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.host` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.parent` | `object` |  |
| `hits[].data.permanent_url` | `string` |  |
| `hits[].data.resource_subtype` | `string` |  |
| `hits[].data.resource_type` | `string` |  |
| `hits[].data.size` | `integer` |  |
| `hits[].data.view_url` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Workspace Tags

### Workspace Tags List

Returns all tags in a workspace

#### Python SDK

```python
await asana.workspace_tags.list(
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_tags",
    "action": "list",
    "params": {
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list tags from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Tags

### Tags Get

Get a single tag by its ID

#### Python SDK

```python
await asana.tags.get(
    tag_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "get",
    "params": {
        "tag_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `tag_gid` | `string` | Yes | Tag GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `color` | `string` |  |
| `created_at` | `string` |  |
| `followers` | `array` |  |
| `notes` | `string` |  |
| `permalink_url` | `string` |  |
| `workspace` | `object` |  |


</details>

### Tags Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.tags.search(
    query={"filter": {"eq": {"color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"color": "<str>"}}}
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
| `color` | `string` |  |
| `followers` | `array` |  |
| `gid` | `string` |  |
| `name` | `string` |  |
| `permalink_url` | `string` |  |
| `resource_type` | `string` |  |
| `workspace` | `object` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.color` | `string` |  |
| `hits[].data.followers` | `array` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.permalink_url` | `string` |  |
| `hits[].data.resource_type` | `string` |  |
| `hits[].data.workspace` | `object` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Project Sections

### Project Sections List

Returns all sections in a project

#### Python SDK

```python
await asana.project_sections.list(
    project_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_sections",
    "action": "list",
    "params": {
        "project_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | Project GID to list sections from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Sections

### Sections Get

Get a single section by its ID

#### Python SDK

```python
await asana.sections.get(
    section_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sections",
    "action": "get",
    "params": {
        "section_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `section_gid` | `string` | Yes | Section GID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `created_at` | `string` |  |
| `project` | `object` |  |


</details>

### Sections Search

Search and filter sections records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.sections.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sections",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"created_at": "<str>"}}}
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
| `created_at` | `string` |  |
| `gid` | `string` |  |
| `name` | `string` |  |
| `project` | `object` |  |
| `resource_type` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.created_at` | `string` |  |
| `hits[].data.gid` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.project` | `object` |  |
| `hits[].data.resource_type` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Task Subtasks

### Task Subtasks List

Returns all subtasks of a task

#### Python SDK

```python
await asana.task_subtasks.list(
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_subtasks",
    "action": "list",
    "params": {
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list subtasks from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Task Dependencies

### Task Dependencies List

Returns all tasks that this task depends on

#### Python SDK

```python
await asana.task_dependencies.list(
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_dependencies",
    "action": "list",
    "params": {
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list dependencies from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

## Task Dependents

### Task Dependents List

Returns all tasks that depend on this task

#### Python SDK

```python
await asana.task_dependents.list(
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_dependents",
    "action": "list",
    "params": {
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list dependents from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

