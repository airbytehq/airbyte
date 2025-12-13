# Asana

## Supported Entities and Actions

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

### Tasks

#### Tasks List

Returns a paginated list of tasks

**Python SDK**

```python
asana.tasks.list()
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


**Params**

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
asana.tasks.get(
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


**Params**

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
asana.project_tasks.list(
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


**Params**

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

Returns tasks that match the specified search criteria. Note - This endpoint requires a premium Asana account.

**Python SDK**

```python
asana.workspace_task_search.list(
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


**Params**

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
asana.projects.list()
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


**Params**

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
asana.projects.get(
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


**Params**

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
asana.task_projects.list(
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


**Params**

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
asana.team_projects.list(
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


**Params**

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
asana.workspace_projects.list(
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


**Params**

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
asana.workspaces.list()
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


**Params**

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
asana.workspaces.get(
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


**Params**

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
asana.users.list()
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


**Params**

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
asana.users.get(
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


**Params**

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
asana.workspace_users.list(
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


**Params**

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
asana.team_users.list(
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


**Params**

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
asana.teams.get(
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


**Params**

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
asana.workspace_teams.list(
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


**Params**

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
asana.user_teams.list(
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


**Params**

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



## Authentication

The Asana connector supports the following authentication methods:


### Asana OAuth 2.0

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth access token for API requests |
| `refresh_token` | `str` | Yes | OAuth refresh token for automatic token renewal |
| `client_id` | `str` | Yes | Connected App Consumer Key |
| `client_secret` | `str` | Yes | Connected App Consumer Secret |

#### Example

**Python SDK**

```python
AsanaConnector(
  auth_config=AsanaAuthConfig(
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

