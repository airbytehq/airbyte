# Greenhouse full reference

This is the full reference documentation for the Greenhouse agent connector.

## Supported entities and actions

The Greenhouse connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Candidates | [List](#candidates-list), [Get](#candidates-get), [Search](#candidates-search) |
| Applications | [List](#applications-list), [Get](#applications-get), [Search](#applications-search) |
| Jobs | [List](#jobs-list), [Get](#jobs-get), [Search](#jobs-search) |
| Offers | [List](#offers-list), [Get](#offers-get), [Search](#offers-search) |
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Departments | [List](#departments-list), [Get](#departments-get), [Search](#departments-search) |
| Offices | [List](#offices-list), [Get](#offices-get), [Search](#offices-search) |
| Job Posts | [List](#job-posts-list), [Get](#job-posts-get), [Search](#job-posts-search) |
| Sources | [List](#sources-list), [Search](#sources-search) |
| Scheduled Interviews | [List](#scheduled-interviews-list), [Get](#scheduled-interviews-get) |
| Application Attachment | [Download](#application-attachment-download) |
| Candidate Attachment | [Download](#candidate-attachment-download) |

## Candidates

### Candidates List

Returns a paginated list of all candidates in the organization

#### Python SDK

```python
await greenhouse.candidates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Candidates Get

Get a single candidate by ID

#### Python SDK

```python
await greenhouse.candidates.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Candidate ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Candidates Search

Search and filter candidates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.candidates.search(
    query={"filter": {"eq": {"addresses": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidates",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"addresses": []}}}
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
| `addresses` | `array` | Candidate's addresses |
| `application_ids` | `array` | List of application IDs |
| `applications` | `array` | An array of all applications made by candidates. |
| `attachments` | `array` | Attachments related to the candidate |
| `can_email` | `boolean` | Indicates if candidate can be emailed |
| `company` | `string` | Company where the candidate is associated |
| `coordinator` | `string` | Coordinator assigned to the candidate |
| `created_at` | `string` | Date and time of creation |
| `custom_fields` | `object` | Custom fields associated with the candidate |
| `educations` | `array` | List of candidate's educations |
| `email_addresses` | `array` | Candidate's email addresses |
| `employments` | `array` | List of candidate's employments |
| `first_name` | `string` | Candidate's first name |
| `id` | `integer` | Candidate's ID |
| `is_private` | `boolean` | Indicates if the candidate's data is private |
| `keyed_custom_fields` | `object` | Keyed custom fields associated with the candidate |
| `last_activity` | `string` | Details of the last activity related to the candidate |
| `last_name` | `string` | Candidate's last name |
| `phone_numbers` | `array` | Candidate's phone numbers |
| `photo_url` | `string` | URL of the candidate's profile photo |
| `recruiter` | `string` | Recruiter assigned to the candidate |
| `social_media_addresses` | `array` | Candidate's social media addresses |
| `tags` | `array` | Tags associated with the candidate |
| `title` | `string` | Candidate's title (e.g., Mr., Mrs., Dr.) |
| `updated_at` | `string` | Date and time of last update |
| `website_addresses` | `array` | List of candidate's website addresses |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.addresses` | `array` | Candidate's addresses |
| `hits[].data.application_ids` | `array` | List of application IDs |
| `hits[].data.applications` | `array` | An array of all applications made by candidates. |
| `hits[].data.attachments` | `array` | Attachments related to the candidate |
| `hits[].data.can_email` | `boolean` | Indicates if candidate can be emailed |
| `hits[].data.company` | `string` | Company where the candidate is associated |
| `hits[].data.coordinator` | `string` | Coordinator assigned to the candidate |
| `hits[].data.created_at` | `string` | Date and time of creation |
| `hits[].data.custom_fields` | `object` | Custom fields associated with the candidate |
| `hits[].data.educations` | `array` | List of candidate's educations |
| `hits[].data.email_addresses` | `array` | Candidate's email addresses |
| `hits[].data.employments` | `array` | List of candidate's employments |
| `hits[].data.first_name` | `string` | Candidate's first name |
| `hits[].data.id` | `integer` | Candidate's ID |
| `hits[].data.is_private` | `boolean` | Indicates if the candidate's data is private |
| `hits[].data.keyed_custom_fields` | `object` | Keyed custom fields associated with the candidate |
| `hits[].data.last_activity` | `string` | Details of the last activity related to the candidate |
| `hits[].data.last_name` | `string` | Candidate's last name |
| `hits[].data.phone_numbers` | `array` | Candidate's phone numbers |
| `hits[].data.photo_url` | `string` | URL of the candidate's profile photo |
| `hits[].data.recruiter` | `string` | Recruiter assigned to the candidate |
| `hits[].data.social_media_addresses` | `array` | Candidate's social media addresses |
| `hits[].data.tags` | `array` | Tags associated with the candidate |
| `hits[].data.title` | `string` | Candidate's title (e.g., Mr., Mrs., Dr.) |
| `hits[].data.updated_at` | `string` | Date and time of last update |
| `hits[].data.website_addresses` | `array` | List of candidate's website addresses |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Applications

### Applications List

Returns a paginated list of all applications

#### Python SDK

```python
await greenhouse.applications.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by applications created before this timestamp |
| `created_after` | `string` | No | Filter by applications created after this timestamp |
| `last_activity_after` | `string` | No | Filter by applications with activity after this timestamp |
| `job_id` | `integer` | No | Filter by job ID |
| `status` | `"active" \| "rejected" \| "hired"` | No | Filter by application status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Applications Get

Get a single application by ID

#### Python SDK

```python
await greenhouse.applications.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Application ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Applications Search

Search and filter applications records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.applications.search(
    query={"filter": {"eq": {"answers": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "applications",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"answers": []}}}
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
| `answers` | `array` | Answers provided in the application. |
| `applied_at` | `string` | Timestamp when the candidate applied. |
| `attachments` | `array` | Attachments uploaded with the application. |
| `candidate_id` | `integer` | Unique identifier for the candidate. |
| `credited_to` | `object` | Information about the employee who credited the application. |
| `current_stage` | `object` | Current stage of the application process. |
| `id` | `integer` | Unique identifier for the application. |
| `job_post_id` | `integer` |  |
| `jobs` | `array` | Jobs applied for by the candidate. |
| `last_activity_at` | `string` | Timestamp of the last activity on the application. |
| `location` | `string` | Location related to the application. |
| `prospect` | `boolean` | Status of the application prospect. |
| `prospect_detail` | `object` | Details related to the application prospect. |
| `prospective_department` | `string` | Prospective department for the candidate. |
| `prospective_office` | `string` | Prospective office for the candidate. |
| `rejected_at` | `string` | Timestamp when the application was rejected. |
| `rejection_details` | `object` | Details related to the application rejection. |
| `rejection_reason` | `object` | Reason for the application rejection. |
| `source` | `object` | Source of the application. |
| `status` | `string` | Status of the application. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.answers` | `array` | Answers provided in the application. |
| `hits[].data.applied_at` | `string` | Timestamp when the candidate applied. |
| `hits[].data.attachments` | `array` | Attachments uploaded with the application. |
| `hits[].data.candidate_id` | `integer` | Unique identifier for the candidate. |
| `hits[].data.credited_to` | `object` | Information about the employee who credited the application. |
| `hits[].data.current_stage` | `object` | Current stage of the application process. |
| `hits[].data.id` | `integer` | Unique identifier for the application. |
| `hits[].data.job_post_id` | `integer` |  |
| `hits[].data.jobs` | `array` | Jobs applied for by the candidate. |
| `hits[].data.last_activity_at` | `string` | Timestamp of the last activity on the application. |
| `hits[].data.location` | `string` | Location related to the application. |
| `hits[].data.prospect` | `boolean` | Status of the application prospect. |
| `hits[].data.prospect_detail` | `object` | Details related to the application prospect. |
| `hits[].data.prospective_department` | `string` | Prospective department for the candidate. |
| `hits[].data.prospective_office` | `string` | Prospective office for the candidate. |
| `hits[].data.rejected_at` | `string` | Timestamp when the application was rejected. |
| `hits[].data.rejection_details` | `object` | Details related to the application rejection. |
| `hits[].data.rejection_reason` | `object` | Reason for the application rejection. |
| `hits[].data.source` | `object` | Source of the application. |
| `hits[].data.status` | `string` | Status of the application. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Jobs

### Jobs List

Returns a paginated list of all jobs in the organization

#### Python SDK

```python
await greenhouse.jobs.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Jobs Get

Get a single job by ID

#### Python SDK

```python
await greenhouse.jobs.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Job ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Jobs Search

Search and filter jobs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.jobs.search(
    query={"filter": {"eq": {"closed_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"closed_at": "<str>"}}}
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
| `closed_at` | `string` | The date and time the job was closed |
| `confidential` | `boolean` | Indicates if the job details are confidential |
| `copied_from_id` | `integer` | The ID of the job from which this job was copied |
| `created_at` | `string` | The date and time the job was created |
| `custom_fields` | `object` | Custom fields related to the job |
| `departments` | `array` | Departments associated with the job |
| `hiring_team` | `object` | Members of the hiring team for the job |
| `id` | `integer` | Unique ID of the job |
| `is_template` | `boolean` | Indicates if the job is a template |
| `keyed_custom_fields` | `object` | Keyed custom fields related to the job |
| `name` | `string` | Name of the job |
| `notes` | `string` | Additional notes or comments about the job |
| `offices` | `array` | Offices associated with the job |
| `opened_at` | `string` | The date and time the job was opened |
| `openings` | `array` | Openings associated with the job |
| `requisition_id` | `string` | ID associated with the job requisition |
| `status` | `string` | Current status of the job |
| `updated_at` | `string` | The date and time the job was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.closed_at` | `string` | The date and time the job was closed |
| `hits[].data.confidential` | `boolean` | Indicates if the job details are confidential |
| `hits[].data.copied_from_id` | `integer` | The ID of the job from which this job was copied |
| `hits[].data.created_at` | `string` | The date and time the job was created |
| `hits[].data.custom_fields` | `object` | Custom fields related to the job |
| `hits[].data.departments` | `array` | Departments associated with the job |
| `hits[].data.hiring_team` | `object` | Members of the hiring team for the job |
| `hits[].data.id` | `integer` | Unique ID of the job |
| `hits[].data.is_template` | `boolean` | Indicates if the job is a template |
| `hits[].data.keyed_custom_fields` | `object` | Keyed custom fields related to the job |
| `hits[].data.name` | `string` | Name of the job |
| `hits[].data.notes` | `string` | Additional notes or comments about the job |
| `hits[].data.offices` | `array` | Offices associated with the job |
| `hits[].data.opened_at` | `string` | The date and time the job was opened |
| `hits[].data.openings` | `array` | Openings associated with the job |
| `hits[].data.requisition_id` | `string` | ID associated with the job requisition |
| `hits[].data.status` | `string` | Current status of the job |
| `hits[].data.updated_at` | `string` | The date and time the job was last updated |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Offers

### Offers List

Returns a paginated list of all offers

#### Python SDK

```python
await greenhouse.offers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offers",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by offers created before this timestamp |
| `created_after` | `string` | No | Filter by offers created after this timestamp |
| `resolved_after` | `string` | No | Filter by offers resolved after this timestamp |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Offers Get

Get a single offer by ID

#### Python SDK

```python
await greenhouse.offers.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Offer ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Offers Search

Search and filter offers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.offers.search(
    query={"filter": {"eq": {"application_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"application_id": 0}}}
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
| `application_id` | `integer` | Unique identifier for the application associated with the offer |
| `candidate_id` | `integer` | Unique identifier for the candidate associated with the offer |
| `created_at` | `string` | Timestamp indicating when the offer was created |
| `custom_fields` | `object` | Additional custom fields related to the offer |
| `id` | `integer` | Unique identifier for the offer |
| `job_id` | `integer` | Unique identifier for the job associated with the offer |
| `keyed_custom_fields` | `object` | Keyed custom fields associated with the offer |
| `opening` | `object` | Details about the job opening |
| `resolved_at` | `string` | Timestamp indicating when the offer was resolved |
| `sent_at` | `string` | Timestamp indicating when the offer was sent |
| `starts_at` | `string` | Timestamp indicating when the offer starts |
| `status` | `string` | Status of the offer |
| `updated_at` | `string` | Timestamp indicating when the offer was last updated |
| `version` | `integer` | Version of the offer data |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.application_id` | `integer` | Unique identifier for the application associated with the offer |
| `hits[].data.candidate_id` | `integer` | Unique identifier for the candidate associated with the offer |
| `hits[].data.created_at` | `string` | Timestamp indicating when the offer was created |
| `hits[].data.custom_fields` | `object` | Additional custom fields related to the offer |
| `hits[].data.id` | `integer` | Unique identifier for the offer |
| `hits[].data.job_id` | `integer` | Unique identifier for the job associated with the offer |
| `hits[].data.keyed_custom_fields` | `object` | Keyed custom fields associated with the offer |
| `hits[].data.opening` | `object` | Details about the job opening |
| `hits[].data.resolved_at` | `string` | Timestamp indicating when the offer was resolved |
| `hits[].data.sent_at` | `string` | Timestamp indicating when the offer was sent |
| `hits[].data.starts_at` | `string` | Timestamp indicating when the offer starts |
| `hits[].data.status` | `string` | Status of the offer |
| `hits[].data.updated_at` | `string` | Timestamp indicating when the offer was last updated |
| `hits[].data.version` | `integer` | Version of the offer data |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Users

### Users List

Returns a paginated list of all users

#### Python SDK

```python
await greenhouse.users.list()
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `created_before` | `string` | No | Filter by users created before this timestamp |
| `created_after` | `string` | No | Filter by users created after this timestamp |
| `updated_before` | `string` | No | Filter by users updated before this timestamp |
| `updated_after` | `string` | No | Filter by users updated after this timestamp |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users Get

Get a single user by ID

#### Python SDK

```python
await greenhouse.users.get(
    id=0
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
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.users.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | The date and time when the user account was created. |
| `departments` | `array` | List of departments associated with users |
| `disabled` | `boolean` | Indicates whether the user account is disabled. |
| `emails` | `array` | Email addresses of the users |
| `employee_id` | `string` | Employee identifier for the user. |
| `first_name` | `string` | The first name of the user. |
| `id` | `integer` | Unique identifier for the user. |
| `last_name` | `string` | The last name of the user. |
| `linked_candidate_ids` | `array` | IDs of candidates linked to the user. |
| `name` | `string` | The full name of the user. |
| `offices` | `array` | List of office locations where users are based |
| `primary_email_address` | `string` | The primary email address of the user. |
| `site_admin` | `boolean` | Indicates whether the user is a site administrator. |
| `updated_at` | `string` | The date and time when the user account was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.created_at` | `string` | The date and time when the user account was created. |
| `hits[].data.departments` | `array` | List of departments associated with users |
| `hits[].data.disabled` | `boolean` | Indicates whether the user account is disabled. |
| `hits[].data.emails` | `array` | Email addresses of the users |
| `hits[].data.employee_id` | `string` | Employee identifier for the user. |
| `hits[].data.first_name` | `string` | The first name of the user. |
| `hits[].data.id` | `integer` | Unique identifier for the user. |
| `hits[].data.last_name` | `string` | The last name of the user. |
| `hits[].data.linked_candidate_ids` | `array` | IDs of candidates linked to the user. |
| `hits[].data.name` | `string` | The full name of the user. |
| `hits[].data.offices` | `array` | List of office locations where users are based |
| `hits[].data.primary_email_address` | `string` | The primary email address of the user. |
| `hits[].data.site_admin` | `boolean` | Indicates whether the user is a site administrator. |
| `hits[].data.updated_at` | `string` | The date and time when the user account was last updated. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Departments

### Departments List

Returns a paginated list of all departments

#### Python SDK

```python
await greenhouse.departments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Departments Get

Get a single department by ID

#### Python SDK

```python
await greenhouse.departments.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Department ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Departments Search

Search and filter departments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.departments.search(
    query={"filter": {"eq": {"child_department_external_ids": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"child_department_external_ids": []}}}
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
| `child_department_external_ids` | `array` | External IDs of child departments associated with this department. |
| `child_ids` | `array` | Unique IDs of child departments associated with this department. |
| `external_id` | `string` | External ID of this department. |
| `id` | `integer` | Unique ID of this department. |
| `name` | `string` | Name of the department. |
| `parent_department_external_id` | `string` | External ID of the parent department of this department. |
| `parent_id` | `integer` | Unique ID of the parent department of this department. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.child_department_external_ids` | `array` | External IDs of child departments associated with this department. |
| `hits[].data.child_ids` | `array` | Unique IDs of child departments associated with this department. |
| `hits[].data.external_id` | `string` | External ID of this department. |
| `hits[].data.id` | `integer` | Unique ID of this department. |
| `hits[].data.name` | `string` | Name of the department. |
| `hits[].data.parent_department_external_id` | `string` | External ID of the parent department of this department. |
| `hits[].data.parent_id` | `integer` | Unique ID of the parent department of this department. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Offices

### Offices List

Returns a paginated list of all offices

#### Python SDK

```python
await greenhouse.offices.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offices",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Offices Get

Get a single office by ID

#### Python SDK

```python
await greenhouse.offices.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Office ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Offices Search

Search and filter offices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.offices.search(
    query={"filter": {"eq": {"child_ids": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offices",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"child_ids": []}}}
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
| `child_ids` | `array` | IDs of child offices associated with this office |
| `child_office_external_ids` | `array` | External IDs of child offices associated with this office |
| `external_id` | `string` | Unique identifier for this office in the external system |
| `id` | `integer` | Unique identifier for this office in the API system |
| `location` | `object` | Location details of this office |
| `name` | `string` | Name of the office |
| `parent_id` | `integer` | ID of the parent office, if this office is a branch office |
| `parent_office_external_id` | `string` | External ID of the parent office in the external system |
| `primary_contact_user_id` | `integer` | User ID of the primary contact person for this office |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.child_ids` | `array` | IDs of child offices associated with this office |
| `hits[].data.child_office_external_ids` | `array` | External IDs of child offices associated with this office |
| `hits[].data.external_id` | `string` | Unique identifier for this office in the external system |
| `hits[].data.id` | `integer` | Unique identifier for this office in the API system |
| `hits[].data.location` | `object` | Location details of this office |
| `hits[].data.name` | `string` | Name of the office |
| `hits[].data.parent_id` | `integer` | ID of the parent office, if this office is a branch office |
| `hits[].data.parent_office_external_id` | `string` | External ID of the parent office in the external system |
| `hits[].data.primary_contact_user_id` | `integer` | User ID of the primary contact person for this office |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Job Posts

### Job Posts List

Returns a paginated list of all job posts

#### Python SDK

```python
await greenhouse.job_posts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_posts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |
| `live` | `boolean` | No | Filter by live status |
| `active` | `boolean` | No | Filter by active status |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Job Posts Get

Get a single job post by ID

#### Python SDK

```python
await greenhouse.job_posts.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Job Post ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Job Posts Search

Search and filter job posts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.job_posts.search(
    query={"filter": {"eq": {"active": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_posts",
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
| `active` | `boolean` | Flag indicating if the job post is active or not. |
| `content` | `string` | Content or description of the job post. |
| `created_at` | `string` | Date and time when the job post was created. |
| `demographic_question_set_id` | `integer` | ID of the demographic question set associated with the job post. |
| `external` | `boolean` | Flag indicating if the job post is external or not. |
| `first_published_at` | `string` | Date and time when the job post was first published. |
| `id` | `integer` | Unique identifier of the job post. |
| `internal` | `boolean` | Flag indicating if the job post is internal or not. |
| `internal_content` | `string` | Internal content or description of the job post. |
| `job_id` | `integer` | ID of the job associated with the job post. |
| `live` | `boolean` | Flag indicating if the job post is live or not. |
| `location` | `object` | Details about the job post location. |
| `questions` | `array` | List of questions related to the job post. |
| `title` | `string` | Title or headline of the job post. |
| `updated_at` | `string` | Date and time when the job post was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.active` | `boolean` | Flag indicating if the job post is active or not. |
| `hits[].data.content` | `string` | Content or description of the job post. |
| `hits[].data.created_at` | `string` | Date and time when the job post was created. |
| `hits[].data.demographic_question_set_id` | `integer` | ID of the demographic question set associated with the job post. |
| `hits[].data.external` | `boolean` | Flag indicating if the job post is external or not. |
| `hits[].data.first_published_at` | `string` | Date and time when the job post was first published. |
| `hits[].data.id` | `integer` | Unique identifier of the job post. |
| `hits[].data.internal` | `boolean` | Flag indicating if the job post is internal or not. |
| `hits[].data.internal_content` | `string` | Internal content or description of the job post. |
| `hits[].data.job_id` | `integer` | ID of the job associated with the job post. |
| `hits[].data.live` | `boolean` | Flag indicating if the job post is live or not. |
| `hits[].data.location` | `object` | Details about the job post location. |
| `hits[].data.questions` | `array` | List of questions related to the job post. |
| `hits[].data.title` | `string` | Title or headline of the job post. |
| `hits[].data.updated_at` | `string` | Date and time when the job post was last updated. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Sources

### Sources List

Returns a paginated list of all sources

#### Python SDK

```python
await greenhouse.sources.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `per_page` | `integer` | No | Number of items to return per page (max 500) |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `type` | `object \| null` |  |


</details>

### Sources Search

Search and filter sources records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await greenhouse.sources.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sources",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
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
| `id` | `integer` | The unique identifier for the source. |
| `name` | `string` | The name of the source. |
| `type` | `object` | Type of the data source |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `integer` | The unique identifier for the source. |
| `hits[].data.name` | `string` | The name of the source. |
| `hits[].data.type` | `object` | Type of the data source |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Scheduled Interviews

### Scheduled Interviews List

Returns a paginated list of all scheduled interviews

#### Python SDK

```python
await greenhouse.scheduled_interviews.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "scheduled_interviews",
    "action": "list"
}'
```


#### Parameters

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


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Scheduled Interviews Get

Get a single scheduled interview by ID

#### Python SDK

```python
await greenhouse.scheduled_interviews.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Scheduled Interview ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Application Attachment

### Application Attachment Download

Downloads an attachment (resume, cover letter, etc.) for an application by index.
The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
Files should be downloaded immediately after retrieval.


#### Python SDK

```python
async for chunk in greenhouse.application_attachment.download(    id=0,    attachment_index=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Application ID |
| `attachment_index` | `integer` | Yes | Index of the attachment to download (0-based) |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


## Candidate Attachment

### Candidate Attachment Download

Downloads an attachment (resume, cover letter, etc.) for a candidate by index.
The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
Files should be downloaded immediately after retrieval.


#### Python SDK

```python
async for chunk in greenhouse.candidate_attachment.download(    id=0,    attachment_index=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Candidate ID |
| `attachment_index` | `integer` | Yes | Index of the attachment to download (0-based) |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


