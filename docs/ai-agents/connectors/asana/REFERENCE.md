# Asana full reference

This is the full reference documentation for the Asana agent connector.

## Supported entities and actions

The Asana connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Tasks | [List](#tasks-list), [Create](#tasks-create), [Get](#tasks-get), [Update](#tasks-update), [Delete](#tasks-delete), [Context Store Search](#tasks-context-store-search) |
| Project Tasks | [List](#project-tasks-list) |
| Workspace Task Search | [List](#workspace-task-search-list) |
| Projects | [List](#projects-list), [Create](#projects-create), [Get](#projects-get), [Update](#projects-update), [Delete](#projects-delete), [Context Store Search](#projects-context-store-search) |
| Task Projects | [List](#task-projects-list) |
| Team Projects | [List](#team-projects-list) |
| Workspace Projects | [List](#workspace-projects-list) |
| Workspaces | [List](#workspaces-list), [Get](#workspaces-get), [Context Store Search](#workspaces-context-store-search) |
| Users | [List](#users-list), [Get](#users-get), [Context Store Search](#users-context-store-search) |
| Workspace Users | [List](#workspace-users-list) |
| Team Users | [List](#team-users-list) |
| Teams | [Get](#teams-get), [Context Store Search](#teams-context-store-search) |
| Workspace Teams | [List](#workspace-teams-list) |
| User Teams | [List](#user-teams-list) |
| Attachments | [List](#attachments-list), [Get](#attachments-get), [Download](#attachments-download), [Context Store Search](#attachments-context-store-search) |
| Workspace Tags | [List](#workspace-tags-list), [Create](#workspace-tags-create) |
| Tags | [Get](#tags-get), [Update](#tags-update), [Delete](#tags-delete), [Context Store Search](#tags-context-store-search) |
| Tag Tasks | [List](#tag-tasks-list) |
| Project Sections | [List](#project-sections-list), [Create](#project-sections-create) |
| Sections | [Get](#sections-get), [Update](#sections-update), [Delete](#sections-delete), [Context Store Search](#sections-context-store-search) |
| Section Tasks | [List](#section-tasks-list), [Create](#section-tasks-create) |
| Task Subtasks | [List](#task-subtasks-list) |
| Task Dependencies | [List](#task-dependencies-list) |
| Task Dependents | [List](#task-dependents-list) |
| Task Stories | [Create](#task-stories-create) |
| Task Tags | [Create](#task-tags-create), [Delete](#task-tags-delete) |
| Workspace Memberships | [Create](#workspace-memberships-create) |

## Tasks

### Tasks List

Returns a paginated list of tasks. Must include either a project OR a section OR a workspace AND assignee parameter.

#### Python SDK

```python
await asana.tasks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Tasks Create

Creates a new task. Every task is required to be created in a specific workspace,
and this workspace cannot be changed once set. The workspace need not be set explicitly
if you specify projects or a parent task instead.


#### Python SDK

```python
await asana.tasks.create(
    data={
        "name": "<str>",
        "workspace": "<str>"
    }
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "create",
    "params": {
        "data": {
            "name": "<str>",
            "workspace": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | Yes | Name of the task |
| `data.workspace` | `string` | Yes | GID of the workspace to create the task in |
| `data.projects` | `array<string>` | No | Array of project GIDs to add the task to |
| `data.assignee` | `string` | No | GID of the user to assign the task to, or 'me' for the current user |
| `data.notes` | `string` | No | Free-form textual description of the task (plain text, no formatting) |
| `data.html_notes` | `string` | No | HTML-formatted description of the task |
| `data.due_on` | `string` | No | Due date in YYYY-MM-DD format |
| `data.due_at` | `string` | No | Due date and time in ISO 8601 format (e.g., 2025-03-20T12:00:00.000Z) |
| `data.start_on` | `string` | No | Start date in YYYY-MM-DD format |
| `data.completed` | `boolean` | No | Whether the task is completed |
| `data.parent` | `string` | No | GID of the parent task (to create a subtask) |
| `data.tags` | `array<string>` | No | Array of tag GIDs to add to the task |
| `data.followers` | `array<string>` | No | Array of user GIDs to add as followers |
| `data.resource_subtype` | `"default_task" \| "milestone" \| "section" \| "approval"` | No | The subtype of the task: default_task, milestone, section, or approval |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |


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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Tasks Update

Updates an existing task. Only the fields provided in the data block will be updated;
any unspecified fields will remain unchanged. When using this method, it is best to
specify only those fields you wish to change.


#### Python SDK

```python
await asana.tasks.update(
    data={},
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "update",
    "params": {
        "data": {},
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | No | Name of the task |
| `data.assignee` | `string` | No | GID of the user to assign the task to, or 'me' for the current user |
| `data.notes` | `string` | No | Free-form textual description of the task (plain text, no formatting) |
| `data.html_notes` | `string` | No | HTML-formatted description of the task |
| `data.due_on` | `string` | No | Due date in YYYY-MM-DD format |
| `data.due_at` | `string` | No | Due date and time in ISO 8601 format (e.g., 2025-03-20T12:00:00.000Z) |
| `data.start_on` | `string` | No | Start date in YYYY-MM-DD format |
| `data.completed` | `boolean` | No | Whether the task is completed |
| `task_gid` | `string` | Yes | The task to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |


</details>

### Tasks Delete

Deletes a specific, existing task. Deleted tasks go into the trash of the user
making the delete request. Tasks can be recovered from the trash within 30 days;
afterward they are completely removed from the system.


#### Python SDK

```python
await asana.tasks.delete(
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "delete",
    "params": {
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | The task to delete |


### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.tasks.context_store_search(
    query={"filter": {"eq": {"actual_time_minutes": 0}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actual_time_minutes` | `integer` | The actual time spent on the task in minutes |
| `data[].approval_status` | `string` |  |
| `data[].assignee` | `object` |  |
| `data[].completed` | `boolean` |  |
| `data[].completed_at` | `string` |  |
| `data[].completed_by` | `object` |  |
| `data[].created_at` | `string` |  |
| `data[].custom_fields` | `array` |  |
| `data[].dependencies` | `array` |  |
| `data[].dependents` | `array` |  |
| `data[].due_at` | `string` |  |
| `data[].due_on` | `string` |  |
| `data[].external` | `object` |  |
| `data[].followers` | `array` |  |
| `data[].gid` | `string` |  |
| `data[].hearted` | `boolean` |  |
| `data[].hearts` | `array` |  |
| `data[].html_notes` | `string` |  |
| `data[].is_rendered_as_separator` | `boolean` |  |
| `data[].liked` | `boolean` |  |
| `data[].likes` | `array` |  |
| `data[].memberships` | `array` |  |
| `data[].modified_at` | `string` |  |
| `data[].name` | `string` |  |
| `data[].notes` | `string` |  |
| `data[].num_hearts` | `integer` |  |
| `data[].num_likes` | `integer` |  |
| `data[].num_subtasks` | `integer` |  |
| `data[].parent` | `object` |  |
| `data[].permalink_url` | `string` |  |
| `data[].projects` | `array` |  |
| `data[].resource_subtype` | `string` |  |
| `data[].resource_type` | `string` |  |
| `data[].start_on` | `string` |  |
| `data[].tags` | `array` |  |
| `data[].workspace` | `object` |  |

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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Projects Create

Create a new project in a workspace or team. Every project is required to be
created in a specific workspace or organization, and this cannot be changed once set.


#### Python SDK

```python
await asana.projects.create(
    data={
        "name": "<str>",
        "workspace": "<str>"
    }
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "create",
    "params": {
        "data": {
            "name": "<str>",
            "workspace": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | Yes | Name of the project |
| `data.workspace` | `string` | Yes | GID of the workspace to create the project in |
| `data.team` | `string` | No | GID of the team to share the project with (required for organizations) |
| `data.notes` | `string` | No | Free-form textual description of the project (plain text) |
| `data.html_notes` | `string` | No | HTML-formatted description of the project |
| `data.color` | `string` | No | Color of the project (e.g., dark-pink, dark-green, dark-blue, dark-red, dark-teal, dark-brown, dark-orange, dark-purple, dark-warm-gray, light-pink, light-green, light-blue, light-red, light-teal, light-brown, light-orange, light-purple, light-warm-gray, none) |
| `data.default_view` | `"list" \| "board" \| "calendar" \| "timeline"` | No | The default view of the project (list, board, calendar, timeline) |
| `data.due_on` | `string` | No | Due date in YYYY-MM-DD format |
| `data.start_on` | `string` | No | Start date in YYYY-MM-DD format |
| `data.privacy_setting` | `"public_to_workspace" \| "private"` | No | Privacy setting: public_to_workspace or private |
| `data.archived` | `boolean` | No | Whether the project is archived |


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
| `team` | `object \| null` |  |
| `workspace` | `object` |  |
| `icon` | `string \| null` |  |
| `completed_by` | `object \| null` |  |


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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `team` | `object \| null` |  |
| `workspace` | `object` |  |
| `icon` | `string \| null` |  |
| `completed_by` | `object \| null` |  |


</details>

### Projects Update

Updates an existing project. Only the fields provided in the data block will be updated;
any unspecified fields will remain unchanged. When using this method, it is best to
specify only those fields you wish to change.


#### Python SDK

```python
await asana.projects.update(
    data={},
    project_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "update",
    "params": {
        "data": {},
        "project_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | No | Name of the project |
| `data.notes` | `string` | No | Free-form textual description of the project (plain text) |
| `data.html_notes` | `string` | No | HTML-formatted description of the project |
| `data.color` | `string` | No | Color of the project |
| `data.default_view` | `"list" \| "board" \| "calendar" \| "timeline"` | No | The default view of the project (list, board, calendar, timeline) |
| `data.due_on` | `string` | No | Due date in YYYY-MM-DD format |
| `data.start_on` | `string` | No | Start date in YYYY-MM-DD format |
| `data.archived` | `boolean` | No | Whether the project is archived |
| `project_gid` | `string` | Yes | The project to update |


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
| `team` | `object \| null` |  |
| `workspace` | `object` |  |
| `icon` | `string \| null` |  |
| `completed_by` | `object \| null` |  |


</details>

### Projects Delete

Deletes a specific, existing project. Returns an empty data record.


#### Python SDK

```python
await asana.projects.delete(
    project_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "delete",
    "params": {
        "project_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | The project to delete |


### Projects Context Store Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.projects.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` |  |
| `data[].color` | `string` |  |
| `data[].created_at` | `string` |  |
| `data[].current_status` | `object` |  |
| `data[].custom_field_settings` | `array` |  |
| `data[].custom_fields` | `array` |  |
| `data[].default_view` | `string` |  |
| `data[].due_date` | `string` |  |
| `data[].due_on` | `string` |  |
| `data[].followers` | `array` |  |
| `data[].gid` | `string` |  |
| `data[].html_notes` | `string` |  |
| `data[].icon` | `string` |  |
| `data[].is_template` | `boolean` |  |
| `data[].members` | `array` |  |
| `data[].modified_at` | `string` |  |
| `data[].name` | `string` |  |
| `data[].notes` | `string` |  |
| `data[].owner` | `object` |  |
| `data[].permalink_url` | `string` |  |
| `data[].public` | `boolean` |  |
| `data[].resource_type` | `string` |  |
| `data[].start_on` | `string` |  |
| `data[].team` | `object` |  |
| `data[].workspace` | `object` |  |

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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Workspaces Context Store Search

Search and filter workspaces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.workspaces.context_store_search(
    query={"filter": {"eq": {"email_domains": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].email_domains` | `array` |  |
| `data[].gid` | `string` |  |
| `data[].is_organization` | `boolean` |  |
| `data[].name` | `string` |  |
| `data[].resource_type` | `string` |  |

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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.users.context_store_search(
    query={"filter": {"eq": {"email": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].email` | `string` |  |
| `data[].gid` | `string` |  |
| `data[].name` | `string` |  |
| `data[].photo` | `object` |  |
| `data[].resource_type` | `string` |  |
| `data[].workspaces` | `array` |  |

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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Teams Context Store Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.teams.context_store_search(
    query={"filter": {"eq": {"description": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].description` | `string` |  |
| `data[].gid` | `string` |  |
| `data[].html_description` | `string` |  |
| `data[].name` | `string` |  |
| `data[].organization` | `object` |  |
| `data[].permalink_url` | `string` |  |
| `data[].resource_type` | `string` |  |

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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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


### Attachments Context Store Search

Search and filter attachments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.attachments.context_store_search(
    query={"filter": {"eq": {"connected_to_app": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].connected_to_app` | `boolean` |  |
| `data[].created_at` | `string` |  |
| `data[].download_url` | `string` |  |
| `data[].gid` | `string` |  |
| `data[].host` | `string` |  |
| `data[].name` | `string` |  |
| `data[].parent` | `object` |  |
| `data[].permanent_url` | `string` |  |
| `data[].resource_subtype` | `string` |  |
| `data[].resource_type` | `string` |  |
| `data[].size` | `integer` |  |
| `data[].view_url` | `string` |  |

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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Workspace Tags Create

Creates a new tag in a workspace or organization. Every tag is required to be
created in a specific workspace or organization, and this cannot be changed once set.
Returns the full record of the newly created tag.


#### Python SDK

```python
await asana.workspace_tags.create(
    data={
        "name": "<str>"
    },
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_tags",
    "action": "create",
    "params": {
        "data": {
            "name": "<str>"
        },
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | Yes | Name of the tag |
| `data.color` | `string` | No | Color of the tag. Must be one of: dark-pink, dark-green, dark-blue, dark-red, dark-teal, dark-brown, dark-orange, dark-purple, dark-warm-gray, light-pink, light-green, light-blue, light-red, light-teal, light-brown, light-orange, light-purple, light-warm-gray, none, null |
| `data.notes` | `string` | No | Free-form textual description of the tag |
| `workspace_gid` | `string` | Yes | Globally unique identifier for the workspace or organization |


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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Tags Update

Updates the properties of a tag. Only the fields provided in the data block will
be updated; any unspecified fields will remain unchanged. Returns the complete
updated tag record.


#### Python SDK

```python
await asana.tags.update(
    data={},
    tag_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "update",
    "params": {
        "data": {},
        "tag_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | No | Name of the tag |
| `data.color` | `string` | No | Color of the tag |
| `data.notes` | `string` | No | Free-form textual description of the tag |
| `tag_gid` | `string` | Yes | The tag to update |


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

### Tags Delete

A specific, existing tag can be deleted by making a DELETE request on the URL
for that tag. Returns an empty data record.


#### Python SDK

```python
await asana.tags.delete(
    tag_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "delete",
    "params": {
        "tag_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `tag_gid` | `string` | Yes | The tag to delete |


### Tags Context Store Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.tags.context_store_search(
    query={"filter": {"eq": {"color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].color` | `string` |  |
| `data[].followers` | `array` |  |
| `data[].gid` | `string` |  |
| `data[].name` | `string` |  |
| `data[].permalink_url` | `string` |  |
| `data[].resource_type` | `string` |  |
| `data[].workspace` | `object` |  |

</details>

## Tag Tasks

### Tag Tasks List

Returns the compact task records for all tasks with the given tag.
Tasks can have more than one tag at a time.


#### Python SDK

```python
await asana.tag_tasks.list(
    tag_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tag_tasks",
    "action": "list",
    "params": {
        "tag_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `tag_gid` | `string` | Yes | Globally unique identifier for the tag |
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Project Sections Create

Creates a new section in a project. Returns the full record of the newly created section.


#### Python SDK

```python
await asana.project_sections.create(
    data={
        "name": "<str>"
    },
    project_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_sections",
    "action": "create",
    "params": {
        "data": {
            "name": "<str>"
        },
        "project_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | Yes | The name of the section (this is displayed as the column header in board view) |
| `data.insert_before` | `string` | No | GID of a section in the same project before which the new section should be inserted. Cannot be provided together with insert_after. |
| `data.insert_after` | `string` | No | GID of a section in the same project after which the new section should be inserted. Cannot be provided together with insert_before. |
| `project_gid` | `string` | Yes | Globally unique identifier for the project |


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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

### Sections Update

A specific, existing section can be updated by making a PUT request on the URL for
that section. Only the fields provided in the data block will be updated; any unspecified
fields will remain unchanged. Currently only the name field can be updated.


#### Python SDK

```python
await asana.sections.update(
    data={},
    section_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sections",
    "action": "update",
    "params": {
        "data": {},
        "section_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.name` | `string` | No | The new name of the section |
| `section_gid` | `string` | Yes | The section to update |


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

### Sections Delete

A specific, existing section can be deleted by making a DELETE request on the URL
for that section. Note that sections must be empty to be deleted. The last remaining
section in a project cannot be deleted.


#### Python SDK

```python
await asana.sections.delete(
    section_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sections",
    "action": "delete",
    "params": {
        "section_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `section_gid` | `string` | Yes | The section to delete |


### Sections Context Store Search

Search and filter sections records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await asana.sections.context_store_search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sections",
    "action": "context_store_search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
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
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` |  |
| `data[].gid` | `string` |  |
| `data[].name` | `string` |  |
| `data[].project` | `object` |  |
| `data[].resource_type` | `string` |  |

</details>

## Section Tasks

### Section Tasks List

Returns the compact task records for all tasks within the given section.

#### Python SDK

```python
await asana.section_tasks.list(
    section_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "section_tasks",
    "action": "list",
    "params": {
        "section_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `section_gid` | `string` | Yes | The globally unique identifier for the section |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `completed_since` | `string` | No | Only return tasks that are either incomplete or that have been completed since this time |


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

### Section Tasks Create

Add a task to a specific, existing section. This will remove the task from other
sections of the project. The task will be inserted at the top of the section unless
an insert_before or insert_after parameter is declared.


#### Python SDK

```python
await asana.section_tasks.create(
    data={
        "task": "<str>"
    },
    section_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "section_tasks",
    "action": "create",
    "params": {
        "data": {
            "task": "<str>"
        },
        "section_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.task` | `string` | Yes | The GID of the task to add to this section |
| `data.insert_before` | `string` | No | GID of a task in this section before which the added task should be inserted. Cannot be provided together with insert_after. |
| `data.insert_after` | `string` | No | GID of a task in this section after which the added task should be inserted. Cannot be provided together with insert_before. |
| `section_gid` | `string` | Yes | The globally unique identifier for the section |


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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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

## Task Stories

### Task Stories Create

Adds a comment to a task. The comment will be authored by the currently
authenticated user, and timestamped when the server receives the request.


#### Python SDK

```python
await asana.task_stories.create(
    data={
        "text": "<str>"
    },
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_stories",
    "action": "create",
    "params": {
        "data": {
            "text": "<str>"
        },
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.text` | `string` | Yes | The plain text body of the comment |
| `data.html_text` | `string` | No | HTML-formatted body of the comment |
| `data.is_pinned` | `boolean` | No | Whether the story should be pinned on the resource |
| `task_gid` | `string` | Yes | The task to add a comment to |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `resource_subtype` | `string` |  |
| `text` | `string` |  |
| `html_text` | `string` |  |
| `is_pinned` | `boolean` |  |
| `created_at` | `string` |  |
| `created_by` | `object` |  |
| `target` | `object` |  |
| `type` | `string` |  |


</details>

## Task Tags

### Task Tags Create

Adds a tag to a task. Returns an empty data block.


#### Python SDK

```python
await asana.task_tags.create(
    data={
        "tag": "<str>"
    },
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_tags",
    "action": "create",
    "params": {
        "data": {
            "tag": "<str>"
        },
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.tag` | `string` | Yes | The GID of the tag to add to the task |
| `task_gid` | `string` | Yes | The task to operate on |


### Task Tags Delete

Removes a tag from a task. Returns an empty data block.


#### Python SDK

```python
await asana.task_tags.delete(
    data={
        "tag": "<str>"
    },
    task_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_tags",
    "action": "delete",
    "params": {
        "data": {
            "tag": "<str>"
        },
        "task_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.tag` | `string` | Yes | The GID of the tag to remove from the task |
| `task_gid` | `string` | Yes | The task to operate on |


## Workspace Memberships

### Workspace Memberships Create

Add a user to a workspace or organization. The user can be referenced by their
globally unique user ID or their email address. Returns the full user record
for the invited user.


#### Python SDK

```python
await asana.workspace_memberships.create(
    data={
        "user": "<str>"
    },
    workspace_gid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspace_memberships",
    "action": "create",
    "params": {
        "data": {
            "user": "<str>"
        },
        "workspace_gid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | Yes |  |
| `data.user` | `string` | Yes | A user GID or email address to add to the workspace |
| `workspace_gid` | `string` | Yes | The workspace or organization to add the user to |


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

