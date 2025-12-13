# Greenhouse

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Candidates | [List](#candidates-list), [Get](#candidates-get) |
| Applications | [List](#applications-list), [Get](#applications-get) |
| Jobs | [List](#jobs-list), [Get](#jobs-get) |
| Offers | [List](#offers-list), [Get](#offers-get) |
| Users | [List](#users-list), [Get](#users-get) |
| Departments | [List](#departments-list), [Get](#departments-get) |
| Offices | [List](#offices-list), [Get](#offices-get) |
| Job Posts | [List](#job-posts-list), [Get](#job-posts-get) |
| Sources | [List](#sources-list) |
| Scheduled Interviews | [List](#scheduled-interviews-list), [Get](#scheduled-interviews-get) |
| Application Attachment | [Download](#application-attachment-download) |
| Candidate Attachment | [Download](#candidate-attachment-download) |

### Candidates

#### Candidates List

Returns a paginated list of all candidates in the organization

**Python SDK**

```python
greenhouse.candidates.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidates",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


#### Candidates Get

Get a single candidate by ID

**Python SDK**

```python
greenhouse.candidates.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidates",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Candidate ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `first_name` | `string` |  |
| `last_name` | `string` |  |
| `company` | `string \| null` |  |
| `title` | `string \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `last_activity` | `string` |  |
| `is_private` | `boolean` |  |
| `photo_url` | `string \| null` |  |
| `attachments` | `array<object>` |  |
| `attachments[].filename` | `string` |  |
| `attachments[].url` | `string` |  |
| `attachments[].type` | `"resume" \| "cover_letter" \| "admin_only" \| "take_home_test" \| "offer_packet" \| "offer_letter" \| "signed_offer_letter" \| "other"` |  |
| `attachments[].created_at` | `string` |  |
| `application_ids` | `array<integer>` |  |
| `phone_numbers` | `array<object>` |  |
| `addresses` | `array<object>` |  |
| `email_addresses` | `array<object>` |  |
| `website_addresses` | `array<object>` |  |
| `social_media_addresses` | `array<object>` |  |
| `recruiter` | `object \| null` |  |
| `coordinator` | `object \| null` |  |
| `can_email` | `boolean` |  |
| `tags` | `array<string>` |  |
| `custom_fields` | `object` |  |


</details>

### Applications

#### Applications List

Returns a paginated list of all applications

**Python SDK**

```python
greenhouse.applications.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "applications",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by applications created before this timestamp |
| `created_after` | `string` | No | Filter by applications created after this timestamp |
| `last_activity_after` | `string` | No | Filter by applications with activity after this timestamp |
| `job_id` | `integer` | No | Filter by job ID |
| `status` | `"active" \| "rejected" \| "hired"` | No | Filter by application status |


#### Applications Get

Get a single application by ID

**Python SDK**

```python
greenhouse.applications.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "applications",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Application ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `candidate_id` | `integer` |  |
| `prospect` | `boolean` |  |
| `applied_at` | `string` |  |
| `rejected_at` | `string \| null` |  |
| `last_activity_at` | `string` |  |
| `location` | `object \| null` |  |
| `source` | `object` |  |
| `credited_to` | `object` |  |
| `rejection_reason` | `object \| null` |  |
| `rejection_details` | `object \| null` |  |
| `jobs` | `array<object>` |  |
| `job_post_id` | `integer \| null` |  |
| `status` | `string` |  |
| `current_stage` | `object \| null` |  |
| `answers` | `array<object>` |  |
| `prospective_office` | `object \| null` |  |
| `prospective_department` | `object \| null` |  |
| `prospect_detail` | `object` |  |
| `attachments` | `array<object>` |  |
| `attachments[].filename` | `string` |  |
| `attachments[].url` | `string` |  |
| `attachments[].type` | `"resume" \| "cover_letter" \| "admin_only" \| "take_home_test" \| "offer_packet" \| "offer_letter" \| "signed_offer_letter" \| "other"` |  |
| `attachments[].created_at` | `string` |  |
| `custom_fields` | `object` |  |


</details>

### Jobs

#### Jobs List

Returns a paginated list of all jobs in the organization

**Python SDK**

```python
greenhouse.jobs.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


#### Jobs Get

Get a single job by ID

**Python SDK**

```python
greenhouse.jobs.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Job ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `requisition_id` | `string \| null` |  |
| `notes` | `string \| null` |  |
| `confidential` | `boolean` |  |
| `status` | `string` |  |
| `created_at` | `string` |  |
| `opened_at` | `string` |  |
| `closed_at` | `string \| null` |  |
| `updated_at` | `string` |  |
| `departments` | `array<object \| null>` |  |
| `offices` | `array<object>` |  |
| `custom_fields` | `object` |  |
| `hiring_team` | `object` |  |
| `openings` | `array<object>` |  |


</details>

### Offers

#### Offers List

Returns a paginated list of all offers

**Python SDK**

```python
greenhouse.offers.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offers",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by offers created before this timestamp |
| `created_after` | `string` | No | Filter by offers created after this timestamp |
| `resolved_after` | `string` | No | Filter by offers resolved after this timestamp |


#### Offers Get

Get a single offer by ID

**Python SDK**

```python
greenhouse.offers.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offers",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Offer ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `version` | `integer` |  |
| `application_id` | `integer` |  |
| `job_id` | `integer` |  |
| `candidate_id` | `integer` |  |
| `opening` | `object \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `sent_at` | `string \| null` |  |
| `resolved_at` | `string \| null` |  |
| `starts_at` | `string \| null` |  |
| `status` | `string` |  |
| `custom_fields` | `object` |  |


</details>

### Users

#### Users List

Returns a paginated list of all users

**Python SDK**

```python
greenhouse.users.list()
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by users created before this timestamp |
| `created_after` | `string` | No | Filter by users created after this timestamp |
| `updated_before` | `string` | No | Filter by users updated before this timestamp |
| `updated_after` | `string` | No | Filter by users updated after this timestamp |


#### Users Get

Get a single user by ID

**Python SDK**

```python
greenhouse.users.get(
    id=0
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
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `first_name` | `string` |  |
| `last_name` | `string` |  |
| `primary_email_address` | `string` |  |
| `updated_at` | `string` |  |
| `created_at` | `string` |  |
| `disabled` | `boolean` |  |
| `site_admin` | `boolean` |  |
| `emails` | `array<string>` |  |
| `employee_id` | `string \| null` |  |
| `linked_candidate_ids` | `array<integer>` |  |
| `offices` | `array<object>` |  |
| `departments` | `array<object>` |  |


</details>

### Departments

#### Departments List

Returns a paginated list of all departments

**Python SDK**

```python
greenhouse.departments.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


#### Departments Get

Get a single department by ID

**Python SDK**

```python
greenhouse.departments.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Department ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `parent_id` | `integer \| null` |  |
| `parent_department_external_id` | `string \| null` |  |
| `child_ids` | `array<integer>` |  |
| `child_department_external_ids` | `array<string>` |  |
| `external_id` | `string \| null` |  |


</details>

### Offices

#### Offices List

Returns a paginated list of all offices

**Python SDK**

```python
greenhouse.offices.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offices",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


#### Offices Get

Get a single office by ID

**Python SDK**

```python
greenhouse.offices.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offices",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Office ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `location` | `object \| null` |  |
| `primary_contact_user_id` | `integer \| null` |  |
| `parent_id` | `integer \| null` |  |
| `parent_office_external_id` | `string \| null` |  |
| `child_ids` | `array<integer>` |  |
| `child_office_external_ids` | `array<string>` |  |
| `external_id` | `string \| null` |  |


</details>

### Job Posts

#### Job Posts List

Returns a paginated list of all job posts

**Python SDK**

```python
greenhouse.job_posts.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_posts",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `live` | `boolean` | No | Filter by live status |
| `active` | `boolean` | No | Filter by active status |


#### Job Posts Get

Get a single job post by ID

**Python SDK**

```python
greenhouse.job_posts.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_posts",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Job Post ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `title` | `string` |  |
| `location` | `object \| null` |  |
| `internal` | `boolean` |  |
| `external` | `boolean` |  |
| `active` | `boolean` |  |
| `live` | `boolean` |  |
| `first_published_at` | `string \| null` |  |
| `job_id` | `integer` |  |
| `content` | `string \| null` |  |
| `internal_content` | `string \| null` |  |
| `updated_at` | `string` |  |
| `created_at` | `string` |  |
| `demographic_question_set_id` | `integer \| null` |  |
| `questions` | `array<object>` |  |


</details>

### Sources

#### Sources List

Returns a paginated list of all sources

**Python SDK**

```python
greenhouse.sources.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sources",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


### Scheduled Interviews

#### Scheduled Interviews List

Returns a paginated list of all scheduled interviews

**Python SDK**

```python
greenhouse.scheduled_interviews.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "scheduled_interviews",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by interviews created before this timestamp |
| `created_after` | `string` | No | Filter by interviews created after this timestamp |
| `updated_before` | `string` | No | Filter by interviews updated before this timestamp |
| `updated_after` | `string` | No | Filter by interviews updated after this timestamp |
| `starts_after` | `string` | No | Filter by interviews starting after this timestamp |
| `ends_before` | `string` | No | Filter by interviews ending before this timestamp |


#### Scheduled Interviews Get

Get a single scheduled interview by ID

**Python SDK**

```python
greenhouse.scheduled_interviews.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "scheduled_interviews",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Scheduled Interview ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `application_id` | `integer` |  |
| `external_event_id` | `string \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `start` | `object \| null` |  |
| `end` | `object \| null` |  |
| `location` | `string \| null` |  |
| `video_conferencing_url` | `string \| null` |  |
| `status` | `string` |  |
| `interview` | `object \| null` |  |
| `organizer` | `object \| null` |  |
| `interviewers` | `array<object>` |  |


</details>

### Application Attachment

#### Application Attachment Download

Downloads an attachment (resume, cover letter, etc.) for an application by index.
The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
Files should be downloaded immediately after retrieval.


**Python SDK**

```python
async for chunk in greenhouse.application_attachment.download(    id=0,    attachment_index=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "application_attachment",
    "action": "download",
    "params": {
        "id": 0,
        "attachment_index": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Application ID |
| `attachment_index` | `integer` | Yes | Index of the attachment to download (0-based) |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Candidate Attachment

#### Candidate Attachment Download

Downloads an attachment (resume, cover letter, etc.) for a candidate by index.
The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
Files should be downloaded immediately after retrieval.


**Python SDK**

```python
async for chunk in greenhouse.candidate_attachment.download(    id=0,    attachment_index=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidate_attachment",
    "action": "download",
    "params": {
        "id": 0,
        "attachment_index": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Candidate ID |
| `attachment_index` | `integer` | Yes | Index of the attachment to download (0-based) |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |




## Authentication

The Greenhouse connector supports the following authentication methods:


### Harvest API Key Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Greenhouse Harvest API Key from the Dev Center |

#### Example

**Python SDK**

```python
GreenhouseConnector(
  auth_config=GreenhouseAuthConfig(
    api_key="<Your Greenhouse Harvest API Key from the Dev Center>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "59f1e50a-331f-4f09-b3e8-2e8d4d355f44",
  "auth_config": {
    "api_key": "<Your Greenhouse Harvest API Key from the Dev Center>"
  },
  "name": "My Greenhouse Connector"
}'
```

