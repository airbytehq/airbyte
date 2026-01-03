# Asana full reference

This is the full reference documentation for the Asana agent connector.

## Supported entities and actions

The Asana connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Tasks | [List](#tasks-list), [Get](#tasks-get) |
| Project Tasks | [List](#project-tasks-list) |
| Workspace Task Search | [List](#workspace-task-search-list) |
| Projects | [List](#projects-list), [Get](#projects-get) |
| Task Projects | [List](#task-projects-list) |
| Team Projects | [List](#team-projects-list) |
| Workspace Projects | [List](#workspace-projects-list) |
| Workspaces | [List](#workspaces-list), [Get](#workspaces-get) |
| Users | [List](#users-list), [Get](#users-get) |
| Workspace Users | [List](#workspace-users-list) |
| Team Users | [List](#team-users-list) |
| Teams | [Get](#teams-get) |
| Workspace Teams | [List](#workspace-teams-list) |
| User Teams | [List](#user-teams-list) |
| Attachments | [List](#attachments-list), [Get](#attachments-get), [Download](#attachments-download) |
| Workspace Tags | [List](#workspace-tags-list) |
| Tags | [Get](#tags-get) |
| Project Sections | [List](#project-sections-list) |
| Sections | [Get](#sections-get) |
| Task Subtasks | [List](#task-subtasks-list) |
| Task Dependencies | [List](#task-dependencies-list) |
| Task Dependents | [List](#task-dependents-list) |

### Tasks

#### Tasks List

Returns a paginated list of tasks. Must include either a project OR a section OR a workspace AND assignee parameter.

**Python SDK**

```python
await asana.tasks.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list"
}'
```


**Parameters**

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

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

#### Tasks Get

Get a single task by its ID

**Python SDK**

```python
await asana.tasks.get(
    task_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |


</details>

### Project Tasks

#### Project Tasks List

Returns all tasks in a project

**Python SDK**

```python
await asana.project_tasks.list(
    project_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | Project GID to list tasks from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `completed_since` | `string` | No | Only return tasks that have been completed since this time |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Workspace Task Search

#### Workspace Task Search List

Returns tasks that match the specified search criteria. Note - This endpoint requires a premium Asana account. At least one search parameter must be provided.

**Python SDK**

```python
await asana.workspace_task_search.list(
    workspace_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

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

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Projects

#### Projects List

Returns a paginated list of projects

**Python SDK**

```python
await asana.projects.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `workspace` | `string` | No | The workspace to filter projects on |
| `team` | `string` | No | The team to filter projects on |
| `archived` | `boolean` | No | Filter by archived status |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

#### Projects Get

Get a single project by its ID

**Python SDK**

```python
await asana.projects.get(
    project_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | Project GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Task Projects

#### Task Projects List

Returns all projects a task is in

**Python SDK**

```python
await asana.task_projects.list(
    task_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list projects from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Team Projects

#### Team Projects List

Returns all projects for a team

**Python SDK**

```python
await asana.team_projects.list(
    team_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_gid` | `string` | Yes | Team GID to list projects from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `archived` | `boolean` | No | Filter by archived status |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Workspace Projects

#### Workspace Projects List

Returns all projects in a workspace

**Python SDK**

```python
await asana.workspace_projects.list(
    workspace_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list projects from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `archived` | `boolean` | No | Filter by archived status |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Workspaces

#### Workspaces List

Returns a paginated list of workspaces

**Python SDK**

```python
await asana.workspaces.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

#### Workspaces Get

Get a single workspace by its ID

**Python SDK**

```python
await asana.workspaces.get(
    workspace_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `email_domains` | `array<string>` |  |
| `is_organization` | `boolean` |  |


</details>

### Users

#### Users List

Returns a paginated list of users

**Python SDK**

```python
await asana.users.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |
| `workspace` | `string` | No | The workspace to filter users on |
| `team` | `string` | No | The team to filter users on |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

#### Users Get

Get a single user by their ID

**Python SDK**

```python
await asana.users.get(
    user_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_gid` | `string` | Yes | User GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `email` | `string` |  |
| `name` | `string` |  |
| `photo` | `object \| null` |  |
| `resource_type` | `string` |  |
| `workspaces` | `array<object>` |  |


</details>

### Workspace Users

#### Workspace Users List

Returns all users in a workspace

**Python SDK**

```python
await asana.workspace_users.list(
    workspace_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list users from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Team Users

#### Team Users List

Returns all users in a team

**Python SDK**

```python
await asana.team_users.list(
    team_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_gid` | `string` | Yes | Team GID to list users from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Teams

#### Teams Get

Get a single team by its ID

**Python SDK**

```python
await asana.teams.get(
    team_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `team_gid` | `string` | Yes | Team GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `name` | `string` |  |
| `organization` | `object` |  |
| `permalink_url` | `string` |  |
| `resource_type` | `string` |  |


</details>

### Workspace Teams

#### Workspace Teams List

Returns all teams in a workspace

**Python SDK**

```python
await asana.workspace_teams.list(
    workspace_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list teams from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### User Teams

#### User Teams List

Returns all teams a user is a member of

**Python SDK**

```python
await asana.user_teams.list(
    user_gid="<str>",
    organization="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_gid` | `string` | Yes | User GID to list teams from |
| `organization` | `string` | Yes | The workspace or organization to filter teams on |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Attachments

#### Attachments List

Returns a list of attachments for an object (task, project, etc.)

**Python SDK**

```python
await asana.attachments.list(
    parent="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `parent` | `string` | Yes | Globally unique identifier for the object to fetch attachments for (e.g., a task GID) |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

#### Attachments Get

Get details for a single attachment by its GID

**Python SDK**

```python
await asana.attachments.get(
    attachment_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_gid` | `string` | Yes | Globally unique identifier for the attachment |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

#### Attachments Download

Downloads the file content of an attachment. This operation first retrieves the attachment
metadata to get the download_url, then downloads the file from that URL.


**Python SDK**

```python
async for chunk in asana.attachments.download(    attachment_gid="<str>"):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_gid` | `string` | Yes | Globally unique identifier for the attachment |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Workspace Tags

#### Workspace Tags List

Returns all tags in a workspace

**Python SDK**

```python
await asana.workspace_tags.list(
    workspace_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace_gid` | `string` | Yes | Workspace GID to list tags from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Tags

#### Tags Get

Get a single tag by its ID

**Python SDK**

```python
await asana.tags.get(
    tag_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `tag_gid` | `string` | Yes | Tag GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Project Sections

#### Project Sections List

Returns all sections in a project

**Python SDK**

```python
await asana.project_sections.list(
    project_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_gid` | `string` | Yes | Project GID to list sections from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Sections

#### Sections Get

Get a single section by its ID

**Python SDK**

```python
await asana.sections.get(
    section_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `section_gid` | `string` | Yes | Section GID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `created_at` | `string` |  |
| `project` | `object` |  |


</details>

### Task Subtasks

#### Task Subtasks List

Returns all subtasks of a task

**Python SDK**

```python
await asana.task_subtasks.list(
    task_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list subtasks from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Task Dependencies

#### Task Dependencies List

Returns all tasks that this task depends on

**Python SDK**

```python
await asana.task_dependencies.list(
    task_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list dependencies from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>

### Task Dependents

#### Task Dependents List

Returns all tasks that depend on this task

**Python SDK**

```python
await asana.task_dependents.list(
    task_gid="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `task_gid` | `string` | Yes | Task GID to list dependents from |
| `limit` | `integer` | No | Number of items to return per page |
| `offset` | `string` | No | Pagination offset token |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `gid` | `string` |  |
| `resource_type` | `string` |  |
| `name` | `string` |  |
| `resource_subtype` | `string` |  |
| `created_by` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `object \| null` |  |

</details>



## Authentication

The Asana connector supports the following authentication methods.


### OAuth 2

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | No | OAuth access token for API requests |
| `refresh_token` | `str` | Yes | OAuth refresh token for automatic token renewal |
| `client_id` | `str` | Yes | Connected App Consumer Key |
| `client_secret` | `str` | Yes | Connected App Consumer Secret |

#### Example

**Python SDK**

```python
AsanaConnector(
  auth_config=AsanaOauth2AuthConfig(
    access_token="<OAuth access token for API requests>",
    refresh_token="<OAuth refresh token for automatic token renewal>",
    client_id="<Connected App Consumer Key>",
    client_secret="<Connected App Consumer Secret>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "d0243522-dccf-4978-8ba0-37ed47a0bdbf",
  "auth_config": {
    "access_token": "<OAuth access token for API requests>",
    "refresh_token": "<OAuth refresh token for automatic token renewal>",
    "client_id": "<Connected App Consumer Key>",
    "client_secret": "<Connected App Consumer Secret>"
  },
  "name": "My Asana Connector"
}'
```


### Personal Access Token

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `token` | `str` | Yes | Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps |

#### Example

**Python SDK**

```python
AsanaConnector(
  auth_config=AsanaPersonalAccessTokenAuthConfig(
    token="<Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "d0243522-dccf-4978-8ba0-37ed47a0bdbf",
  "auth_config": {
    "token": "<Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps>"
  },
  "name": "My Asana Connector"
}'
```

