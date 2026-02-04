# Jira full reference

This is the full reference documentation for the Jira agent connector.

## Supported entities and actions

The Jira connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [API Search](#issues-api-search), [Create](#issues-create), [Get](#issues-get), [Update](#issues-update), [Delete](#issues-delete), [Search](#issues-search) |
| Projects | [API Search](#projects-api-search), [Get](#projects-get), [Search](#projects-search) |
| Users | [Get](#users-get), [List](#users-list), [API Search](#users-api-search), [Search](#users-search) |
| Issue Fields | [List](#issue-fields-list), [API Search](#issue-fields-api-search), [Search](#issue-fields-search) |
| Issue Comments | [List](#issue-comments-list), [Create](#issue-comments-create), [Get](#issue-comments-get), [Update](#issue-comments-update), [Delete](#issue-comments-delete), [Search](#issue-comments-search) |
| Issue Worklogs | [List](#issue-worklogs-list), [Get](#issue-worklogs-get), [Search](#issue-worklogs-search) |
| Issues Assignee | [Update](#issues-assignee-update) |

## Issues

### Issues API Search

Retrieve issues based on JQL query with pagination support.

IMPORTANT: This endpoint requires a bounded JQL query. A bounded query must include a search restriction that limits the scope of the search. Examples of valid restrictions include: project (e.g., "project = MYPROJECT"), assignee (e.g., "assignee = currentUser()"), reporter, issue key, sprint, or date-based filters combined with a project restriction. An unbounded query like "order by key desc" will be rejected with a 400 error. Example bounded query: "project = MYPROJECT AND updated >= -7d ORDER BY created DESC".


#### Python SDK

```python
await jira.issues.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "api_search"
}'
```


#### Parameters

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

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `fields` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `isLast` | `boolean \| null` |  |
| `total` | `integer` |  |

</details>

### Issues Create

Creates an issue or a sub-task from a JSON representation

#### Python SDK

```python
await jira.issues.create(
    fields={
        "project": {},
        "issuetype": {},
        "summary": "<str>"
    },
    update={},
    update_history=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "create",
    "params": {
        "fields": {
            "project": {},
            "issuetype": {},
            "summary": "<str>"
        },
        "update": {},
        "updateHistory": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fields` | `object` | Yes | The issue fields to set |
| `fields.project` | `object` | Yes | The project to create the issue in |
| `fields.project.id` | `string` | No | Project ID |
| `fields.project.key` | `string` | No | Project key (e.g., 'PROJ') |
| `fields.issuetype` | `object` | Yes | The type of issue (e.g., Bug, Task, Story) |
| `fields.issuetype.id` | `string` | No | Issue type ID |
| `fields.issuetype.name` | `string` | No | Issue type name (e.g., 'Bug', 'Task', 'Story') |
| `fields.summary` | `string` | Yes | A brief summary of the issue (title) |
| `fields.description` | `object` | No | Issue description in Atlassian Document Format (ADF) |
| `fields.description.type` | `string` | No | Document type (always 'doc') |
| `fields.description.version` | `integer` | No | ADF version |
| `fields.description.content` | `array<object>` | No | Array of content blocks |
| `fields.description.content.type` | `string` | No | Block type (e.g., 'paragraph') |
| `fields.description.content.content` | `array<object>` | No |  |
| `fields.description.content.content.type` | `string` | No | Content type (e.g., 'text') |
| `fields.description.content.content.text` | `string` | No | Text content |
| `fields.priority` | `object` | No | Issue priority |
| `fields.priority.id` | `string` | No | Priority ID |
| `fields.priority.name` | `string` | No | Priority name (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest') |
| `fields.assignee` | `object` | No | The user to assign the issue to |
| `fields.assignee.accountId` | `string` | No | The account ID of the user |
| `fields.labels` | `array<string>` | No | Labels to add to the issue |
| `fields.parent` | `object` | No | Parent issue for subtasks |
| `fields.parent.key` | `string` | No | Parent issue key |
| `update` | `object` | No | Additional update operations to perform |
| `updateHistory` | `boolean` | No | Whether the action taken is added to the user's Recent history |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `self` | `string` |  |


</details>

### Issues Get

Retrieve a single issue by its ID or key

#### Python SDK

```python
await jira.issues.get(
    issue_id_or_key="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

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

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `fields` | `object` |  |


</details>

### Issues Update

Edits an issue. Issue properties may be updated as part of the edit. Only fields included in the request body are updated.

#### Python SDK

```python
await jira.issues.update(
    fields={},
    update={},
    transition={},
    issue_id_or_key="<str>",
    notify_users=True,
    override_screen_security=True,
    override_editable_flag=True,
    return_issue=True,
    expand="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "update",
    "params": {
        "fields": {},
        "update": {},
        "transition": {},
        "issueIdOrKey": "<str>",
        "notifyUsers": True,
        "overrideScreenSecurity": True,
        "overrideEditableFlag": True,
        "returnIssue": True,
        "expand": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fields` | `object` | No | The issue fields to update |
| `fields.summary` | `string` | No | A brief summary of the issue (title) |
| `fields.description` | `object` | No | Issue description in Atlassian Document Format (ADF) |
| `fields.description.type` | `string` | No | Document type (always 'doc') |
| `fields.description.version` | `integer` | No | ADF version |
| `fields.description.content` | `array<object>` | No | Array of content blocks |
| `fields.description.content.type` | `string` | No | Block type (e.g., 'paragraph') |
| `fields.description.content.content` | `array<object>` | No |  |
| `fields.description.content.content.type` | `string` | No | Content type (e.g., 'text') |
| `fields.description.content.content.text` | `string` | No | Text content |
| `fields.priority` | `object` | No | Issue priority |
| `fields.priority.id` | `string` | No | Priority ID |
| `fields.priority.name` | `string` | No | Priority name (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest') |
| `fields.assignee` | `object` | No | The user to assign the issue to |
| `fields.assignee.accountId` | `string` | No | The account ID of the user (use null to unassign) |
| `fields.labels` | `array<string>` | No | Labels for the issue |
| `update` | `object` | No | Additional update operations to perform |
| `transition` | `object` | No | Transition the issue to a new status |
| `transition.id` | `string` | No | The ID of the transition to perform |
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `notifyUsers` | `boolean` | No | Whether a notification email about the issue update is sent to all watchers. Default is true. |
| `overrideScreenSecurity` | `boolean` | No | Whether screen security is overridden to enable hidden fields to be edited. |
| `overrideEditableFlag` | `boolean` | No | Whether the issue's edit metadata is overridden. |
| `returnIssue` | `boolean` | No | Whether the updated issue is returned. |
| `expand` | `string` | No | Expand options when returning the updated issue. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `self` | `string` |  |
| `expand` | `string \| null` |  |
| `fields` | `object` |  |


</details>

### Issues Delete

Deletes an issue. An issue cannot be deleted if it has one or more subtasks unless deleteSubtasks is true.

#### Python SDK

```python
await jira.issues.delete(
    issue_id_or_key="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "delete",
    "params": {
        "issueIdOrKey": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `deleteSubtasks` | `boolean` | No | Whether to delete the issue's subtasks. Default is false. |


### Issues Search

Search and filter issues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await jira.issues.search(
    query={"filter": {"eq": {"changelog": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"changelog": {}}}}
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
| `changelog` | `object` | Details of changelogs associated with the issue |
| `created` | `string` | The timestamp when the issue was created |
| `editmeta` | `object` | The metadata for the fields on the issue that can be amended |
| `expand` | `string` | Expand options that include additional issue details in the response |
| `fields` | `object` | Details of various fields associated with the issue |
| `fieldsToInclude` | `object` | Specify the fields to include in the fetched issues data |
| `id` | `string` | The unique ID of the issue |
| `key` | `string` | The unique key of the issue |
| `names` | `object` | The ID and name of each field present on the issue |
| `operations` | `object` | The operations that can be performed on the issue |
| `projectId` | `string` | The ID of the project containing the issue |
| `projectKey` | `string` | The key of the project containing the issue |
| `properties` | `object` | Details of the issue properties identified in the request |
| `renderedFields` | `object` | The rendered value of each field present on the issue |
| `schema` | `object` | The schema describing each field present on the issue |
| `self` | `string` | The URL of the issue details |
| `transitions` | `array` | The transitions that can be performed on the issue |
| `updated` | `string` | The timestamp when the issue was last updated |
| `versionedRepresentations` | `object` | The versions of each field on the issue |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.changelog` | `object` | Details of changelogs associated with the issue |
| `hits[].data.created` | `string` | The timestamp when the issue was created |
| `hits[].data.editmeta` | `object` | The metadata for the fields on the issue that can be amended |
| `hits[].data.expand` | `string` | Expand options that include additional issue details in the response |
| `hits[].data.fields` | `object` | Details of various fields associated with the issue |
| `hits[].data.fieldsToInclude` | `object` | Specify the fields to include in the fetched issues data |
| `hits[].data.id` | `string` | The unique ID of the issue |
| `hits[].data.key` | `string` | The unique key of the issue |
| `hits[].data.names` | `object` | The ID and name of each field present on the issue |
| `hits[].data.operations` | `object` | The operations that can be performed on the issue |
| `hits[].data.projectId` | `string` | The ID of the project containing the issue |
| `hits[].data.projectKey` | `string` | The key of the project containing the issue |
| `hits[].data.properties` | `object` | Details of the issue properties identified in the request |
| `hits[].data.renderedFields` | `object` | The rendered value of each field present on the issue |
| `hits[].data.schema` | `object` | The schema describing each field present on the issue |
| `hits[].data.self` | `string` | The URL of the issue details |
| `hits[].data.transitions` | `array` | The transitions that can be performed on the issue |
| `hits[].data.updated` | `string` | The timestamp when the issue was last updated |
| `hits[].data.versionedRepresentations` | `object` | The versions of each field on the issue |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Projects

### Projects API Search

Search and filter projects with advanced query parameters

#### Python SDK

```python
await jira.projects.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "api_search"
}'
```


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPage` | `string \| null` |  |
| `total` | `integer` |  |

</details>

### Projects Get

Retrieve a single project by its ID or key

#### Python SDK

```python
await jira.projects.get(
    project_id_or_key="<str>"
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
        "projectIdOrKey": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `projectIdOrKey` | `string` | Yes | The project ID or key (e.g., "PROJ" or "10000") |
| `expand` | `string` | No | Comma-separated list of additional fields to include (description, projectKeys, lead, issueTypes, url, insight) |
| `properties` | `string` | No | A comma-separated list of project property keys to return. To get a list of all project property keys, use Get project property keys. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Projects Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await jira.projects.search(
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
| `archived` | `boolean` | Whether the project is archived |
| `archivedBy` | `object` | The user who archived the project |
| `archivedDate` | `string` | The date when the project was archived |
| `assigneeType` | `string` | The default assignee when creating issues for this project |
| `avatarUrls` | `object` | The URLs of the project's avatars |
| `components` | `array` | List of the components contained in the project |
| `deleted` | `boolean` | Whether the project is marked as deleted |
| `deletedBy` | `object` | The user who marked the project as deleted |
| `deletedDate` | `string` | The date when the project was marked as deleted |
| `description` | `string` | A brief description of the project |
| `email` | `string` | An email address associated with the project |
| `entityId` | `string` | The unique identifier of the project entity |
| `expand` | `string` | Expand options that include additional project details in the response |
| `favourite` | `boolean` | Whether the project is selected as a favorite |
| `id` | `string` | The ID of the project |
| `insight` | `object` | Insights about the project |
| `isPrivate` | `boolean` | Whether the project is private |
| `issueTypeHierarchy` | `object` | The issue type hierarchy for the project |
| `issueTypes` | `array` | List of the issue types available in the project |
| `key` | `string` | The key of the project |
| `lead` | `object` | The username of the project lead |
| `name` | `string` | The name of the project |
| `permissions` | `object` | User permissions on the project |
| `projectCategory` | `object` | The category the project belongs to |
| `projectTypeKey` | `string` | The project type of the project |
| `properties` | `object` | Map of project properties |
| `retentionTillDate` | `string` | The date when the project is deleted permanently |
| `roles` | `object` | The name and self URL for each role defined in the project |
| `self` | `string` | The URL of the project details |
| `simplified` | `boolean` | Whether the project is simplified |
| `style` | `string` | The type of the project |
| `url` | `string` | A link to information about this project |
| `uuid` | `string` | Unique ID for next-gen projects |
| `versions` | `array` | The versions defined in the project |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.archived` | `boolean` | Whether the project is archived |
| `hits[].data.archivedBy` | `object` | The user who archived the project |
| `hits[].data.archivedDate` | `string` | The date when the project was archived |
| `hits[].data.assigneeType` | `string` | The default assignee when creating issues for this project |
| `hits[].data.avatarUrls` | `object` | The URLs of the project's avatars |
| `hits[].data.components` | `array` | List of the components contained in the project |
| `hits[].data.deleted` | `boolean` | Whether the project is marked as deleted |
| `hits[].data.deletedBy` | `object` | The user who marked the project as deleted |
| `hits[].data.deletedDate` | `string` | The date when the project was marked as deleted |
| `hits[].data.description` | `string` | A brief description of the project |
| `hits[].data.email` | `string` | An email address associated with the project |
| `hits[].data.entityId` | `string` | The unique identifier of the project entity |
| `hits[].data.expand` | `string` | Expand options that include additional project details in the response |
| `hits[].data.favourite` | `boolean` | Whether the project is selected as a favorite |
| `hits[].data.id` | `string` | The ID of the project |
| `hits[].data.insight` | `object` | Insights about the project |
| `hits[].data.isPrivate` | `boolean` | Whether the project is private |
| `hits[].data.issueTypeHierarchy` | `object` | The issue type hierarchy for the project |
| `hits[].data.issueTypes` | `array` | List of the issue types available in the project |
| `hits[].data.key` | `string` | The key of the project |
| `hits[].data.lead` | `object` | The username of the project lead |
| `hits[].data.name` | `string` | The name of the project |
| `hits[].data.permissions` | `object` | User permissions on the project |
| `hits[].data.projectCategory` | `object` | The category the project belongs to |
| `hits[].data.projectTypeKey` | `string` | The project type of the project |
| `hits[].data.properties` | `object` | Map of project properties |
| `hits[].data.retentionTillDate` | `string` | The date when the project is deleted permanently |
| `hits[].data.roles` | `object` | The name and self URL for each role defined in the project |
| `hits[].data.self` | `string` | The URL of the project details |
| `hits[].data.simplified` | `boolean` | Whether the project is simplified |
| `hits[].data.style` | `string` | The type of the project |
| `hits[].data.url` | `string` | A link to information about this project |
| `hits[].data.uuid` | `string` | Unique ID for next-gen projects |
| `hits[].data.versions` | `array` | The versions defined in the project |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Users

### Users Get

Retrieve a single user by their account ID

#### Python SDK

```python
await jira.users.get(
    account_id="<str>"
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
        "accountId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `accountId` | `string` | Yes | The account ID of the user |
| `expand` | `string` | No | Comma-separated list of additional fields to include (groups, applicationRoles) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users List

Returns a paginated list of users

#### Python SDK

```python
await jira.users.list()
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
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page (max 1000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users API Search

Search for users using a query string

#### Python SDK

```python
await jira.users.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "api_search"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | A query string to search for users (matches display name, email, account ID) |
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page (max 1000) |
| `accountId` | `string` | No | Filter by account IDs (supports multiple values) |
| `property` | `string` | No | Property key to filter users |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await jira.users.search(
    query={"filter": {"eq": {"accountId": "<str>"}}}
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
        "query": {"filter": {"eq": {"accountId": "<str>"}}}
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
| `accountId` | `string` | The account ID of the user, uniquely identifying the user across all Atlassian products |
| `accountType` | `string` | The user account type (atlassian, app, or customer) |
| `active` | `boolean` | Indicates whether the user is active |
| `applicationRoles` | `object` | The application roles assigned to the user |
| `avatarUrls` | `object` | The avatars of the user |
| `displayName` | `string` | The display name of the user |
| `emailAddress` | `string` | The email address of the user |
| `expand` | `string` | Options to include additional user details in the response |
| `groups` | `object` | The groups to which the user belongs |
| `key` | `string` | Deprecated property |
| `locale` | `string` | The locale of the user |
| `name` | `string` | Deprecated property |
| `self` | `string` | The URL of the user |
| `timeZone` | `string` | The time zone specified in the user's profile |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.accountId` | `string` | The account ID of the user, uniquely identifying the user across all Atlassian products |
| `hits[].data.accountType` | `string` | The user account type (atlassian, app, or customer) |
| `hits[].data.active` | `boolean` | Indicates whether the user is active |
| `hits[].data.applicationRoles` | `object` | The application roles assigned to the user |
| `hits[].data.avatarUrls` | `object` | The avatars of the user |
| `hits[].data.displayName` | `string` | The display name of the user |
| `hits[].data.emailAddress` | `string` | The email address of the user |
| `hits[].data.expand` | `string` | Options to include additional user details in the response |
| `hits[].data.groups` | `object` | The groups to which the user belongs |
| `hits[].data.key` | `string` | Deprecated property |
| `hits[].data.locale` | `string` | The locale of the user |
| `hits[].data.name` | `string` | Deprecated property |
| `hits[].data.self` | `string` | The URL of the user |
| `hits[].data.timeZone` | `string` | The time zone specified in the user's profile |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Issue Fields

### Issue Fields List

Returns a list of all custom and system fields

#### Python SDK

```python
await jira.issue_fields.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_fields",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string \| null` |  |
| `name` | `string` |  |
| `custom` | `boolean \| null` |  |
| `orderable` | `boolean \| null` |  |
| `navigable` | `boolean \| null` |  |
| `searchable` | `boolean \| null` |  |
| `clauseNames` | `array \| null` |  |
| `schema` | `object \| null` |  |
| `untranslatedName` | `string \| null` |  |
| `typeDisplayName` | `string \| null` |  |
| `description` | `string \| null` |  |
| `searcherKey` | `string \| null` |  |
| `screensCount` | `integer \| null` |  |
| `contextsCount` | `integer \| null` |  |
| `isLocked` | `boolean \| null` |  |
| `lastUsed` | `string \| null` |  |


</details>

### Issue Fields API Search

Search and filter issue fields with query parameters

#### Python SDK

```python
await jira.issue_fields.api_search()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_fields",
    "action": "api_search"
}'
```


#### Parameters

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

#### Records

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

### Issue Fields Search

Search and filter issue fields records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await jira.issue_fields.search(
    query={"filter": {"eq": {"clauseNames": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_fields",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clauseNames": []}}}
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
| `clauseNames` | `array` | The names that can be used to reference the field in an advanced search |
| `custom` | `boolean` | Whether the field is a custom field |
| `id` | `string` | The ID of the field |
| `key` | `string` | The key of the field |
| `name` | `string` | The name of the field |
| `navigable` | `boolean` | Whether the field can be used as a column on the issue navigator |
| `orderable` | `boolean` | Whether the content of the field can be used to order lists |
| `schema` | `object` | The data schema for the field |
| `scope` | `object` | The scope of the field |
| `searchable` | `boolean` | Whether the content of the field can be searched |
| `untranslatedName` | `string` | The untranslated name of the field |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.clauseNames` | `array` | The names that can be used to reference the field in an advanced search |
| `hits[].data.custom` | `boolean` | Whether the field is a custom field |
| `hits[].data.id` | `string` | The ID of the field |
| `hits[].data.key` | `string` | The key of the field |
| `hits[].data.name` | `string` | The name of the field |
| `hits[].data.navigable` | `boolean` | Whether the field can be used as a column on the issue navigator |
| `hits[].data.orderable` | `boolean` | Whether the content of the field can be used to order lists |
| `hits[].data.schema` | `object` | The data schema for the field |
| `hits[].data.scope` | `object` | The scope of the field |
| `hits[].data.searchable` | `boolean` | Whether the content of the field can be searched |
| `hits[].data.untranslatedName` | `string` | The untranslated name of the field |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Issue Comments

### Issue Comments List

Retrieve all comments for a specific issue

#### Python SDK

```python
await jira.issue_comments.list(
    issue_id_or_key="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page |
| `orderBy` | `"created" \| "-created" \| "+created"` | No | Order the results by created date (+ for ascending, - for descending) |
| `expand` | `string` | No | Comma-separated list of additional fields to include (renderedBody, properties) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `startAt` | `integer` |  |
| `maxResults` | `integer` |  |
| `total` | `integer` |  |

</details>

### Issue Comments Create

Adds a comment to an issue

#### Python SDK

```python
await jira.issue_comments.create(
    body={
        "type": "<str>",
        "version": 0,
        "content": []
    },
    visibility={},
    properties=[],
    issue_id_or_key="<str>",
    expand="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_comments",
    "action": "create",
    "params": {
        "body": {
            "type": "<str>",
            "version": 0,
            "content": []
        },
        "visibility": {},
        "properties": [],
        "issueIdOrKey": "<str>",
        "expand": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `body` | `object` | Yes | Comment content in Atlassian Document Format (ADF) |
| `body.type` | `string` | Yes | Document type (always 'doc') |
| `body.version` | `integer` | Yes | ADF version |
| `body.content` | `array<object>` | Yes | Array of content blocks |
| `body.content.type` | `string` | No | Block type (e.g., 'paragraph') |
| `body.content.content` | `array<object>` | No |  |
| `body.content.content.type` | `string` | No | Content type (e.g., 'text') |
| `body.content.content.text` | `string` | No | Text content |
| `visibility` | `object` | No | Restrict comment visibility to a group or role |
| `visibility.type` | `"group" \| "role"` | No | The type of visibility restriction |
| `visibility.value` | `string` | No | The name of the group or role |
| `visibility.identifier` | `string` | No | The ID of the group or role |
| `properties` | `array<object>` | No | Custom properties for the comment |
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `expand` | `string` | No | Expand options for the returned comment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Issue Comments Get

Retrieve a single comment by its ID

#### Python SDK

```python
await jira.issue_comments.get(
    issue_id_or_key="<str>",
    comment_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `commentId` | `string` | Yes | The comment ID |
| `expand` | `string` | No | Comma-separated list of additional fields to include (renderedBody, properties) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Issue Comments Update

Updates a comment on an issue

#### Python SDK

```python
await jira.issue_comments.update(
    body={
        "type": "<str>",
        "version": 0,
        "content": []
    },
    visibility={},
    issue_id_or_key="<str>",
    comment_id="<str>",
    notify_users=True,
    expand="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_comments",
    "action": "update",
    "params": {
        "body": {
            "type": "<str>",
            "version": 0,
            "content": []
        },
        "visibility": {},
        "issueIdOrKey": "<str>",
        "commentId": "<str>",
        "notifyUsers": True,
        "expand": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `body` | `object` | Yes | Updated comment content in Atlassian Document Format (ADF) |
| `body.type` | `string` | Yes | Document type (always 'doc') |
| `body.version` | `integer` | Yes | ADF version |
| `body.content` | `array<object>` | Yes | Array of content blocks |
| `body.content.type` | `string` | No | Block type (e.g., 'paragraph') |
| `body.content.content` | `array<object>` | No |  |
| `body.content.content.type` | `string` | No | Content type (e.g., 'text') |
| `body.content.content.text` | `string` | No | Text content |
| `visibility` | `object` | No | Restrict comment visibility to a group or role |
| `visibility.type` | `"group" \| "role"` | No | The type of visibility restriction |
| `visibility.value` | `string` | No | The name of the group or role |
| `visibility.identifier` | `string` | No | The ID of the group or role |
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `commentId` | `string` | Yes | The comment ID |
| `notifyUsers` | `boolean` | No | Whether a notification email about the comment update is sent. Default is true. |
| `expand` | `string` | No | Expand options for the returned comment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Issue Comments Delete

Deletes a comment from an issue

#### Python SDK

```python
await jira.issue_comments.delete(
    issue_id_or_key="<str>",
    comment_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_comments",
    "action": "delete",
    "params": {
        "issueIdOrKey": "<str>",
        "commentId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `commentId` | `string` | Yes | The comment ID |


### Issue Comments Search

Search and filter issue comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await jira.issue_comments.search(
    query={"filter": {"eq": {"author": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_comments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"author": {}}}}
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
| `author` | `object` | The ID of the user who created the comment |
| `body` | `object` | The comment text in Atlassian Document Format |
| `created` | `string` | The date and time at which the comment was created |
| `id` | `string` | The ID of the comment |
| `issueId` | `string` | Id of the related issue |
| `jsdPublic` | `boolean` | Whether the comment is visible in Jira Service Desk |
| `properties` | `array` | A list of comment properties |
| `renderedBody` | `string` | The rendered version of the comment |
| `self` | `string` | The URL of the comment |
| `updateAuthor` | `object` | The ID of the user who updated the comment last |
| `updated` | `string` | The date and time at which the comment was updated last |
| `visibility` | `object` | The group or role to which this item is visible |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.author` | `object` | The ID of the user who created the comment |
| `hits[].data.body` | `object` | The comment text in Atlassian Document Format |
| `hits[].data.created` | `string` | The date and time at which the comment was created |
| `hits[].data.id` | `string` | The ID of the comment |
| `hits[].data.issueId` | `string` | Id of the related issue |
| `hits[].data.jsdPublic` | `boolean` | Whether the comment is visible in Jira Service Desk |
| `hits[].data.properties` | `array` | A list of comment properties |
| `hits[].data.renderedBody` | `string` | The rendered version of the comment |
| `hits[].data.self` | `string` | The URL of the comment |
| `hits[].data.updateAuthor` | `object` | The ID of the user who updated the comment last |
| `hits[].data.updated` | `string` | The date and time at which the comment was updated last |
| `hits[].data.visibility` | `object` | The group or role to which this item is visible |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Issue Worklogs

### Issue Worklogs List

Retrieve all worklogs for a specific issue

#### Python SDK

```python
await jira.issue_worklogs.list(
    issue_id_or_key="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `startAt` | `integer` | No | The index of the first item to return in a page of results (page offset) |
| `maxResults` | `integer` | No | The maximum number of items to return per page |
| `expand` | `string` | No | Comma-separated list of additional fields to include (properties) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `startAt` | `integer` |  |
| `maxResults` | `integer` |  |
| `total` | `integer` |  |

</details>

### Issue Worklogs Get

Retrieve a single worklog by its ID

#### Python SDK

```python
await jira.issue_worklogs.get(
    issue_id_or_key="<str>",
    worklog_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |
| `worklogId` | `string` | Yes | The worklog ID |
| `expand` | `string` | No | Comma-separated list of additional fields to include (properties) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Issue Worklogs Search

Search and filter issue worklogs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await jira.issue_worklogs.search(
    query={"filter": {"eq": {"author": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_worklogs",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"author": {}}}}
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
| `author` | `object` | Details of the user who created the worklog |
| `comment` | `object` | A comment about the worklog in Atlassian Document Format |
| `created` | `string` | The datetime on which the worklog was created |
| `id` | `string` | The ID of the worklog record |
| `issueId` | `string` | The ID of the issue this worklog is for |
| `properties` | `array` | Details of properties for the worklog |
| `self` | `string` | The URL of the worklog item |
| `started` | `string` | The datetime on which the worklog effort was started |
| `timeSpent` | `string` | The time spent working on the issue as days, hours, or minutes |
| `timeSpentSeconds` | `integer` | The time in seconds spent working on the issue |
| `updateAuthor` | `object` | Details of the user who last updated the worklog |
| `updated` | `string` | The datetime on which the worklog was last updated |
| `visibility` | `object` | Details about any restrictions in the visibility of the worklog |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.author` | `object` | Details of the user who created the worklog |
| `hits[].data.comment` | `object` | A comment about the worklog in Atlassian Document Format |
| `hits[].data.created` | `string` | The datetime on which the worklog was created |
| `hits[].data.id` | `string` | The ID of the worklog record |
| `hits[].data.issueId` | `string` | The ID of the issue this worklog is for |
| `hits[].data.properties` | `array` | Details of properties for the worklog |
| `hits[].data.self` | `string` | The URL of the worklog item |
| `hits[].data.started` | `string` | The datetime on which the worklog effort was started |
| `hits[].data.timeSpent` | `string` | The time spent working on the issue as days, hours, or minutes |
| `hits[].data.timeSpentSeconds` | `integer` | The time in seconds spent working on the issue |
| `hits[].data.updateAuthor` | `object` | Details of the user who last updated the worklog |
| `hits[].data.updated` | `string` | The datetime on which the worklog was last updated |
| `hits[].data.visibility` | `object` | Details about any restrictions in the visibility of the worklog |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Issues Assignee

### Issues Assignee Update

Assigns an issue to a user. Use accountId to specify the assignee. Use null to unassign the issue. Use "-1" to set to automatic (project default).

#### Python SDK

```python
await jira.issues_assignee.update(
    account_id="<str>",
    issue_id_or_key="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues_assignee",
    "action": "update",
    "params": {
        "accountId": "<str>",
        "issueIdOrKey": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `accountId` | `string` | No | The account ID of the user to assign the issue to. Use null to unassign the issue. Use "-1" to set to automatic (project default assignee). |
| `issueIdOrKey` | `string` | Yes | The issue ID or key (e.g., "PROJ-123" or "10000") |


