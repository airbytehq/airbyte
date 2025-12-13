# Linear

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Issues | [List](#issues-list), [Get](#issues-get) |
| Projects | [List](#projects-list), [Get](#projects-get) |
| Teams | [List](#teams-list), [Get](#teams-get) |

### Issues

#### Issues List

Returns a paginated list of issues via GraphQL with pagination support

**Python SDK**

```python
linear.issues.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list"
}'
```


**Params**

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
linear.issues.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Params**

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

### Projects

#### Projects List

Returns a paginated list of projects via GraphQL with pagination support

**Python SDK**

```python
linear.projects.list()
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
linear.projects.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


**Params**

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
linear.teams.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list"
}'
```


**Params**

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
linear.teams.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


**Params**

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



## Authentication

The Linear connector supports the following authentication methods:


### Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | API authentication key |

#### Example

**Python SDK**

```python
LinearConnector(
  auth_config=LinearAuthConfig(
    api_key="<API authentication key>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "1c5d8316-ed42-4473-8fbc-2626f03f070c",
  "auth_config": {
    "api_key": "<API authentication key>"
  },
  "name": "My Linear Connector"
}'
```

