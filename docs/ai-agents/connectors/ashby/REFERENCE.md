# Ashby full reference

This is the full reference documentation for the Ashby agent connector.

## Supported entities and actions

The Ashby connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Candidates | [List](#candidates-list), [Get](#candidates-get) |
| Applications | [List](#applications-list), [Get](#applications-get) |
| Jobs | [List](#jobs-list), [Get](#jobs-get) |
| Departments | [List](#departments-list), [Get](#departments-get) |
| Locations | [List](#locations-list), [Get](#locations-get) |
| Users | [List](#users-list), [Get](#users-get) |
| Job Postings | [List](#job-postings-list), [Get](#job-postings-get) |
| Sources | [List](#sources-list) |
| Archive Reasons | [List](#archive-reasons-list) |
| Candidate Tags | [List](#candidate-tags-list) |
| Custom Fields | [List](#custom-fields-list) |
| Feedback Form Definitions | [List](#feedback-form-definitions-list) |

## Candidates

### Candidates List

Lists all candidates in the organization

#### Python SDK

```python
await ashby.candidates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `createdAt` | `string \| null` |  |
| `updatedAt` | `string \| null` |  |
| `name` | `string \| null` |  |
| `emailAddresses` | `array \| null` |  |
| `phoneNumbers` | `array \| null` |  |
| `socialLinks` | `array \| null` |  |
| `tags` | `array \| null` |  |
| `applicationIds` | `array \| null` |  |
| `fileHandles` | `array \| null` |  |
| `customFields` | `array \| null` |  |
| `profileUrl` | `string \| null` |  |
| `source` | `object \| any` |  |
| `creditedToUser` | `object \| any` |  |
| `timezone` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Candidates Get

Get a single candidate by ID

#### Python SDK

```python
await ashby.candidates.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidates",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Candidate ID |


## Applications

### Applications List

Gets all applications in the organization

#### Python SDK

```python
await ashby.applications.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "applications",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `createdAt` | `string \| null` |  |
| `updatedAt` | `string \| null` |  |
| `archivedAt` | `string \| null` |  |
| `candidate` | `object \| any` |  |
| `status` | `string \| null` |  |
| `customFields` | `array \| null` |  |
| `currentInterviewStage` | `object \| any` |  |
| `source` | `object \| any` |  |
| `creditedToUser` | `object \| any` |  |
| `archiveReason` | `object \| any` |  |
| `job` | `object \| any` |  |
| `hiringTeam` | `array \| null` |  |
| `appliedViaJobPostingId` | `string \| null` |  |
| `submitterClientIp` | `string \| null` |  |
| `submitterUserAgent` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Applications Get

Get a single application by ID

#### Python SDK

```python
await ashby.applications.get(
    application_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "applications",
    "action": "get",
    "params": {
        "applicationId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `applicationId` | `string` | Yes | Application ID |


## Jobs

### Jobs List

List all open, closed, and archived jobs

#### Python SDK

```python
await ashby.jobs.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `confidential` | `boolean \| null` |  |
| `status` | `string \| null` |  |
| `employmentType` | `string \| null` |  |
| `locationId` | `string \| null` |  |
| `departmentId` | `string \| null` |  |
| `defaultInterviewPlanId` | `string \| null` |  |
| `interviewPlanIds` | `array \| null` |  |
| `jobPostingIds` | `array \| null` |  |
| `customFields` | `array \| null` |  |
| `hiringTeam` | `array \| null` |  |
| `customRequisitionId` | `string \| null` |  |
| `brandId` | `string \| null` |  |
| `author` | `object \| any` |  |
| `createdAt` | `string \| null` |  |
| `updatedAt` | `string \| null` |  |
| `openedAt` | `string \| null` |  |
| `closedAt` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Jobs Get

Get a single job by ID

#### Python SDK

```python
await ashby.jobs.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Job ID |


## Departments

### Departments List

List all departments

#### Python SDK

```python
await ashby.departments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `externalName` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |
| `parentId` | `string \| null` |  |
| `createdAt` | `string \| null` |  |
| `updatedAt` | `string \| null` |  |
| `extraData` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Departments Get

Get a single department by ID

#### Python SDK

```python
await ashby.departments.get(
    department_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "get",
    "params": {
        "departmentId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `departmentId` | `string` | Yes | Department ID |


## Locations

### Locations List

List all locations

#### Python SDK

```python
await ashby.locations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `externalName` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |
| `address` | `object \| any` |  |
| `isRemote` | `boolean \| null` |  |
| `workplaceType` | `string \| null` |  |
| `parentLocationId` | `string \| null` |  |
| `type` | `string \| null` |  |
| `extraData` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Locations Get

Get a single location by ID

#### Python SDK

```python
await ashby.locations.get(
    location_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "get",
    "params": {
        "locationId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `locationId` | `string` | Yes | Location ID |


## Users

### Users List

List all users in the organization

#### Python SDK

```python
await ashby.users.list()
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
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `firstName` | `string \| null` |  |
| `lastName` | `string \| null` |  |
| `email` | `string \| null` |  |
| `globalRole` | `string \| null` |  |
| `isEnabled` | `boolean \| null` |  |
| `updatedAt` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Users Get

Get a single user by ID

#### Python SDK

```python
await ashby.users.get(
    user_id="<str>"
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
        "userId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `userId` | `string` | Yes | User ID |


## Job Postings

### Job Postings List

List all job postings

#### Python SDK

```python
await ashby.job_postings.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_postings",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `jobId` | `string \| null` |  |
| `departmentName` | `string \| null` |  |
| `teamName` | `string \| null` |  |
| `locationName` | `string \| null` |  |
| `locationExternalName` | `string \| null` |  |
| `workplaceType` | `string \| null` |  |
| `employmentType` | `string \| null` |  |
| `isListed` | `boolean \| null` |  |
| `publishedDate` | `string \| null` |  |
| `applicationDeadline` | `string \| null` |  |
| `externalLink` | `string \| null` |  |
| `applyLink` | `string \| null` |  |
| `locationIds` | `object \| any` |  |
| `compensationTierSummary` | `string \| null` |  |
| `shouldDisplayCompensationOnJobBoard` | `boolean \| null` |  |
| `updatedAt` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Job Postings Get

Get a single job posting by ID

#### Python SDK

```python
await ashby.job_postings.get(
    job_posting_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_postings",
    "action": "get",
    "params": {
        "jobPostingId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `jobPostingId` | `string` | Yes | Job posting ID |


## Sources

### Sources List

List all candidate sources

#### Python SDK

```python
await ashby.sources.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sources",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |
| `sourceType` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

## Archive Reasons

### Archive Reasons List

List all archive reasons

#### Python SDK

```python
await ashby.archive_reasons.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "archive_reasons",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `text` | `string \| null` |  |
| `reasonType` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

## Candidate Tags

### Candidate Tags List

List all candidate tags

#### Python SDK

```python
await ashby.candidate_tags.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidate_tags",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

## Custom Fields

### Custom Fields List

List all custom fields

#### Python SDK

```python
await ashby.custom_fields.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_fields",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `objectType` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |
| `isPrivate` | `boolean \| null` |  |
| `fieldType` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

## Feedback Form Definitions

### Feedback Form Definitions List

List all feedback form definitions

#### Python SDK

```python
await ashby.feedback_form_definitions.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "feedback_form_definitions",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Maximum number of records to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `organizationId` | `string \| null` |  |
| `title` | `string \| null` |  |
| `isArchived` | `boolean \| null` |  |
| `isDefaultForm` | `boolean \| null` |  |
| `formDefinition` | `object \| any` |  |
| `interviewId` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

