# Linear full reference

This is the full reference documentation for the Linear agent connector.

## Supported entities and actions

The Linear connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [List](#issues-list), [Get](#issues-get), [Create](#issues-create), [Update](#issues-update), [Search](#issues-search) |
| Projects | [List](#projects-list), [Get](#projects-get), [Search](#projects-search) |
| Teams | [List](#teams-list), [Get](#teams-get), [Search](#teams-search) |
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Comments | [List](#comments-list), [Get](#comments-get), [Create](#comments-create), [Update](#comments-update), [Search](#comments-search) |

## Issues

### Issues List

Returns a paginated list of issues via GraphQL with pagination support

#### Python SDK

```python
await linear.issues.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string` |  |
| `description` | `string \| any` |  |
| `state` | `object \| any` |  |
| `priority` | `number \| any` |  |
| `assignee` | `object \| any` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `hasNextPage` | `boolean` |  |
| `endCursor` | `string \| null` |  |

</details>

### Issues Get

Get a single issue by ID via GraphQL

#### Python SDK

```python
await linear.issues.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Issue ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Issues Create

Create a new issue via GraphQL mutation

#### Python SDK

```python
await linear.issues.create(
    team_id="<str>",
    title="<str>",
    description="<str>",
    state_id="<str>",
    priority=0
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
        "teamId": "<str>",
        "title": "<str>",
        "description": "<str>",
        "stateId": "<str>",
        "priority": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `teamId` | `string` | Yes | The ID of the team to create the issue in |
| `title` | `string` | Yes | The title of the issue |
| `description` | `string` | No | The description of the issue (supports markdown) |
| `stateId` | `string` | No | The ID of the workflow state for the issue |
| `priority` | `integer` | No | The priority of the issue (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Issues Update

Update an existing issue via GraphQL mutation. All fields except id are optional for partial updates.
To assign a user, provide assigneeId with the user's ID (get user IDs from the users list).
Omit assigneeId to leave the current assignee unchanged.


#### Python SDK

```python
await linear.issues.update(
    id="<str>",
    title="<str>",
    description="<str>",
    state_id="<str>",
    priority=0,
    assignee_id="<str>"
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
        "id": "<str>",
        "title": "<str>",
        "description": "<str>",
        "stateId": "<str>",
        "priority": 0,
        "assigneeId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the issue to update |
| `title` | `string` | No | The new title of the issue |
| `description` | `string` | No | The new description of the issue (supports markdown) |
| `stateId` | `string` | No | The ID of the new workflow state for the issue |
| `priority` | `integer` | No | The new priority of the issue (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low) |
| `assigneeId` | `string` | No | The ID of the user to assign to this issue. Get user IDs from the users list. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Issues Search

Search and filter issues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linear.issues.search(
    query={"filter": {"eq": {"addedToCycleAt": "<str>"}}}
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
        "query": {"filter": {"eq": {"addedToCycleAt": "<str>"}}}
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
| `addedToCycleAt` | `string` |  |
| `addedToProjectAt` | `string` |  |
| `addedToTeamAt` | `string` |  |
| `assignee` | `object` |  |
| `assigneeId` | `string` |  |
| `attachmentIds` | `array` |  |
| `attachments` | `object` |  |
| `branchName` | `string` |  |
| `canceledAt` | `string` |  |
| `completedAt` | `string` |  |
| `createdAt` | `string` |  |
| `creator` | `object` |  |
| `creatorId` | `string` |  |
| `customerTicketCount` | `number` |  |
| `cycle` | `object` |  |
| `cycleId` | `string` |  |
| `description` | `string` |  |
| `descriptionState` | `string` |  |
| `dueDate` | `string` |  |
| `estimate` | `number` |  |
| `id` | `string` |  |
| `identifier` | `string` |  |
| `integrationSourceType` | `string` |  |
| `labelIds` | `array` |  |
| `labels` | `object` |  |
| `milestoneId` | `string` |  |
| `number` | `number` |  |
| `parent` | `object` |  |
| `parentId` | `string` |  |
| `previousIdentifiers` | `array` |  |
| `priority` | `number` |  |
| `priorityLabel` | `string` |  |
| `prioritySortOrder` | `number` |  |
| `project` | `object` |  |
| `projectId` | `string` |  |
| `projectMilestone` | `object` |  |
| `reactionData` | `array` |  |
| `relationIds` | `array` |  |
| `relations` | `object` |  |
| `slaType` | `string` |  |
| `sortOrder` | `number` |  |
| `sourceCommentId` | `string` |  |
| `startedAt` | `string` |  |
| `state` | `object` |  |
| `stateId` | `string` |  |
| `subIssueSortOrder` | `number` |  |
| `subscriberIds` | `array` |  |
| `subscribers` | `object` |  |
| `team` | `object` |  |
| `teamId` | `string` |  |
| `title` | `string` |  |
| `updatedAt` | `string` |  |
| `url` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.addedToCycleAt` | `string` |  |
| `hits[].data.addedToProjectAt` | `string` |  |
| `hits[].data.addedToTeamAt` | `string` |  |
| `hits[].data.assignee` | `object` |  |
| `hits[].data.assigneeId` | `string` |  |
| `hits[].data.attachmentIds` | `array` |  |
| `hits[].data.attachments` | `object` |  |
| `hits[].data.branchName` | `string` |  |
| `hits[].data.canceledAt` | `string` |  |
| `hits[].data.completedAt` | `string` |  |
| `hits[].data.createdAt` | `string` |  |
| `hits[].data.creator` | `object` |  |
| `hits[].data.creatorId` | `string` |  |
| `hits[].data.customerTicketCount` | `number` |  |
| `hits[].data.cycle` | `object` |  |
| `hits[].data.cycleId` | `string` |  |
| `hits[].data.description` | `string` |  |
| `hits[].data.descriptionState` | `string` |  |
| `hits[].data.dueDate` | `string` |  |
| `hits[].data.estimate` | `number` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.identifier` | `string` |  |
| `hits[].data.integrationSourceType` | `string` |  |
| `hits[].data.labelIds` | `array` |  |
| `hits[].data.labels` | `object` |  |
| `hits[].data.milestoneId` | `string` |  |
| `hits[].data.number` | `number` |  |
| `hits[].data.parent` | `object` |  |
| `hits[].data.parentId` | `string` |  |
| `hits[].data.previousIdentifiers` | `array` |  |
| `hits[].data.priority` | `number` |  |
| `hits[].data.priorityLabel` | `string` |  |
| `hits[].data.prioritySortOrder` | `number` |  |
| `hits[].data.project` | `object` |  |
| `hits[].data.projectId` | `string` |  |
| `hits[].data.projectMilestone` | `object` |  |
| `hits[].data.reactionData` | `array` |  |
| `hits[].data.relationIds` | `array` |  |
| `hits[].data.relations` | `object` |  |
| `hits[].data.slaType` | `string` |  |
| `hits[].data.sortOrder` | `number` |  |
| `hits[].data.sourceCommentId` | `string` |  |
| `hits[].data.startedAt` | `string` |  |
| `hits[].data.state` | `object` |  |
| `hits[].data.stateId` | `string` |  |
| `hits[].data.subIssueSortOrder` | `number` |  |
| `hits[].data.subscriberIds` | `array` |  |
| `hits[].data.subscribers` | `object` |  |
| `hits[].data.team` | `object` |  |
| `hits[].data.teamId` | `string` |  |
| `hits[].data.title` | `string` |  |
| `hits[].data.updatedAt` | `string` |  |
| `hits[].data.url` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Projects

### Projects List

Returns a paginated list of projects via GraphQL with pagination support

#### Python SDK

```python
await linear.projects.list()
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
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `description` | `string \| any` |  |
| `state` | `string \| any` |  |
| `startDate` | `string \| any` |  |
| `targetDate` | `string \| any` |  |
| `lead` | `object \| any` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `hasNextPage` | `boolean` |  |
| `endCursor` | `string \| null` |  |

</details>

### Projects Get

Get a single project by ID via GraphQL

#### Python SDK

```python
await linear.projects.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Project ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Projects Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linear.projects.search(
    query={"filter": {"eq": {"canceledAt": "<str>"}}}
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
        "query": {"filter": {"eq": {"canceledAt": "<str>"}}}
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
| `canceledAt` | `string` |  |
| `color` | `string` |  |
| `completedAt` | `string` |  |
| `completedIssueCountHistory` | `array` |  |
| `completedScopeHistory` | `array` |  |
| `content` | `string` |  |
| `contentState` | `string` |  |
| `convertedFromIssue` | `object` |  |
| `convertedFromIssueId` | `string` |  |
| `createdAt` | `string` |  |
| `creator` | `object` |  |
| `creatorId` | `string` |  |
| `description` | `string` |  |
| `health` | `string` |  |
| `healthUpdatedAt` | `string` |  |
| `icon` | `string` |  |
| `id` | `string` |  |
| `inProgressScopeHistory` | `array` |  |
| `issueCountHistory` | `array` |  |
| `lead` | `object` |  |
| `leadId` | `string` |  |
| `name` | `string` |  |
| `priority` | `number` |  |
| `prioritySortOrder` | `number` |  |
| `progress` | `number` |  |
| `scope` | `number` |  |
| `scopeHistory` | `array` |  |
| `slugId` | `string` |  |
| `sortOrder` | `number` |  |
| `startDate` | `string` |  |
| `startedAt` | `string` |  |
| `status` | `object` |  |
| `statusId` | `string` |  |
| `targetDate` | `string` |  |
| `teamIds` | `array` |  |
| `teams` | `object` |  |
| `updateRemindersDay` | `string` |  |
| `updateRemindersHour` | `number` |  |
| `updatedAt` | `string` |  |
| `url` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.canceledAt` | `string` |  |
| `hits[].data.color` | `string` |  |
| `hits[].data.completedAt` | `string` |  |
| `hits[].data.completedIssueCountHistory` | `array` |  |
| `hits[].data.completedScopeHistory` | `array` |  |
| `hits[].data.content` | `string` |  |
| `hits[].data.contentState` | `string` |  |
| `hits[].data.convertedFromIssue` | `object` |  |
| `hits[].data.convertedFromIssueId` | `string` |  |
| `hits[].data.createdAt` | `string` |  |
| `hits[].data.creator` | `object` |  |
| `hits[].data.creatorId` | `string` |  |
| `hits[].data.description` | `string` |  |
| `hits[].data.health` | `string` |  |
| `hits[].data.healthUpdatedAt` | `string` |  |
| `hits[].data.icon` | `string` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.inProgressScopeHistory` | `array` |  |
| `hits[].data.issueCountHistory` | `array` |  |
| `hits[].data.lead` | `object` |  |
| `hits[].data.leadId` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.priority` | `number` |  |
| `hits[].data.prioritySortOrder` | `number` |  |
| `hits[].data.progress` | `number` |  |
| `hits[].data.scope` | `number` |  |
| `hits[].data.scopeHistory` | `array` |  |
| `hits[].data.slugId` | `string` |  |
| `hits[].data.sortOrder` | `number` |  |
| `hits[].data.startDate` | `string` |  |
| `hits[].data.startedAt` | `string` |  |
| `hits[].data.status` | `object` |  |
| `hits[].data.statusId` | `string` |  |
| `hits[].data.targetDate` | `string` |  |
| `hits[].data.teamIds` | `array` |  |
| `hits[].data.teams` | `object` |  |
| `hits[].data.updateRemindersDay` | `string` |  |
| `hits[].data.updateRemindersHour` | `number` |  |
| `hits[].data.updatedAt` | `string` |  |
| `hits[].data.url` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Teams

### Teams List

Returns a list of teams via GraphQL with pagination support

#### Python SDK

```python
await linear.teams.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `key` | `string` |  |
| `description` | `string \| any` |  |
| `timezone` | `string \| any` |  |
| `createdAt` | `string` |  |
| `updatedAt` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `hasNextPage` | `boolean` |  |
| `endCursor` | `string \| null` |  |

</details>

### Teams Get

Get a single team by ID via GraphQL

#### Python SDK

```python
await linear.teams.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Team ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Teams Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linear.teams.search(
    query={"filter": {"eq": {"activeCycle": {}}}}
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
        "query": {"filter": {"eq": {"activeCycle": {}}}}
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
| `activeCycle` | `object` |  |
| `activeCycleId` | `string` |  |
| `autoArchivePeriod` | `number` |  |
| `autoClosePeriod` | `number` |  |
| `autoCloseStateId` | `string` |  |
| `color` | `string` |  |
| `createdAt` | `string` |  |
| `cycleCalenderUrl` | `string` |  |
| `cycleCooldownTime` | `number` |  |
| `cycleDuration` | `number` |  |
| `cycleIssueAutoAssignCompleted` | `boolean` |  |
| `cycleIssueAutoAssignStarted` | `boolean` |  |
| `cycleLockToActive` | `boolean` |  |
| `cycleStartDay` | `number` |  |
| `cyclesEnabled` | `boolean` |  |
| `defaultIssueEstimate` | `number` |  |
| `defaultIssueState` | `object` |  |
| `defaultIssueStateId` | `string` |  |
| `groupIssueHistory` | `boolean` |  |
| `icon` | `string` |  |
| `id` | `string` |  |
| `inviteHash` | `string` |  |
| `issueCount` | `number` |  |
| `issueEstimationAllowZero` | `boolean` |  |
| `issueEstimationExtended` | `boolean` |  |
| `issueEstimationType` | `string` |  |
| `key` | `string` |  |
| `markedAsDuplicateWorkflowState` | `object` |  |
| `markedAsDuplicateWorkflowStateId` | `string` |  |
| `name` | `string` |  |
| `parentTeamId` | `string` |  |
| `private` | `boolean` |  |
| `requirePriorityToLeaveTriage` | `boolean` |  |
| `scimManaged` | `boolean` |  |
| `setIssueSortOrderOnStateChange` | `string` |  |
| `timezone` | `string` |  |
| `triageEnabled` | `boolean` |  |
| `triageIssueStateId` | `string` |  |
| `upcomingCycleCount` | `number` |  |
| `updatedAt` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.activeCycle` | `object` |  |
| `hits[].data.activeCycleId` | `string` |  |
| `hits[].data.autoArchivePeriod` | `number` |  |
| `hits[].data.autoClosePeriod` | `number` |  |
| `hits[].data.autoCloseStateId` | `string` |  |
| `hits[].data.color` | `string` |  |
| `hits[].data.createdAt` | `string` |  |
| `hits[].data.cycleCalenderUrl` | `string` |  |
| `hits[].data.cycleCooldownTime` | `number` |  |
| `hits[].data.cycleDuration` | `number` |  |
| `hits[].data.cycleIssueAutoAssignCompleted` | `boolean` |  |
| `hits[].data.cycleIssueAutoAssignStarted` | `boolean` |  |
| `hits[].data.cycleLockToActive` | `boolean` |  |
| `hits[].data.cycleStartDay` | `number` |  |
| `hits[].data.cyclesEnabled` | `boolean` |  |
| `hits[].data.defaultIssueEstimate` | `number` |  |
| `hits[].data.defaultIssueState` | `object` |  |
| `hits[].data.defaultIssueStateId` | `string` |  |
| `hits[].data.groupIssueHistory` | `boolean` |  |
| `hits[].data.icon` | `string` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.inviteHash` | `string` |  |
| `hits[].data.issueCount` | `number` |  |
| `hits[].data.issueEstimationAllowZero` | `boolean` |  |
| `hits[].data.issueEstimationExtended` | `boolean` |  |
| `hits[].data.issueEstimationType` | `string` |  |
| `hits[].data.key` | `string` |  |
| `hits[].data.markedAsDuplicateWorkflowState` | `object` |  |
| `hits[].data.markedAsDuplicateWorkflowStateId` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.parentTeamId` | `string` |  |
| `hits[].data.private` | `boolean` |  |
| `hits[].data.requirePriorityToLeaveTriage` | `boolean` |  |
| `hits[].data.scimManaged` | `boolean` |  |
| `hits[].data.setIssueSortOrderOnStateChange` | `string` |  |
| `hits[].data.timezone` | `string` |  |
| `hits[].data.triageEnabled` | `boolean` |  |
| `hits[].data.triageIssueStateId` | `string` |  |
| `hits[].data.upcomingCycleCount` | `number` |  |
| `hits[].data.updatedAt` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Users

### Users List

Returns a paginated list of users in the organization via GraphQL

#### Python SDK

```python
await linear.users.list()
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
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Users Get

Get a single user by ID via GraphQL

#### Python SDK

```python
await linear.users.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linear.users.search(
    query={"filter": {"eq": {"active": True}}}
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
        "query": {"filter": {"eq": {"active": True}}}
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
| `active` | `boolean` |  |
| `admin` | `boolean` |  |
| `avatarBackgroundColor` | `string` |  |
| `avatarUrl` | `string` |  |
| `createdAt` | `string` |  |
| `createdIssueCount` | `number` |  |
| `displayName` | `string` |  |
| `email` | `string` |  |
| `guest` | `boolean` |  |
| `id` | `string` |  |
| `initials` | `string` |  |
| `inviteHash` | `string` |  |
| `isMe` | `boolean` |  |
| `lastSeen` | `string` |  |
| `name` | `string` |  |
| `teamIds` | `array` |  |
| `teams` | `object` |  |
| `timezone` | `string` |  |
| `updatedAt` | `string` |  |
| `url` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.active` | `boolean` |  |
| `hits[].data.admin` | `boolean` |  |
| `hits[].data.avatarBackgroundColor` | `string` |  |
| `hits[].data.avatarUrl` | `string` |  |
| `hits[].data.createdAt` | `string` |  |
| `hits[].data.createdIssueCount` | `number` |  |
| `hits[].data.displayName` | `string` |  |
| `hits[].data.email` | `string` |  |
| `hits[].data.guest` | `boolean` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.initials` | `string` |  |
| `hits[].data.inviteHash` | `string` |  |
| `hits[].data.isMe` | `boolean` |  |
| `hits[].data.lastSeen` | `string` |  |
| `hits[].data.name` | `string` |  |
| `hits[].data.teamIds` | `array` |  |
| `hits[].data.teams` | `object` |  |
| `hits[].data.timezone` | `string` |  |
| `hits[].data.updatedAt` | `string` |  |
| `hits[].data.url` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Comments

### Comments List

Returns a paginated list of comments for an issue via GraphQL

#### Python SDK

```python
await linear.comments.list(
    issue_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueId` | `string` | Yes | Issue ID to get comments for |
| `first` | `integer` | No | Number of items to return (max 250) |
| `after` | `string` | No | Cursor to start after (for pagination) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Comments Get

Get a single comment by ID via GraphQL

#### Python SDK

```python
await linear.comments.get(
    id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Comment ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Comments Create

Create a new comment on an issue via GraphQL mutation

#### Python SDK

```python
await linear.comments.create(
    issue_id="<str>",
    body="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `issueId` | `string` | Yes | The ID of the issue to add the comment to |
| `body` | `string` | Yes | The comment content in markdown |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Comments Update

Update an existing comment via GraphQL mutation

#### Python SDK

```python
await linear.comments.update(
    id="<str>",
    body="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the comment to update |
| `body` | `string` | Yes | The new comment content in markdown |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |


</details>

### Comments Search

Search and filter comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linear.comments.search(
    query={"filter": {"eq": {"body": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"body": "<str>"}}}
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
| `body` | `string` |  |
| `bodyData` | `string` |  |
| `createdAt` | `string` |  |
| `editedAt` | `string` |  |
| `id` | `string` |  |
| `issue` | `object` |  |
| `issueId` | `string` |  |
| `parent` | `object` |  |
| `parentCommentId` | `string` |  |
| `resolvingCommentId` | `string` |  |
| `resolvingUserId` | `string` |  |
| `updatedAt` | `string` |  |
| `url` | `string` |  |
| `user` | `object` |  |
| `userId` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.body` | `string` |  |
| `hits[].data.bodyData` | `string` |  |
| `hits[].data.createdAt` | `string` |  |
| `hits[].data.editedAt` | `string` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.issue` | `object` |  |
| `hits[].data.issueId` | `string` |  |
| `hits[].data.parent` | `object` |  |
| `hits[].data.parentCommentId` | `string` |  |
| `hits[].data.resolvingCommentId` | `string` |  |
| `hits[].data.resolvingUserId` | `string` |  |
| `hits[].data.updatedAt` | `string` |  |
| `hits[].data.url` | `string` |  |
| `hits[].data.user` | `object` |  |
| `hits[].data.userId` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

