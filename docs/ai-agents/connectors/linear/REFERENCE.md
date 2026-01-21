# Linear full reference

This is the full reference documentation for the Linear agent connector.

## Supported entities and actions

The Linear connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [List](#issues-list), [Get](#issues-get), [Create](#issues-create), [Update](#issues-update) |
| Projects | [List](#projects-list), [Get](#projects-get) |
| Teams | [List](#teams-list), [Get](#teams-get) |
| Comments | [List](#comments-list), [Get](#comments-get), [Create](#comments-create), [Update](#comments-update) |

### Issues

#### Issues List

Returns a paginated list of issues via GraphQL with pagination support

**Python SDK**

```python
await linear.issues.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Issues Get

Get a single issue by ID via GraphQL

**Python SDK**

```python
await linear.issues.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Issue ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Issues Create

Create a new issue via GraphQL mutation

**Python SDK**

```python
await linear.issues.create(
    team_id="<str>",
    title="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "create",
    "params": {
        "teamId": "<str>",
        "title": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `teamId` | `string` | Yes | The ID of the team to create the issue in |
| `title` | `string` | Yes | The title of the issue |
| `description` | `string` | No | The description of the issue (supports markdown) |
| `stateId` | `string` | No | The ID of the workflow state for the issue |
| `priority` | `integer` | No | The priority of the issue (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Issues Update

Update an existing issue via GraphQL mutation. All fields except id are optional for partial updates.

**Python SDK**

```python
await linear.issues.update(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "update",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the issue to update |
| `title` | `string` | No | The new title of the issue |
| `description` | `string` | No | The new description of the issue (supports markdown) |
| `stateId` | `string` | No | The ID of the new workflow state for the issue |
| `priority` | `integer` | No | The new priority of the issue (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Projects

#### Projects List

Returns a paginated list of projects via GraphQL with pagination support

**Python SDK**

```python
await linear.projects.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Projects Get

Get a single project by ID via GraphQL

**Python SDK**

```python
await linear.projects.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Project ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Teams

#### Teams List

Returns a list of teams via GraphQL with pagination support

**Python SDK**

```python
await linear.teams.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Teams Get

Get a single team by ID via GraphQL

**Python SDK**

```python
await linear.teams.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Team ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Comments

#### Comments List

Returns a paginated list of comments for an issue via GraphQL

**Python SDK**

```python
await linear.comments.list(
    issue_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "list",
    "params": {
        "issueId": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueId` | `string` | Yes | Issue ID to get comments for |
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Comments Get

Get a single comment by ID via GraphQL

**Python SDK**

```python
await linear.comments.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Comment ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Comments Create

Create a new comment on an issue via GraphQL mutation

**Python SDK**

```python
await linear.comments.create(
    issue_id="<str>",
    body="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "create",
    "params": {
        "issueId": "<str>",
        "body": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueId` | `string` | Yes | The ID of the issue to add the comment to |
| `body` | `string` | Yes | The comment content in markdown |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

#### Comments Update

Update an existing comment via GraphQL mutation

**Python SDK**

```python
await linear.comments.update(
    id="<str>",
    body="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "update",
    "params": {
        "id": "<str>",
        "body": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the comment to update |
| `body` | `string` | Yes | The new comment content in markdown |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>



## Authentication

The Linear connector supports the following authentication methods.


### Linear API Key Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Linear API key from Settings > API > Personal API keys |

#### Example

**Python SDK**

```python
LinearConnector(
  auth_config=LinearAuthConfig(
    api_key="<Your Linear API key from Settings > API > Personal API keys>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/sources' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "workspace_id": "{your_workspace_id}",
  "source_template_id": "{source_template_id}",
  "auth_config": {
    "api_key": "<Your Linear API key from Settings > API > Personal API keys>"
  },
  "name": "My Linear Connector"
}'
```

