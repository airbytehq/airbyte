# Jira

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Issues | [Search](#issues-search), [Get](#issues-get) |
| Projects | [Search](#projects-search), [Get](#projects-get) |
| Users | [Get](#users-get), [List](#users-list), [Search](#users-search) |
| Issue Fields | [List](#issue-fields-list), [Search](#issue-fields-search) |
| Issue Comments | [List](#issue-comments-list), [Get](#issue-comments-get) |
| Issue Worklogs | [List](#issue-worklogs-list), [Get](#issue-worklogs-get) |

### Issues

#### Issues Search

Retrieve issues based on JQL query with pagination support

**Python SDK**

```python
jira.issues.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "search"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `jql` | `string` | No | JQL query string to filter issues |
| `nextPageToken` | `string` | No | The token for a page to fetch that is not the first page. The first page has a nextPageToken of null. Use the `nextPageToken` to fetch the next page of issues. The `nextPageToken` field is not included in the response for the last page, indicating there is no next page. |
| `maxResults` | `integer` | No | The maximum number of items to return per page. To manage page size, API may return fewer items per page where a large number of fields or properties are requested. The greatest number of items returned per page is achieved when requesting `id` or `key` only. It returns max 5000 issues. |
| `fields` | `string` | No | A comma-separated list of fields to return for each issue. By default, all navigable fields are returned. To get a list of all fields, use the Get fields operation. |
| `expand` | `string` | No | A comma-separated list of parameters to expand. This parameter accepts multiple values, including `renderedFields`, `names`, `schema`, `transitions`, `operations`, `editmeta`, `changelog`, and `versionedRepresentations`. |
| `properties` | `string` | No | A comma-separated list of issue property keys. To get a list of all issue property keys, use the Get issue operation. A maximum of 5 properties can be requested. |
| `fieldsByKeys` | `boolean` | No | Whether the fields parameter contains field keys (true) or field IDs (false). Default is false. |
| `failFast` | `boolean` | No | Fail the request early if all field data cannot be retrieved. Default is false. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `fields` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `isLast` | `boolean \| null` |  |
| `total` | `integer` |  |

</details>

#### Issues Get

Retrieve a single issue by its ID or key

**Python SDK**

```python
jira.issues.get(
    issue_id_or_key="<str>"
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
        "issueIdOrKey": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `fields` | `string` | No | A comma-separated list of fields to return for the issue. By default, all navigable and Jira default fields are returned. Use it to retrieve a subset of fields. |
| `expand` | `string` | No | A comma-separated list of parameters to expand. This parameter accepts multiple values, including `renderedFields`, `names`, `schema`, `transitions`, `operations`, `editmeta`, `changelog`, and `versionedRepresentations`. |
| `properties` | `string` | No | A comma-separated list of issue property keys. To get a list of all issue property keys, use the Get issue operation. A maximum of 5 properties can be requested. |
| `fieldsByKeys` | `boolean` | No | Whether the fields parameter contains field keys (true) or field IDs (false). Default is false. |
| `updateHistory` | `boolean` | No | Whether the action taken is added to the user's Recent history. Default is false. |
| `failFast` | `boolean` | No | Fail the request early if all field data cannot be retrieved. Default is false. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `fields` | `object` |  |


</details>

### Projects

#### Projects Search

Search and filter projects with advanced query parameters

**Python SDK**

```python
jira.projects.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "search"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page (max 100) |
| `orderBy` | `"category" \| "-category" \| "+category" \| "key" \| "-key" \| "+key" \| "name" \| "-name" \| "+name" \| "owner" \| "-owner" \| "+owner" \| "issueCount" \| "-issueCount" \| "+issueCount" \| "lastIssueUpdatedDate" \| "-lastIssueUpdatedDate" \| "+lastIssueUpdatedDate" \| "archivedDate" \| "+archivedDate" \| "-archivedDate" \| "deletedDate" \| "+deletedDate" \| "-deletedDate"` | No | Order the results by a field (prefix with + for ascending, - for descending) |
| `id` | `array<integer>` | No | Filter by project IDs (up to 50) |
| `keys` | `array<string>` | No | Filter by project keys (up to 50) |
| `query` | `string` | No | Filter using a literal string (matches project key or name, case insensitive) |
| `typeKey` | `string` | No | Filter by project type (comma-separated) |
| `categoryId` | `integer` | No | Filter by project category ID |
| `action` | `"view" \| "browse" \| "edit" \| "create"` | No | Filter by user permission (view, browse, edit, create) |
| `expand` | `string` | No | Comma-separated list of additional fields (description, projectKeys, lead, issueTypes, url, insight) |
| `status` | `array<"live" \| "archived" \| "deleted">` | No | EXPERIMENTAL - Filter by project status |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `name` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `description` | `string \| null` |  |
| `lead` | `object \| null` |  |
| `avatarUrls` | `object` |  |
| `projectTypeKey` | `string` |  |
| `simplified` | `boolean` |  |
| `style` | `string` |  |
| `isPrivate` | `boolean` |  |
| `properties` | `object` |  |
| `projectCategory` | `object \| null` |  |
| `entityId` | `string \| null` |  |
| `uuid` | `string \| null` |  |
| `url` | `string \| null` |  |
| `assigneeType` | `string \| null` |  |
| `components` | `array \| null` |  |
| `issueTypes` | `array \| null` |  |
| `versions` | `array \| null` |  |
| `roles` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPage` | `string \| null` |  |
| `total` | `integer` |  |

</details>

#### Projects Get

Retrieve a single project by its ID or key

**Python SDK**

```python
jira.projects.get(
    project_id_or_key="<str>"
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
        "projectIdOrKey": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `projectIdOrKey` | `string` | Yes | The project ID or key (e.g., "PROJ" or "10000") |
| `expand` | `string` | No | Comma-separated list of additional fields to include (description, projectKeys, lead, issueTypes, url, insight) |
| `properties` | `string` | No | A comma-separated list of project property keys to return. To get a list of all project property keys, use Get project property keys. |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `name` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `description` | `string \| null` |  |
| `lead` | `object \| null` |  |
| `avatarUrls` | `object` |  |
| `projectTypeKey` | `string` |  |
| `simplified` | `boolean` |  |
| `style` | `string` |  |
| `isPrivate` | `boolean` |  |
| `properties` | `object` |  |
| `projectCategory` | `object \| null` |  |
| `entityId` | `string \| null` |  |
| `uuid` | `string \| null` |  |
| `url` | `string \| null` |  |
| `assigneeType` | `string \| null` |  |
| `components` | `array \| null` |  |
| `issueTypes` | `array \| null` |  |
| `versions` | `array \| null` |  |
| `roles` | `object \| null` |  |


</details>

### Users

#### Users Get

Retrieve a single user by their account ID

**Python SDK**

```python
jira.users.get(
    account_id="<str>"
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
        "accountId": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `accountId` | `string` | Yes | The account ID of the user |
| `expand` | `string` | No | Comma-separated list of additional fields to include (groups, applicationRoles) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `self` | `string` |  |
| `accountId` | `string` |  |
| `accountType` | `string` |  |
| `emailAddress` | `string \| null` |  |
| `avatarUrls` | `object` |  |
| `displayName` | `string` |  |
| `active` | `boolean` |  |
| `timeZone` | `string \| null` |  |
| `locale` | `string \| null` |  |
| `expand` | `string \| null` |  |
| `groups` | `object \| null` |  |
| `applicationRoles` | `object \| null` |  |


</details>

#### Users List

Returns a paginated list of users

**Python SDK**

```python
jira.users.list()
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
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page (max 1000) |


#### Users Search

Search for users using a query string

**Python SDK**

```python
jira.users.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "search"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | A query string to search for users (matches display name, email, account ID) |
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page (max 1000) |
| `accountId` | `string` | No | Filter by account IDs (supports multiple values) |
| `property` | `string` | No | Property key to filter users |


### Issue Fields

#### Issue Fields List

Returns a list of all custom and system fields

**Python SDK**

```python
jira.issue_fields.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_fields",
    "action": "list"
}'
```



#### Issue Fields Search

Search and filter issue fields with query parameters

**Python SDK**

```python
jira.issue_fields.search()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_fields",
    "action": "search"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page (max 100) |
| `type` | `array<"custom" \| "system">` | No | The type of fields to search for (custom, system, or both) |
| `id` | `array<string>` | No | List of field IDs to search for |
| `query` | `string` | No | String to match against field names, descriptions, and field IDs (case insensitive) |
| `orderBy` | `"contextsCount" \| "-contextsCount" \| "+contextsCount" \| "lastUsed" \| "-lastUsed" \| "+lastUsed" \| "name" \| "-name" \| "+name" \| "screensCount" \| "-screensCount" \| "+screensCount"` | No | Order the results by a field (contextsCount, lastUsed, name, screensCount) |
| `expand` | `string` | No | Comma-separated list of additional fields to include (searcherKey, screensCount, contextsCount, isLocked, lastUsed) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `maxResults` | `integer` |  |
| `startAt` | `integer` |  |
| `total` | `integer` |  |
| `isLast` | `boolean` |  |
| `values` | `array<object>` |  |
| `values[].id` | `string` |  |
| `values[].key` | `string \| null` |  |
| `values[].name` | `string` |  |
| `values[].custom` | `boolean \| null` |  |
| `values[].orderable` | `boolean \| null` |  |
| `values[].navigable` | `boolean \| null` |  |
| `values[].searchable` | `boolean \| null` |  |
| `values[].clauseNames` | `array \| null` |  |
| `values[].schema` | `object \| null` |  |
| `values[].untranslatedName` | `string \| null` |  |
| `values[].typeDisplayName` | `string \| null` |  |
| `values[].description` | `string \| null` |  |
| `values[].searcherKey` | `string \| null` |  |
| `values[].screensCount` | `integer \| null` |  |
| `values[].contextsCount` | `integer \| null` |  |
| `values[].isLocked` | `boolean \| null` |  |
| `values[].lastUsed` | `string \| null` |  |


</details>

### Issue Comments

#### Issue Comments List

Retrieve all comments for a specific issue

**Python SDK**

```python
jira.issue_comments.list(
    issue_id_or_key="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_comments",
    "action": "list",
    "params": {
        "issueIdOrKey": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page |
| `orderBy` | `"created" \| "-created" \| "+created"` | No | Order the results by created date (+ for ascending, - for descending) |
| `expand` | `string` | No | Comma-separated list of additional fields to include (renderedBody, properties) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `self` | `string` |  |
| `body` | `object` |  |
| `author` | `object` |  |
| `updateAuthor` | `object` |  |
| `created` | `string` |  |
| `updated` | `string` |  |
| `jsdPublic` | `boolean` |  |
| `visibility` | `object \| null` |  |
| `renderedBody` | `string \| null` |  |
| `properties` | `array \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `startAt` | `integer` |  |
| `maxResults` | `integer` |  |
| `total` | `integer` |  |

</details>

#### Issue Comments Get

Retrieve a single comment by its ID

**Python SDK**

```python
jira.issue_comments.get(
    issue_id_or_key="<str>",
    comment_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_comments",
    "action": "get",
    "params": {
        "issueIdOrKey": "<str>",
        "commentId": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `commentId` | `string` | Yes | The comment ID |
| `expand` | `string` | No | Comma-separated list of additional fields to include (renderedBody, properties) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `self` | `string` |  |
| `body` | `object` |  |
| `author` | `object` |  |
| `updateAuthor` | `object` |  |
| `created` | `string` |  |
| `updated` | `string` |  |
| `jsdPublic` | `boolean` |  |
| `visibility` | `object \| null` |  |
| `renderedBody` | `string \| null` |  |
| `properties` | `array \| null` |  |


</details>

### Issue Worklogs

#### Issue Worklogs List

Retrieve all worklogs for a specific issue

**Python SDK**

```python
jira.issue_worklogs.list(
    issue_id_or_key="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_worklogs",
    "action": "list",
    "params": {
        "issueIdOrKey": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page |
| `expand` | `string` | No | Comma-separated list of additional fields to include (properties) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `self` | `string` |  |
| `author` | `object` |  |
| `updateAuthor` | `object` |  |
| `comment` | `object` |  |
| `created` | `string` |  |
| `updated` | `string` |  |
| `started` | `string` |  |
| `timeSpent` | `string` |  |
| `timeSpentSeconds` | `integer` |  |
| `issueId` | `string` |  |
| `visibility` | `object \| null` |  |
| `properties` | `array \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `startAt` | `integer` |  |
| `maxResults` | `integer` |  |
| `total` | `integer` |  |

</details>

#### Issue Worklogs Get

Retrieve a single worklog by its ID

**Python SDK**

```python
jira.issue_worklogs.get(
    issue_id_or_key="<str>",
    worklog_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_worklogs",
    "action": "get",
    "params": {
        "issueIdOrKey": "<str>",
        "worklogId": "<str>"
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `worklogId` | `string` | Yes | The worklog ID |
| `expand` | `string` | No | Comma-separated list of additional fields to include (properties) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `self` | `string` |  |
| `author` | `object` |  |
| `updateAuthor` | `object` |  |
| `comment` | `object` |  |
| `created` | `string` |  |
| `updated` | `string` |  |
| `started` | `string` |  |
| `timeSpent` | `string` |  |
| `timeSpentSeconds` | `integer` |  |
| `issueId` | `string` |  |
| `visibility` | `object \| null` |  |
| `properties` | `array \| null` |  |


</details>



## Configuration

The connector requires the following configuration variables:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `subdomain` | `string` | Yes | {subdomain} | Your Jira Cloud subdomain |

These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.


## Authentication

The Jira connector supports the following authentication methods:


### Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `username` | `str` | Yes | Authentication username |
| `password` | `str` | Yes | Authentication password |

#### Example

**Python SDK**

```python
JiraConnector(
  auth_config=JiraAuthConfig(
    username="<Authentication username>",
    password="<Authentication password>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "68e63de2-bb83-4c7e-93fa-a8a9051e3993",
  "auth_config": {
    "username": "<Authentication username>",
    "password": "<Authentication password>"
  },
  "name": "My Jira Connector"
}'
```

