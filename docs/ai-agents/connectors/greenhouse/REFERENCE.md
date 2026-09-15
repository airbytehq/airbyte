# Greenhouse full reference

This is the full reference documentation for the Greenhouse agent connector.

## Supported entities and actions

The Greenhouse connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Applications | [List](#applications-list), [Context Store Search](#applications-context-store-search) |
| Candidates | [List](#candidates-list), [Context Store Search](#candidates-context-store-search) |
| Departments | [List](#departments-list), [Context Store Search](#departments-context-store-search) |
| Interviews | [List](#interviews-list) |
| Job Posts | [List](#job-posts-list), [Context Store Search](#job-posts-context-store-search), [Semantic Search](#job-posts-semantic-search) |
| Jobs | [List](#jobs-list), [Context Store Search](#jobs-context-store-search), [Semantic Search](#jobs-semantic-search) |
| Offers | [List](#offers-list), [Context Store Search](#offers-context-store-search) |
| Offices | [List](#offices-list), [Context Store Search](#offices-context-store-search) |
| Sources | [List](#sources-list), [Context Store Search](#sources-context-store-search) |
| Users | [List](#users-list), [Context Store Search](#users-context-store-search) |
| Attachments | [List](#attachments-list), [Download](#attachments-download) |

## Applications

### Applications List

Returns a cursor-paginated list of applications.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "applications",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.applications.list()
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `agency_note_id` | `null \| integer` |  |
| `answers` | `null \| array` |  |
| `candidate_id` | `null \| integer` |  |
| `coordinator_id` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `id` | `null \| integer` |  |
| `job_id` | `null \| integer` |  |
| `job_interview_stage_id` | `null \| integer` |  |
| `job_post_id` | `null \| integer` |  |
| `last_activity_at` | `null \| string` |  |
| `location_address` | `null \| string` |  |
| `needs_decision` | `null \| boolean` |  |
| `prospect` | `null \| boolean` |  |
| `prospective_job_ids` | `null \| array` |  |
| `recruiter_id` | `null \| integer` |  |
| `referrer_id` | `null \| integer` |  |
| `rejected_at` | `null \| string` |  |
| `rejection_reason_id` | `null \| integer` |  |
| `source_id` | `null \| integer` |  |
| `stage_id` | `null \| integer` |  |
| `stage_name` | `null \| string` |  |
| `status` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Applications Context Store Search

Search and filter applications records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "applications",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "agency_note_id": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.applications.context_store_search(
    query={"filter": {"eq": {"agency_note_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "applications",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"agency_note_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `agency_note_id` | `integer` | Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency. |
| `answers` | `array` | Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer. |
| `candidate_id` | `integer` | Id of the candidate (person) this application belongs to. |
| `coordinator_id` | `integer` | Id of the user assigned as coordinator on the application's job, or `null` when unassigned. |
| `created_at` | `string` | Created at from the Greenhouse v3 applications record. |
| `custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `id` | `integer` | Id from the Greenhouse v3 applications record. |
| `job_id` | `integer` | Id of the job this application is on. `null` for jobless prospect applications. |
| `job_interview_stage_id` | `integer` | Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state. |
| `job_post_id` | `integer` | Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role. |
| `last_activity_at` | `string` | Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601. |
| `location_address` | `string` | Free-form location string captured on the application (typically from the job post's location question). |
| `needs_decision` | `boolean` | `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage. |
| `prospect` | `boolean` | `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job. |
| `prospective_job_ids` | `array` | For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects. |
| `recruiter_id` | `integer` | Id of the user assigned as recruiter on the application's job, or `null` when unassigned. |
| `referrer_id` | `integer` | Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user. |
| `rejected_at` | `string` | Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected. |
| `rejection_reason_id` | `integer` | Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected. |
| `source_id` | `integer` | Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set. |
| `stage_id` | `integer` | Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state. |
| `stage_name` | `string` | Display name of the candidate's current interview stage on this application. |
| `status` | `string` | Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 applications record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].agency_note_id` | `integer` | Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency. |
| `data[].answers` | `array` | Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer. |
| `data[].candidate_id` | `integer` | Id of the candidate (person) this application belongs to. |
| `data[].coordinator_id` | `integer` | Id of the user assigned as coordinator on the application's job, or `null` when unassigned. |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 applications record. |
| `data[].custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `data[].id` | `integer` | Id from the Greenhouse v3 applications record. |
| `data[].job_id` | `integer` | Id of the job this application is on. `null` for jobless prospect applications. |
| `data[].job_interview_stage_id` | `integer` | Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state. |
| `data[].job_post_id` | `integer` | Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role. |
| `data[].last_activity_at` | `string` | Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601. |
| `data[].location_address` | `string` | Free-form location string captured on the application (typically from the job post's location question). |
| `data[].needs_decision` | `boolean` | `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage. |
| `data[].prospect` | `boolean` | `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job. |
| `data[].prospective_job_ids` | `array` | For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects. |
| `data[].recruiter_id` | `integer` | Id of the user assigned as recruiter on the application's job, or `null` when unassigned. |
| `data[].referrer_id` | `integer` | Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user. |
| `data[].rejected_at` | `string` | Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected. |
| `data[].rejection_reason_id` | `integer` | Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected. |
| `data[].source_id` | `integer` | Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set. |
| `data[].stage_id` | `integer` | Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state. |
| `data[].stage_name` | `string` | Display name of the candidate's current interview stage on this application. |
| `data[].status` | `string` | Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 applications record. |

</details>

## Candidates

### Candidates List

Returns a cursor-paginated list of candidates.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "candidates",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.candidates.list()
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `addresses` | `null \| array` |  |
| `can_email` | `null \| boolean` |  |
| `company` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `email_addresses` | `null \| array` |  |
| `first_name` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `last_activity_at` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `linked_user_ids` | `null \| array` |  |
| `phone_numbers` | `null \| array` |  |
| `preferred_name` | `null \| string` |  |
| `private` | `null \| boolean` |  |
| `social_media_addresses` | `null \| array` |  |
| `tags` | `null \| array` |  |
| `time_zone` | `null \| string` |  |
| `title` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `website_addresses` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Candidates Context Store Search

Search and filter candidates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "candidates",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "addresses": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.candidates.context_store_search(
    query={"filter": {"eq": {"addresses": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "candidates",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"addresses": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `addresses` | `array` | Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`. |
| `can_email` | `boolean` | Whether this candidate has consented to receive email communication from your organization. |
| `company` | `string` | Candidate's current company, as entered on their profile. |
| `created_at` | `string` | Created at from the Greenhouse v3 candidates record. |
| `custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `email_addresses` | `array` | Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`. |
| `first_name` | `string` | First name from the Greenhouse v3 candidates record. |
| `id` | `integer` | Id from the Greenhouse v3 candidates record. |
| `last_activity_at` | `string` | Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601. |
| `last_name` | `string` | Last name from the Greenhouse v3 candidates record. |
| `linked_user_ids` | `array` | Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record). |
| `phone_numbers` | `array` | Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`. |
| `preferred_name` | `string` | Preferred or chosen name the candidate goes by, when different from their legal first name. |
| `private` | `boolean` | If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`. |
| `social_media_addresses` | `array` | Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned. |
| `tags` | `array` | Candidate tag names applied to this candidate within your organization. |
| `time_zone` | `string` | Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`). |
| `title` | `string` | Candidate's current job title, as entered on their profile. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 candidates record. |
| `website_addresses` | `array` | Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].addresses` | `array` | Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`. |
| `data[].can_email` | `boolean` | Whether this candidate has consented to receive email communication from your organization. |
| `data[].company` | `string` | Candidate's current company, as entered on their profile. |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 candidates record. |
| `data[].custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `data[].email_addresses` | `array` | Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`. |
| `data[].first_name` | `string` | First name from the Greenhouse v3 candidates record. |
| `data[].id` | `integer` | Id from the Greenhouse v3 candidates record. |
| `data[].last_activity_at` | `string` | Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601. |
| `data[].last_name` | `string` | Last name from the Greenhouse v3 candidates record. |
| `data[].linked_user_ids` | `array` | Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record). |
| `data[].phone_numbers` | `array` | Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`. |
| `data[].preferred_name` | `string` | Preferred or chosen name the candidate goes by, when different from their legal first name. |
| `data[].private` | `boolean` | If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`. |
| `data[].social_media_addresses` | `array` | Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned. |
| `data[].tags` | `array` | Candidate tag names applied to this candidate within your organization. |
| `data[].time_zone` | `string` | Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`). |
| `data[].title` | `string` | Candidate's current job title, as entered on their profile. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 candidates record. |
| `data[].website_addresses` | `array` | Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`. |

</details>

## Departments

### Departments List

Returns a cursor-paginated list of departments.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "departments",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.departments.list()
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `null \| string` |  |
| `external_id` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `parent_id` | `null \| integer` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Departments Context Store Search

Search and filter departments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "departments",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "created_at": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.departments.context_store_search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "departments",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"created_at": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | Created at from the Greenhouse v3 departments record. |
| `external_id` | `string` | Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set. |
| `id` | `integer` | Id from the Greenhouse v3 departments record. |
| `name` | `string` | Display name of the department (e.g. `Engineering`, `Marketing`). |
| `parent_id` | `integer` | Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 departments record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 departments record. |
| `data[].external_id` | `string` | Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set. |
| `data[].id` | `integer` | Id from the Greenhouse v3 departments record. |
| `data[].name` | `string` | Display name of the department (e.g. `Engineering`, `Marketing`). |
| `data[].parent_id` | `integer` | Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 departments record. |

</details>

## Interviews

### Interviews List

Returns a cursor-paginated list of interviews.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "interviews",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.interviews.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "interviews",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `all_day_end_on` | `null \| string` |  |
| `all_day_start_on` | `null \| string` |  |
| `application_id` | `null \| integer` |  |
| `availability_received_at` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `ends_at` | `null \| string` |  |
| `external_event_id` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `job_id` | `null \| integer` |  |
| `job_interview_id` | `null \| integer` |  |
| `location` | `null \| string` |  |
| `organizer_id` | `null \| integer` |  |
| `scheduled_at` | `null \| string` |  |
| `starts_at` | `null \| string` |  |
| `status` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `video_conferencing_url` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

## Job Posts

### Job Posts List

Returns a cursor-paginated list of job posts.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "job_posts",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.job_posts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |
| `active` | `boolean` | No | Filter by active status. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `active` | `null \| boolean` |  |
| `content` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `demographic_question_set_id` | `null \| integer` |  |
| `featured` | `null \| boolean` |  |
| `first_published_at` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `internal` | `null \| boolean` |  |
| `internal_content` | `null \| string` |  |
| `job_board_id` | `null \| integer` |  |
| `job_id` | `null \| integer` |  |
| `language` | `null \| string` |  |
| `live` | `null \| boolean` |  |
| `public_url` | `null \| string` |  |
| `questions` | `null \| array` |  |
| `title` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Job Posts Context Store Search

Search and filter job posts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "job_posts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "active": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.job_posts.context_store_search(
    query={"filter": {"eq": {"active": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_posts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"active": True}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `active` | `boolean` | If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them. |
| `content` | `string` | HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded. |
| `created_at` | `string` | Created at from the Greenhouse v3 job posts record. |
| `demographic_question_set_id` | `integer` | Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data. |
| `featured` | `boolean` | If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time. |
| `first_published_at` | `string` | Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published. |
| `id` | `integer` | Id from the Greenhouse v3 job posts record. |
| `internal` | `boolean` | If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time. |
| `internal_content` | `string` | HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`. |
| `job_board_id` | `integer` | Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time. |
| `job_id` | `integer` | Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan. |
| `language` | `string` | ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen. |
| `live` | `boolean` | If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled. |
| `public_url` | `string` | Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured. |
| `questions` | `array` | Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form. |
| `title` | `string` | Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 job posts record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].active` | `boolean` | If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them. |
| `data[].content` | `string` | HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded. |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 job posts record. |
| `data[].demographic_question_set_id` | `integer` | Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data. |
| `data[].featured` | `boolean` | If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time. |
| `data[].first_published_at` | `string` | Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published. |
| `data[].id` | `integer` | Id from the Greenhouse v3 job posts record. |
| `data[].internal` | `boolean` | If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time. |
| `data[].internal_content` | `string` | HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`. |
| `data[].job_board_id` | `integer` | Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time. |
| `data[].job_id` | `integer` | Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan. |
| `data[].language` | `string` | ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen. |
| `data[].live` | `boolean` | If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled. |
| `data[].public_url` | `string` | Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured. |
| `data[].questions` | `array` | Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form. |
| `data[].title` | `string` | Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 job posts record. |

</details>

### Job Posts Semantic Search

Search job posts records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "job_posts",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "content", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `job_posts.context_store_search` helper only accepts `query`.

```python
await greenhouse.execute(
    "job_posts",
    "context_store_search",
    {"semantic": {"field": "content", "prompt": "<your natural-language query>"}},
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "job_posts",
    "action": "context_store_search",
    "params": {
        "semantic": {"field": "content", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `content` | 2048 | HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded. |
| `internal_content` | 2048 | HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.updated_at` | `string` | Source record field |
| `data[].entity.title` | `string` | Source record field |
| `data[].entity.job_id` | `string` | Source record field |
| `data[].entity.live` | `string` | Source record field |
| `data[].entity.internal` | `string` | Source record field |
| `data[].entity.first_published_at` | `string` | Source record field |
| `data[].entity.created_at` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Jobs

### Jobs List

Returns a cursor-paginated list of jobs.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "jobs",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.jobs.list()
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `closed_at` | `null \| string` |  |
| `confidential` | `null \| boolean` |  |
| `copied_from_id` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `department_id` | `null \| integer` |  |
| `id` | `null \| integer` |  |
| `is_template` | `null \| boolean` |  |
| `name` | `null \| string` |  |
| `notes` | `null \| string` |  |
| `office_ids` | `null \| array` |  |
| `opened_at` | `null \| string` |  |
| `requisition_id` | `null \| string` |  |
| `status` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Jobs Context Store Search

Search and filter jobs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "jobs",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "closed_at": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.jobs.context_store_search(
    query={"filter": {"eq": {"closed_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"closed_at": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `closed_at` | `string` | Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`. |
| `confidential` | `boolean` | If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled. |
| `copied_from_id` | `integer` | Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job. |
| `created_at` | `string` | Created at from the Greenhouse v3 jobs record. |
| `custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `department_id` | `integer` | Id of the department this job is assigned to. `null` when no department is set. |
| `id` | `integer` | Id from the Greenhouse v3 jobs record. |
| `is_template` | `boolean` | If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`. |
| `name` | `string` | Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`. |
| `notes` | `string` | Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts. |
| `office_ids` | `array` | Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set. |
| `opened_at` | `string` | Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`. |
| `requisition_id` | `string` | Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set. |
| `status` | `string` | Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/\{id\}`. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 jobs record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].closed_at` | `string` | Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`. |
| `data[].confidential` | `boolean` | If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled. |
| `data[].copied_from_id` | `integer` | Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job. |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 jobs record. |
| `data[].custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `data[].department_id` | `integer` | Id of the department this job is assigned to. `null` when no department is set. |
| `data[].id` | `integer` | Id from the Greenhouse v3 jobs record. |
| `data[].is_template` | `boolean` | If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`. |
| `data[].name` | `string` | Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`. |
| `data[].notes` | `string` | Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts. |
| `data[].office_ids` | `array` | Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set. |
| `data[].opened_at` | `string` | Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`. |
| `data[].requisition_id` | `string` | Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set. |
| `data[].status` | `string` | Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/\{id\}`. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 jobs record. |

</details>

### Jobs Semantic Search

Search jobs records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass `semantic={field, prompt, filter?, context_size?, min_similarity?, dedup?}` to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "jobs",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "notes", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `jobs.context_store_search` helper only accepts `query`.

```python
await greenhouse.execute(
    "jobs",
    "context_store_search",
    {"semantic": {"field": "notes", "prompt": "<your natural-language query>"}},
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "jobs",
    "action": "context_store_search",
    "params": {
        "semantic": {"field": "notes", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score in [-1.0, 1.0]. Omit for 0.25; scores below the threshold are discarded before deduplication and top-k selection. Use -1.0 to disable the cutoff. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `notes` | 2048 | Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.updated_at` | `string` | Source record field |
| `data[].entity.name` | `string` | Source record field |
| `data[].entity.status` | `string` | Source record field |
| `data[].entity.requisition_id` | `string` | Source record field |
| `data[].entity.confidential` | `string` | Source record field |
| `data[].entity.opened_at` | `string` | Source record field |
| `data[].entity.closed_at` | `string` | Source record field |
| `data[].entity.created_at` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Offers

### Offers List

Returns a cursor-paginated list of offers.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "offers",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.offers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `application_id` | `null \| integer` |  |
| `candidate_id` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `id` | `null \| integer` |  |
| `job_id` | `null \| integer` |  |
| `opening_id` | `null \| integer` |  |
| `resolved_at` | `null \| string` |  |
| `sent_on` | `null \| string` |  |
| `starts_on` | `null \| string` |  |
| `status` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `version` | `null \| integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Offers Context Store Search

Search and filter offers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "offers",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "application_id": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.offers.context_store_search(
    query={"filter": {"eq": {"application_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offers",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"application_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `application_id` | `integer` | Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted. |
| `candidate_id` | `integer` | Id of the candidate (person) receiving this offer. Resolved through the offer's application. |
| `created_at` | `string` | Created at from the Greenhouse v3 offers record. |
| `custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `id` | `integer` | Id from the Greenhouse v3 offers record. |
| `job_id` | `integer` | Id of the job this offer's application is on. |
| `opening_id` | `integer` | Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening. |
| `resolved_at` | `string` | Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/\{id\}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution. |
| `sent_on` | `string` | Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent. |
| `starts_on` | `string` | Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer. |
| `status` | `string` | Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status). |
| `updated_at` | `string` | Updated at from the Greenhouse v3 offers record. |
| `version` | `integer` | Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].application_id` | `integer` | Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted. |
| `data[].candidate_id` | `integer` | Id of the candidate (person) receiving this offer. Resolved through the offer's application. |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 offers record. |
| `data[].custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `data[].id` | `integer` | Id from the Greenhouse v3 offers record. |
| `data[].job_id` | `integer` | Id of the job this offer's application is on. |
| `data[].opening_id` | `integer` | Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening. |
| `data[].resolved_at` | `string` | Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/\{id\}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution. |
| `data[].sent_on` | `string` | Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent. |
| `data[].starts_on` | `string` | Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer. |
| `data[].status` | `string` | Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status). |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 offers record. |
| `data[].version` | `integer` | Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application. |

</details>

## Offices

### Offices List

Returns a cursor-paginated list of offices.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "offices",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.offices.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `null \| string` |  |
| `external_id` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `location` | `null \| string` |  |
| `name` | `null \| string` |  |
| `parent_id` | `null \| integer` |  |
| `primary_in_house_contact_user_id` | `null \| integer` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Offices Context Store Search

Search and filter offices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "offices",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "created_at": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.offices.context_store_search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "offices",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"created_at": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | Created at from the Greenhouse v3 offices record. |
| `external_id` | `string` | Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled. |
| `id` | `integer` | Id from the Greenhouse v3 offices record. |
| `location` | `string` | Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices. |
| `name` | `string` | Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization. |
| `parent_id` | `integer` | Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization. |
| `primary_in_house_contact_user_id` | `integer` | Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 offices record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 offices record. |
| `data[].external_id` | `string` | Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled. |
| `data[].id` | `integer` | Id from the Greenhouse v3 offices record. |
| `data[].location` | `string` | Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices. |
| `data[].name` | `string` | Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization. |
| `data[].parent_id` | `integer` | Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization. |
| `data[].primary_in_house_contact_user_id` | `integer` | Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 offices record. |

</details>

## Sources

### Sources List

Returns a cursor-paginated list of sources.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "sources",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.sources.list()
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `type` | `null \| object` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Sources Context Store Search

Search and filter sources records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "sources",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "created_at": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.sources.context_store_search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sources",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"created_at": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | Created at from the Greenhouse v3 sources record. |
| `id` | `integer` | Id from the Greenhouse v3 sources record. |
| `name` | `string` | Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name. |
| `type` | `object` | The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 sources record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 sources record. |
| `data[].id` | `integer` | Id from the Greenhouse v3 sources record. |
| `data[].name` | `string` | Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name. |
| `data[].type` | `object` | The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 sources record. |

</details>

## Users

### Users List

Returns a cursor-paginated list of users.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "users",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.users.list()
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
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |
| `show_service_accounts` | `boolean` | No | Include Greenhouse service accounts. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `agency_id` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `deactivated` | `null \| boolean` |  |
| `department_ids` | `null \| array` |  |
| `emails` | `null \| array` |  |
| `employee_id` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `id` | `null \| integer` |  |
| `interviewer_tags` | `null \| array` |  |
| `job_title` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `linked_candidate_ids` | `null \| array` |  |
| `name` | `null \| string` |  |
| `office_ids` | `null \| array` |  |
| `primary_email` | `null \| string` |  |
| `site_admin` | `null \| boolean` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "users",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "agency_id": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await greenhouse.users.context_store_search(
    query={"filter": {"eq": {"agency_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"agency_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `agency_id` | `integer` | Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users. |
| `created_at` | `string` | Created at from the Greenhouse v3 users record. |
| `custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `deactivated` | `boolean` | Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/\{id\}/deactivate` and `POST /v3/users/\{id\}/activate`. |
| `department_ids` | `array` | Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department. |
| `emails` | `array` | All email addresses on the user's account, including the primary address and any additional verified addresses. |
| `employee_id` | `string` | Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set. |
| `first_name` | `string` | First name from the Greenhouse v3 users record. |
| `id` | `integer` | Id from the Greenhouse v3 users record. |
| `interviewer_tags` | `array` | Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`. |
| `job_title` | `string` | Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title. |
| `last_name` | `string` | Last name from the Greenhouse v3 users record. |
| `linked_candidate_ids` | `array` | Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications). |
| `name` | `string` | Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly. |
| `office_ids` | `array` | Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office. |
| `primary_email` | `string` | Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string. |
| `site_admin` | `boolean` | Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/\{id\}/revoke_permissions`. |
| `updated_at` | `string` | Updated at from the Greenhouse v3 users record. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].agency_id` | `integer` | Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users. |
| `data[].created_at` | `string` | Created at from the Greenhouse v3 users record. |
| `data[].custom_fields` | `object` | Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`. |
| `data[].deactivated` | `boolean` | Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/\{id\}/deactivate` and `POST /v3/users/\{id\}/activate`. |
| `data[].department_ids` | `array` | Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department. |
| `data[].emails` | `array` | All email addresses on the user's account, including the primary address and any additional verified addresses. |
| `data[].employee_id` | `string` | Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set. |
| `data[].first_name` | `string` | First name from the Greenhouse v3 users record. |
| `data[].id` | `integer` | Id from the Greenhouse v3 users record. |
| `data[].interviewer_tags` | `array` | Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`. |
| `data[].job_title` | `string` | Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title. |
| `data[].last_name` | `string` | Last name from the Greenhouse v3 users record. |
| `data[].linked_candidate_ids` | `array` | Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications). |
| `data[].name` | `string` | Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly. |
| `data[].office_ids` | `array` | Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office. |
| `data[].primary_email` | `string` | Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string. |
| `data[].site_admin` | `boolean` | Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/\{id\}/revoke_permissions`. |
| `data[].updated_at` | `string` | Updated at from the Greenhouse v3 users record. |

</details>

## Attachments

### Attachments List

Returns a cursor-paginated list of attachments.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "attachments",
  "action": "list"
}'
```

#### Python SDK

```python
await greenhouse.attachments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor from the previous response Link header. Do not combine with any other parameter. |
| `per_page` | `integer` | No | Number of records to return on the first page. |
| `ids` | `array<integer>` | No | Return only records with these IDs (maximum 50). |
| `updated_at` | `string` | No | Filter by updated timestamp using the Harvest v3 pipe expression, such as gte|2026-01-01T00:00:00Z. |
| `application_ids` | `array<integer>` | No | Return attachments associated with these application IDs (maximum 50). |
| `candidate_ids` | `array<integer>` | No | Return attachments belonging to these candidate IDs (maximum 50). |
| `type` | `"resume" \| "cover_letter" \| "take_home_test" \| "offer_packet" \| "offer_letter" \| "signed_offer_letter" \| "other" \| "form_attachment" \| "midfunnel_agreement" \| "automated_agreement"` | No | Filter by attachment type. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `application_id` | `integer` |  |
| `candidate_id` | `integer \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `filename` | `string` |  |
| `url` | `string` |  |
| `type` | `"resume" \| "cover_letter" \| "take_home_test" \| "offer_packet" \| "offer_letter" \| "signed_offer_letter" \| "other" \| "form_attachment" \| "midfunnel_agreement" \| "automated_agreement"` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Attachments Download

Looks up an attachment by ID and follows its current time-limited download URL.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "greenhouse",
  "entity": "attachments",
  "action": "download",
  "params": {
    "ids": []
  }
}'
```

#### Python SDK

```python
async for chunk in greenhouse.attachments.download(    ids=[]):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "download",
    "params": {
        "ids": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ids` | `array<integer>` | Yes | The single attachment ID to download. |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


