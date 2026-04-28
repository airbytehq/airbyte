# Pylon full reference

This is the full reference documentation for the Pylon agent connector.

## Supported entities and actions

The Pylon connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Issues | [List](#issues-list), [Create](#issues-create), [Get](#issues-get), [Update](#issues-update), [Delete](#issues-delete), [Context Store Search](#issues-context-store-search) |
| Issue Replies | [Create](#issue-replies-create) |
| Issue Assignments | [Update](#issue-assignments-update) |
| Issue Statuses | [Update](#issue-statuses-update) |
| Messages | [List](#messages-list), [Context Store Search](#messages-context-store-search) |
| Issue Notes | [Create](#issue-notes-create) |
| Issue Threads | [Create](#issue-threads-create) |
| Accounts | [List](#accounts-list), [Create](#accounts-create), [Get](#accounts-get), [Update](#accounts-update), [Context Store Search](#accounts-context-store-search) |
| Contacts | [List](#contacts-list), [Create](#contacts-create), [Get](#contacts-get), [Update](#contacts-update), [Context Store Search](#contacts-context-store-search) |
| Teams | [List](#teams-list), [Create](#teams-create), [Get](#teams-get), [Update](#teams-update), [Context Store Search](#teams-context-store-search) |
| Tags | [List](#tags-list), [Create](#tags-create), [Get](#tags-get), [Update](#tags-update), [Context Store Search](#tags-context-store-search) |
| Users | [List](#users-list), [Get](#users-get), [Context Store Search](#users-context-store-search) |
| Custom Fields | [List](#custom-fields-list), [Get](#custom-fields-get), [Context Store Search](#custom-fields-context-store-search) |
| Ticket Forms | [List](#ticket-forms-list), [Context Store Search](#ticket-forms-context-store-search) |
| User Roles | [List](#user-roles-list), [Context Store Search](#user-roles-context-store-search) |
| Tasks | [Create](#tasks-create), [Update](#tasks-update) |
| Projects | [Create](#projects-create), [Update](#projects-update) |
| Milestones | [Create](#milestones-create), [Update](#milestones-update) |
| Articles | [Create](#articles-create), [Update](#articles-update) |
| Collections | [Create](#collections-create) |
| Me | [Get](#me-get) |

## Issues

### Issues List

Get a list of issues within a time range

#### Python SDK

```python
await pylon.issues.list(
    start_time="2025-01-01T00:00:00Z",
    end_time="2025-01-01T00:00:00Z"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list",
    "params": {
        "start_time": "2025-01-01T00:00:00Z",
        "end_time": "2025-01-01T00:00:00Z"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_time` | `string` | Yes | The start time (RFC3339) of the time range to get issues for. |
| `end_time` | `string` | Yes | The end time (RFC3339) of the time range to get issues for. |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `account` | `object \| any` |  |
| `assignee` | `object \| any` |  |
| `attachment_urls` | `array \| null` |  |
| `author_unverified` | `boolean \| null` |  |
| `body_html` | `string \| null` |  |
| `business_hours_first_response_seconds` | `integer \| null` |  |
| `business_hours_resolution_seconds` | `integer \| null` |  |
| `business_hours_time_in_status_seconds` | `object \| null` |  |
| `chat_widget_info` | `object \| any` |  |
| `created_at` | `string \| null` |  |
| `csat_responses` | `array \| null` |  |
| `csat_responses[].comment` | `string \| null` |  |
| `csat_responses[].score` | `integer \| null` |  |
| `custom_fields` | `object \| null` |  |
| `customer_portal_visible` | `boolean \| null` |  |
| `external_issues` | `array \| null` |  |
| `external_issues[].external_id` | `string \| null` |  |
| `external_issues[].link` | `string \| null` |  |
| `external_issues[].source` | `string \| null` |  |
| `first_response_seconds` | `integer \| null` |  |
| `first_response_time` | `string \| null` |  |
| `latest_message_time` | `string \| null` |  |
| `link` | `string \| null` |  |
| `number` | `integer \| null` |  |
| `number_of_touches` | `integer \| null` |  |
| `requester` | `object \| any` |  |
| `resolution_seconds` | `integer \| null` |  |
| `resolution_time` | `string \| null` |  |
| `slack` | `object \| any` |  |
| `snoozed_until_time` | `string \| null` |  |
| `source` | `"slack" \| "microsoft_teams" \| "microsoft_teams_chat" \| "chat_widget" \| "email" \| "manual" \| "form" \| "discord" \| "whatsapp" \| "sms" \| "telegram" \| any` |  |
| `state` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `team` | `object \| any` |  |
| `title` | `string \| null` |  |
| `time_in_status_seconds` | `object \| null` |  |
| `type` | `"conversation" \| "ticket" \| any` |  |
| `updated_at` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Issues Create

Create a new issue

#### Python SDK

```python
await pylon.issues.create(
    title="<str>",
    body_html="<str>",
    priority="<str>",
    requester_email="<str>",
    requester_name="<str>",
    account_id="<str>",
    assignee_id="<str>",
    team_id="<str>",
    tags=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "create",
    "params": {
        "title": "<str>",
        "body_html": "<str>",
        "priority": "<str>",
        "requester_email": "<str>",
        "requester_name": "<str>",
        "account_id": "<str>",
        "assignee_id": "<str>",
        "team_id": "<str>",
        "tags": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | Yes | The title of the issue |
| `body_html` | `string` | Yes | The HTML content of the body of the issue |
| `priority` | `string` | No | The priority of the issue (urgent, high, medium, low) |
| `requester_email` | `string` | No | The email of the requester |
| `requester_name` | `string` | No | The full name of the requester |
| `account_id` | `string` | No | The account that this issue belongs to |
| `assignee_id` | `string` | No | The user the issue should be assigned to |
| `team_id` | `string` | No | The ID of the team this issue should be assigned to |
| `tags` | `array<string>` | No | Tags to associate with the issue |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.account` | `object \| any` |  |
| `data.assignee` | `object \| any` |  |
| `data.attachment_urls` | `array \| null` |  |
| `data.author_unverified` | `boolean \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.business_hours_first_response_seconds` | `integer \| null` |  |
| `data.business_hours_resolution_seconds` | `integer \| null` |  |
| `data.business_hours_time_in_status_seconds` | `object \| null` |  |
| `data.chat_widget_info` | `object \| any` |  |
| `data.created_at` | `string \| null` |  |
| `data.csat_responses` | `array \| null` |  |
| `data.csat_responses[].comment` | `string \| null` |  |
| `data.csat_responses[].score` | `integer \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.customer_portal_visible` | `boolean \| null` |  |
| `data.external_issues` | `array \| null` |  |
| `data.external_issues[].external_id` | `string \| null` |  |
| `data.external_issues[].link` | `string \| null` |  |
| `data.external_issues[].source` | `string \| null` |  |
| `data.first_response_seconds` | `integer \| null` |  |
| `data.first_response_time` | `string \| null` |  |
| `data.latest_message_time` | `string \| null` |  |
| `data.link` | `string \| null` |  |
| `data.number` | `integer \| null` |  |
| `data.number_of_touches` | `integer \| null` |  |
| `data.requester` | `object \| any` |  |
| `data.resolution_seconds` | `integer \| null` |  |
| `data.resolution_time` | `string \| null` |  |
| `data.slack` | `object \| any` |  |
| `data.snoozed_until_time` | `string \| null` |  |
| `data.source` | `"slack" \| "microsoft_teams" \| "microsoft_teams_chat" \| "chat_widget" \| "email" \| "manual" \| "form" \| "discord" \| "whatsapp" \| "sms" \| "telegram" \| any` |  |
| `data.state` | `string \| null` |  |
| `data.tags` | `array \| null` |  |
| `data.team` | `object \| any` |  |
| `data.title` | `string \| null` |  |
| `data.time_in_status_seconds` | `object \| null` |  |
| `data.type` | `"conversation" \| "ticket" \| any` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Issues Get

Get a single issue by ID

#### Python SDK

```python
await pylon.issues.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `id` | `string` | Yes | The ID of the issue |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `account` | `object \| any` |  |
| `assignee` | `object \| any` |  |
| `attachment_urls` | `array \| null` |  |
| `author_unverified` | `boolean \| null` |  |
| `body_html` | `string \| null` |  |
| `business_hours_first_response_seconds` | `integer \| null` |  |
| `business_hours_resolution_seconds` | `integer \| null` |  |
| `business_hours_time_in_status_seconds` | `object \| null` |  |
| `chat_widget_info` | `object \| any` |  |
| `created_at` | `string \| null` |  |
| `csat_responses` | `array \| null` |  |
| `csat_responses[].comment` | `string \| null` |  |
| `csat_responses[].score` | `integer \| null` |  |
| `custom_fields` | `object \| null` |  |
| `customer_portal_visible` | `boolean \| null` |  |
| `external_issues` | `array \| null` |  |
| `external_issues[].external_id` | `string \| null` |  |
| `external_issues[].link` | `string \| null` |  |
| `external_issues[].source` | `string \| null` |  |
| `first_response_seconds` | `integer \| null` |  |
| `first_response_time` | `string \| null` |  |
| `latest_message_time` | `string \| null` |  |
| `link` | `string \| null` |  |
| `number` | `integer \| null` |  |
| `number_of_touches` | `integer \| null` |  |
| `requester` | `object \| any` |  |
| `resolution_seconds` | `integer \| null` |  |
| `resolution_time` | `string \| null` |  |
| `slack` | `object \| any` |  |
| `snoozed_until_time` | `string \| null` |  |
| `source` | `"slack" \| "microsoft_teams" \| "microsoft_teams_chat" \| "chat_widget" \| "email" \| "manual" \| "form" \| "discord" \| "whatsapp" \| "sms" \| "telegram" \| any` |  |
| `state` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `team` | `object \| any` |  |
| `title` | `string \| null` |  |
| `time_in_status_seconds` | `object \| null` |  |
| `type` | `"conversation" \| "ticket" \| any` |  |
| `updated_at` | `string \| null` |  |


</details>

### Issues Update

Update an existing issue by ID

#### Python SDK

```python
await pylon.issues.update(
    state="<str>",
    assignee_id="<str>",
    team_id="<str>",
    account_id="<str>",
    tags=[],
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "update",
    "params": {
        "state": "<str>",
        "assignee_id": "<str>",
        "team_id": "<str>",
        "account_id": "<str>",
        "tags": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `state` | `string` | No | The state of the issue (open, snoozed, closed) |
| `assignee_id` | `string` | No | The user the issue should be assigned to |
| `team_id` | `string` | No | The ID of the team this issue should be assigned to |
| `account_id` | `string` | No | The account that this issue belongs to |
| `tags` | `array<string>` | No | Tags to associate with the issue |
| `id` | `string` | Yes | The ID of the issue to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.account` | `object \| any` |  |
| `data.assignee` | `object \| any` |  |
| `data.attachment_urls` | `array \| null` |  |
| `data.author_unverified` | `boolean \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.business_hours_first_response_seconds` | `integer \| null` |  |
| `data.business_hours_resolution_seconds` | `integer \| null` |  |
| `data.business_hours_time_in_status_seconds` | `object \| null` |  |
| `data.chat_widget_info` | `object \| any` |  |
| `data.created_at` | `string \| null` |  |
| `data.csat_responses` | `array \| null` |  |
| `data.csat_responses[].comment` | `string \| null` |  |
| `data.csat_responses[].score` | `integer \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.customer_portal_visible` | `boolean \| null` |  |
| `data.external_issues` | `array \| null` |  |
| `data.external_issues[].external_id` | `string \| null` |  |
| `data.external_issues[].link` | `string \| null` |  |
| `data.external_issues[].source` | `string \| null` |  |
| `data.first_response_seconds` | `integer \| null` |  |
| `data.first_response_time` | `string \| null` |  |
| `data.latest_message_time` | `string \| null` |  |
| `data.link` | `string \| null` |  |
| `data.number` | `integer \| null` |  |
| `data.number_of_touches` | `integer \| null` |  |
| `data.requester` | `object \| any` |  |
| `data.resolution_seconds` | `integer \| null` |  |
| `data.resolution_time` | `string \| null` |  |
| `data.slack` | `object \| any` |  |
| `data.snoozed_until_time` | `string \| null` |  |
| `data.source` | `"slack" \| "microsoft_teams" \| "microsoft_teams_chat" \| "chat_widget" \| "email" \| "manual" \| "form" \| "discord" \| "whatsapp" \| "sms" \| "telegram" \| any` |  |
| `data.state` | `string \| null` |  |
| `data.tags` | `array \| null` |  |
| `data.team` | `object \| any` |  |
| `data.title` | `string \| null` |  |
| `data.time_in_status_seconds` | `object \| null` |  |
| `data.type` | `"conversation" \| "ticket" \| any` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Issues Delete

Permanently deletes an issue by ID. This action cannot be undone.

#### Python SDK

```python
await pylon.issues.delete(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "delete",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the issue to delete |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `request_id` | `string` |  |


</details>

### Issues Context Store Search

Search and filter issues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.issues.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the issue |
| `title` | `string` | Title of the issue |
| `state` | `string` | Current state of the issue (e.g. new, in_progress, closed) |
| `source` | `string` | Channel the issue originated from (e.g. email, slack) |
| `type` | `string` | Type classification of the issue |
| `number` | `integer` | Human-readable issue number within the workspace |
| `created_at` | `string` | Timestamp when the issue was created, in ISO 8601 format |
| `latest_message_time` | `string` | Timestamp of the most recent message on the issue, in ISO 8601 format |
| `resolution_time` | `string` | Timestamp when the issue was resolved, in ISO 8601 format |
| `snoozed_until_time` | `string` | Timestamp the issue is snoozed until, in ISO 8601 format |
| `customer_portal_visible` | `boolean` | Whether the issue is visible in the customer portal |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the issue |
| `data[].title` | `string` | Title of the issue |
| `data[].state` | `string` | Current state of the issue (e.g. new, in_progress, closed) |
| `data[].source` | `string` | Channel the issue originated from (e.g. email, slack) |
| `data[].type` | `string` | Type classification of the issue |
| `data[].number` | `integer` | Human-readable issue number within the workspace |
| `data[].created_at` | `string` | Timestamp when the issue was created, in ISO 8601 format |
| `data[].latest_message_time` | `string` | Timestamp of the most recent message on the issue, in ISO 8601 format |
| `data[].resolution_time` | `string` | Timestamp when the issue was resolved, in ISO 8601 format |
| `data[].snoozed_until_time` | `string` | Timestamp the issue is snoozed until, in ISO 8601 format |
| `data[].customer_portal_visible` | `boolean` | Whether the issue is visible in the customer portal |

</details>

## Issue Replies

### Issue Replies Create

Sends a customer-facing reply on an issue, visible to the requester.

#### Python SDK

```python
await pylon.issue_replies.create(
    body_html="<str>",
    message_id="<str>",
    user_id="<str>",
    contact_id="<str>",
    attachment_urls=[],
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_replies",
    "action": "create",
    "params": {
        "body_html": "<str>",
        "message_id": "<str>",
        "user_id": "<str>",
        "contact_id": "<str>",
        "attachment_urls": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `body_html` | `string` | Yes | The body of the reply message in HTML |
| `message_id` | `string` | Yes | The ID of the message to reply to |
| `user_id` | `string` | No | Optional user ID to post the message as. Only one of user_id or contact_id can be provided. |
| `contact_id` | `string` | No | Optional contact ID to post the message as. Only one of user_id or contact_id can be provided. |
| `attachment_urls` | `array<string>` | No | An array of attachment URLs to attach to this reply |
| `id` | `string` | Yes | The ID of the issue to reply to |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.issue_id` | `string` |  |
| `request_id` | `string` |  |


</details>

## Issue Assignments

### Issue Assignments Update

Assign an issue to a user or team, or remove the current assignment.

#### Python SDK

```python
await pylon.issue_assignments.update(
    assignee_id="<str>",
    team_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_assignments",
    "action": "update",
    "params": {
        "assignee_id": "<str>",
        "team_id": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `assignee_id` | `string` | No | The ID of the user to assign the issue to. Pass an empty string to unassign. |
| `team_id` | `string` | No | The ID of the team to assign the issue to. Pass an empty string to remove team assignment. |
| `id` | `string` | Yes | The ID of the issue to assign |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.account` | `object \| any` |  |
| `data.assignee` | `object \| any` |  |
| `data.attachment_urls` | `array \| null` |  |
| `data.author_unverified` | `boolean \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.business_hours_first_response_seconds` | `integer \| null` |  |
| `data.business_hours_resolution_seconds` | `integer \| null` |  |
| `data.business_hours_time_in_status_seconds` | `object \| null` |  |
| `data.chat_widget_info` | `object \| any` |  |
| `data.created_at` | `string \| null` |  |
| `data.csat_responses` | `array \| null` |  |
| `data.csat_responses[].comment` | `string \| null` |  |
| `data.csat_responses[].score` | `integer \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.customer_portal_visible` | `boolean \| null` |  |
| `data.external_issues` | `array \| null` |  |
| `data.external_issues[].external_id` | `string \| null` |  |
| `data.external_issues[].link` | `string \| null` |  |
| `data.external_issues[].source` | `string \| null` |  |
| `data.first_response_seconds` | `integer \| null` |  |
| `data.first_response_time` | `string \| null` |  |
| `data.latest_message_time` | `string \| null` |  |
| `data.link` | `string \| null` |  |
| `data.number` | `integer \| null` |  |
| `data.number_of_touches` | `integer \| null` |  |
| `data.requester` | `object \| any` |  |
| `data.resolution_seconds` | `integer \| null` |  |
| `data.resolution_time` | `string \| null` |  |
| `data.slack` | `object \| any` |  |
| `data.snoozed_until_time` | `string \| null` |  |
| `data.source` | `"slack" \| "microsoft_teams" \| "microsoft_teams_chat" \| "chat_widget" \| "email" \| "manual" \| "form" \| "discord" \| "whatsapp" \| "sms" \| "telegram" \| any` |  |
| `data.state` | `string \| null` |  |
| `data.tags` | `array \| null` |  |
| `data.team` | `object \| any` |  |
| `data.title` | `string \| null` |  |
| `data.time_in_status_seconds` | `object \| null` |  |
| `data.type` | `"conversation" \| "ticket" \| any` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Issue Statuses

### Issue Statuses Update

Transition an issue to a new status (new, waiting_on_you, waiting_on_customer, on_hold, closed, or a custom status slug).

#### Python SDK

```python
await pylon.issue_statuses.update(
    state="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_statuses",
    "action": "update",
    "params": {
        "state": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `state` | `string` | Yes | The target state for the issue (new, waiting_on_you, waiting_on_customer, on_hold, closed, or a custom status slug) |
| `id` | `string` | Yes | The ID of the issue to update status for |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.account` | `object \| any` |  |
| `data.assignee` | `object \| any` |  |
| `data.attachment_urls` | `array \| null` |  |
| `data.author_unverified` | `boolean \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.business_hours_first_response_seconds` | `integer \| null` |  |
| `data.business_hours_resolution_seconds` | `integer \| null` |  |
| `data.business_hours_time_in_status_seconds` | `object \| null` |  |
| `data.chat_widget_info` | `object \| any` |  |
| `data.created_at` | `string \| null` |  |
| `data.csat_responses` | `array \| null` |  |
| `data.csat_responses[].comment` | `string \| null` |  |
| `data.csat_responses[].score` | `integer \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.customer_portal_visible` | `boolean \| null` |  |
| `data.external_issues` | `array \| null` |  |
| `data.external_issues[].external_id` | `string \| null` |  |
| `data.external_issues[].link` | `string \| null` |  |
| `data.external_issues[].source` | `string \| null` |  |
| `data.first_response_seconds` | `integer \| null` |  |
| `data.first_response_time` | `string \| null` |  |
| `data.latest_message_time` | `string \| null` |  |
| `data.link` | `string \| null` |  |
| `data.number` | `integer \| null` |  |
| `data.number_of_touches` | `integer \| null` |  |
| `data.requester` | `object \| any` |  |
| `data.resolution_seconds` | `integer \| null` |  |
| `data.resolution_time` | `string \| null` |  |
| `data.slack` | `object \| any` |  |
| `data.snoozed_until_time` | `string \| null` |  |
| `data.source` | `"slack" \| "microsoft_teams" \| "microsoft_teams_chat" \| "chat_widget" \| "email" \| "manual" \| "form" \| "discord" \| "whatsapp" \| "sms" \| "telegram" \| any` |  |
| `data.state` | `string \| null` |  |
| `data.tags` | `array \| null` |  |
| `data.team` | `object \| any` |  |
| `data.title` | `string \| null` |  |
| `data.time_in_status_seconds` | `object \| null` |  |
| `data.type` | `"conversation" \| "ticket" \| any` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Messages

### Messages List

Returns all messages on an issue (customer-facing replies and internal notes)

#### Python SDK

```python
await pylon.messages.list(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "list",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the issue to fetch messages for |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `author` | `object \| any` |  |
| `email_info` | `object \| any` |  |
| `file_urls` | `array \| null` |  |
| `is_private` | `boolean \| null` |  |
| `message_html` | `string \| null` |  |
| `source` | `string \| null` |  |
| `thread_id` | `string \| null` |  |
| `timestamp` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Messages Context Store Search

Search and filter messages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.messages.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the message |
| `timestamp` | `string` | Timestamp the message was posted, in ISO 8601 format |
| `is_private` | `boolean` | Whether the message is an internal note (not visible to the customer) |
| `source` | `string` | Channel the message was sent through (e.g. email, slack) |
| `thread_id` | `string` | Identifier of the thread this message belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the message |
| `data[].timestamp` | `string` | Timestamp the message was posted, in ISO 8601 format |
| `data[].is_private` | `boolean` | Whether the message is an internal note (not visible to the customer) |
| `data[].source` | `string` | Channel the message was sent through (e.g. email, slack) |
| `data[].thread_id` | `string` | Identifier of the thread this message belongs to |

</details>

## Issue Notes

### Issue Notes Create

Create an internal note on an issue

#### Python SDK

```python
await pylon.issue_notes.create(
    body_html="<str>",
    thread_id="<str>",
    message_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_notes",
    "action": "create",
    "params": {
        "body_html": "<str>",
        "thread_id": "<str>",
        "message_id": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `body_html` | `string` | Yes | The HTML content of the note |
| `thread_id` | `string` | No | The ID of the thread to add the note to |
| `message_id` | `string` | No | The ID of the message to add the note to |
| `id` | `string` | Yes | The ID of the issue to add a note to |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.body_html` | `string \| null` |  |
| `data.timestamp` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Issue Threads

### Issue Threads Create

Create a new thread on an issue

#### Python SDK

```python
await pylon.issue_threads.create(
    name="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issue_threads",
    "action": "create",
    "params": {
        "name": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the thread |
| `id` | `string` | Yes | The ID of the issue to create a thread on |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Accounts

### Accounts List

Get a list of accounts

#### Python SDK

```python
await pylon.accounts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `channels` | `array \| null` |  |
| `channels[].channel_id` | `string \| null` |  |
| `channels[].source` | `string \| null` |  |
| `channels[].is_primary` | `boolean \| null` |  |
| `created_at` | `string \| null` |  |
| `custom_fields` | `object \| null` |  |
| `domain` | `string \| null` |  |
| `domains` | `array \| null` |  |
| `external_ids` | `object \| null` |  |
| `is_disabled` | `boolean \| null` |  |
| `latest_customer_activity_time` | `string \| null` |  |
| `name` | `string \| null` |  |
| `owner` | `object \| any` |  |
| `primary_domain` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `type` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Accounts Create

Create a new account

#### Python SDK

```python
await pylon.accounts.create(
    name="<str>",
    domains=[],
    primary_domain="<str>",
    owner_id="<str>",
    logo_url="<str>",
    tags=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "create",
    "params": {
        "name": "<str>",
        "domains": [],
        "primary_domain": "<str>",
        "owner_id": "<str>",
        "logo_url": "<str>",
        "tags": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | The name of the account |
| `domains` | `array<string>` | No | The domains of the account (e.g. stripe.com) |
| `primary_domain` | `string` | No | Must be in the list of domains. If there are any domains, there must be exactly one primary domain. |
| `owner_id` | `string` | No | The ID of the owner of the account |
| `logo_url` | `string` | No | The logo URL of the account. Must be a square .png, .jpg or .jpeg. |
| `tags` | `array<string>` | No | Tags to associate with the account |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.channels` | `array \| null` |  |
| `data.channels[].channel_id` | `string \| null` |  |
| `data.channels[].source` | `string \| null` |  |
| `data.channels[].is_primary` | `boolean \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.domain` | `string \| null` |  |
| `data.domains` | `array \| null` |  |
| `data.external_ids` | `object \| null` |  |
| `data.is_disabled` | `boolean \| null` |  |
| `data.latest_customer_activity_time` | `string \| null` |  |
| `data.name` | `string \| null` |  |
| `data.owner` | `object \| any` |  |
| `data.primary_domain` | `string \| null` |  |
| `data.tags` | `array \| null` |  |
| `data.type` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Accounts Get

Get a single account by ID

#### Python SDK

```python
await pylon.accounts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the account |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `channels` | `array \| null` |  |
| `channels[].channel_id` | `string \| null` |  |
| `channels[].source` | `string \| null` |  |
| `channels[].is_primary` | `boolean \| null` |  |
| `created_at` | `string \| null` |  |
| `custom_fields` | `object \| null` |  |
| `domain` | `string \| null` |  |
| `domains` | `array \| null` |  |
| `external_ids` | `object \| null` |  |
| `is_disabled` | `boolean \| null` |  |
| `latest_customer_activity_time` | `string \| null` |  |
| `name` | `string \| null` |  |
| `owner` | `object \| any` |  |
| `primary_domain` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `type` | `string \| null` |  |


</details>

### Accounts Update

Update an existing account by ID

#### Python SDK

```python
await pylon.accounts.update(
    name="<str>",
    domains=[],
    primary_domain="<str>",
    owner_id="<str>",
    logo_url="<str>",
    is_disabled=True,
    tags=[],
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "update",
    "params": {
        "name": "<str>",
        "domains": [],
        "primary_domain": "<str>",
        "owner_id": "<str>",
        "logo_url": "<str>",
        "is_disabled": True,
        "tags": [],
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the account |
| `domains` | `array<string>` | No | Domains of the account. Must specify one domain as primary. |
| `primary_domain` | `string` | No | Must be in the list of domains. If there are any domains, there must be exactly one primary domain. |
| `owner_id` | `string` | No | The ID of the owner of the account. If empty string is passed in, the owner will be removed. |
| `logo_url` | `string` | No | Logo URL of the account |
| `is_disabled` | `boolean` | No | Whether the account is disabled |
| `tags` | `array<string>` | No | Tags to associate with the account |
| `id` | `string` | Yes | The ID of the account to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.channels` | `array \| null` |  |
| `data.channels[].channel_id` | `string \| null` |  |
| `data.channels[].source` | `string \| null` |  |
| `data.channels[].is_primary` | `boolean \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.domain` | `string \| null` |  |
| `data.domains` | `array \| null` |  |
| `data.external_ids` | `object \| null` |  |
| `data.is_disabled` | `boolean \| null` |  |
| `data.latest_customer_activity_time` | `string \| null` |  |
| `data.name` | `string \| null` |  |
| `data.owner` | `object \| any` |  |
| `data.primary_domain` | `string \| null` |  |
| `data.tags` | `array \| null` |  |
| `data.type` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Accounts Context Store Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.accounts.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the account |
| `name` | `string` | Name of the account (customer organization) |
| `domain` | `string` | Primary domain associated with the account |
| `primary_domain` | `string` | Canonical primary domain for the account |
| `type` | `string` | Classification of the account (e.g. customer, prospect) |
| `is_disabled` | `boolean` | Whether the account has been disabled |
| `created_at` | `string` | Timestamp when the account was created, in ISO 8601 format |
| `latest_customer_activity_time` | `string` | Timestamp of the most recent activity from this account, in ISO 8601 format |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the account |
| `data[].name` | `string` | Name of the account (customer organization) |
| `data[].domain` | `string` | Primary domain associated with the account |
| `data[].primary_domain` | `string` | Canonical primary domain for the account |
| `data[].type` | `string` | Classification of the account (e.g. customer, prospect) |
| `data[].is_disabled` | `boolean` | Whether the account has been disabled |
| `data[].created_at` | `string` | Timestamp when the account was created, in ISO 8601 format |
| `data[].latest_customer_activity_time` | `string` | Timestamp of the most recent activity from this account, in ISO 8601 format |

</details>

## Contacts

### Contacts List

Get a list of contacts

#### Python SDK

```python
await pylon.contacts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `account` | `object \| any` |  |
| `avatar_url` | `string \| null` |  |
| `custom_fields` | `object \| null` |  |
| `email` | `string \| null` |  |
| `emails` | `array \| null` |  |
| `integration_user_ids` | `array \| null` |  |
| `integration_user_ids[].id` | `string \| null` |  |
| `integration_user_ids[].source` | `string \| null` |  |
| `name` | `string \| null` |  |
| `phone_numbers` | `array \| null` |  |
| `portal_role` | `string \| null` |  |
| `portal_role_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Contacts Create

Create a new contact

#### Python SDK

```python
await pylon.contacts.create(
    name="<str>",
    email="<str>",
    account_id="<str>",
    avatar_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "create",
    "params": {
        "name": "<str>",
        "email": "<str>",
        "account_id": "<str>",
        "avatar_url": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | The name of the contact |
| `email` | `string` | No | The email address of the contact |
| `account_id` | `string` | No | The ID of the account to associate this contact with |
| `avatar_url` | `string` | No | The URL of the contact's avatar |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.account` | `object \| any` |  |
| `data.avatar_url` | `string \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.email` | `string \| null` |  |
| `data.emails` | `array \| null` |  |
| `data.integration_user_ids` | `array \| null` |  |
| `data.integration_user_ids[].id` | `string \| null` |  |
| `data.integration_user_ids[].source` | `string \| null` |  |
| `data.name` | `string \| null` |  |
| `data.phone_numbers` | `array \| null` |  |
| `data.portal_role` | `string \| null` |  |
| `data.portal_role_id` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Contacts Get

Get a single contact by ID

#### Python SDK

```python
await pylon.contacts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the contact |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `account` | `object \| any` |  |
| `avatar_url` | `string \| null` |  |
| `custom_fields` | `object \| null` |  |
| `email` | `string \| null` |  |
| `emails` | `array \| null` |  |
| `integration_user_ids` | `array \| null` |  |
| `integration_user_ids[].id` | `string \| null` |  |
| `integration_user_ids[].source` | `string \| null` |  |
| `name` | `string \| null` |  |
| `phone_numbers` | `array \| null` |  |
| `portal_role` | `string \| null` |  |
| `portal_role_id` | `string \| null` |  |


</details>

### Contacts Update

Update an existing contact by ID

#### Python SDK

```python
await pylon.contacts.update(
    name="<str>",
    email="<str>",
    account_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "update",
    "params": {
        "name": "<str>",
        "email": "<str>",
        "account_id": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the contact |
| `email` | `string` | No | The email address of the contact |
| `account_id` | `string` | No | The ID of the account to associate this contact with |
| `id` | `string` | Yes | The ID of the contact to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.account` | `object \| any` |  |
| `data.avatar_url` | `string \| null` |  |
| `data.custom_fields` | `object \| null` |  |
| `data.email` | `string \| null` |  |
| `data.emails` | `array \| null` |  |
| `data.integration_user_ids` | `array \| null` |  |
| `data.integration_user_ids[].id` | `string \| null` |  |
| `data.integration_user_ids[].source` | `string \| null` |  |
| `data.name` | `string \| null` |  |
| `data.phone_numbers` | `array \| null` |  |
| `data.portal_role` | `string \| null` |  |
| `data.portal_role_id` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Contacts Context Store Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.contacts.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the contact |
| `name` | `string` | Full name of the contact |
| `email` | `string` | Primary email address of the contact |
| `primary_phone_number` | `string` | Primary phone number of the contact |
| `portal_role` | `string` | Role the contact has in the customer portal |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the contact |
| `data[].name` | `string` | Full name of the contact |
| `data[].email` | `string` | Primary email address of the contact |
| `data[].primary_phone_number` | `string` | Primary phone number of the contact |
| `data[].portal_role` | `string` | Role the contact has in the customer portal |

</details>

## Teams

### Teams List

Get a list of teams

#### Python SDK

```python
await pylon.teams.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `users` | `array \| null` |  |
| `users[].email` | `string \| null` |  |
| `users[].id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Teams Create

Create a new team

#### Python SDK

```python
await pylon.teams.create(
    name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "create",
    "params": {
        "name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the team |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `data.users` | `array \| null` |  |
| `data.users[].email` | `string \| null` |  |
| `data.users[].id` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Teams Get

Get a single team by ID

#### Python SDK

```python
await pylon.teams.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `id` | `string` | Yes | The ID of the team |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `users` | `array \| null` |  |
| `users[].email` | `string \| null` |  |
| `users[].id` | `string \| null` |  |


</details>

### Teams Update

Update an existing team by ID

#### Python SDK

```python
await pylon.teams.update(
    name="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "update",
    "params": {
        "name": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the team |
| `id` | `string` | Yes | The ID of the team to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `data.users` | `array \| null` |  |
| `data.users[].email` | `string \| null` |  |
| `data.users[].id` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Teams Context Store Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.teams.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the team |
| `name` | `string` | Name of the team |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the team |
| `data[].name` | `string` | Name of the team |

</details>

## Tags

### Tags List

Get all tags

#### Python SDK

```python
await pylon.tags.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `hex_color` | `string \| null` |  |
| `object_type` | `string \| null` |  |
| `value` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Tags Create

Create a new tag

#### Python SDK

```python
await pylon.tags.create(
    value="<str>",
    object_type="<str>",
    hex_color="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "create",
    "params": {
        "value": "<str>",
        "object_type": "<str>",
        "hex_color": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `value` | `string` | Yes | The tag value |
| `object_type` | `string` | Yes | The object type (issue, account, contact) |
| `hex_color` | `string` | No | The hex color code of the tag |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.hex_color` | `string \| null` |  |
| `data.object_type` | `string \| null` |  |
| `data.value` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Tags Get

Get a tag by its ID

#### Python SDK

```python
await pylon.tags.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the tag |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `hex_color` | `string \| null` |  |
| `object_type` | `string \| null` |  |
| `value` | `string \| null` |  |


</details>

### Tags Update

Update an existing tag by ID

#### Python SDK

```python
await pylon.tags.update(
    value="<str>",
    hex_color="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "update",
    "params": {
        "value": "<str>",
        "hex_color": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `value` | `string` | No | The tag value |
| `hex_color` | `string` | No | The hex color code of the tag |
| `id` | `string` | Yes | The ID of the tag to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.hex_color` | `string \| null` |  |
| `data.object_type` | `string \| null` |  |
| `data.value` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Tags Context Store Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.tags.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the tag |
| `value` | `string` | Display value of the tag |
| `object_type` | `string` | Type of object this tag applies to (e.g. issue, account) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the tag |
| `data[].value` | `string` | Display value of the tag |
| `data[].object_type` | `string` | Type of object this tag applies to (e.g. issue, account) |

</details>

## Users

### Users List

Get a list of users

#### Python SDK

```python
await pylon.users.list()
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
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `avatar_url` | `string \| null` |  |
| `email` | `string \| null` |  |
| `emails` | `array \| null` |  |
| `name` | `string \| null` |  |
| `role_id` | `string \| null` |  |
| `status` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Users Get

Get a single user by ID

#### Python SDK

```python
await pylon.users.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the user |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `avatar_url` | `string \| null` |  |
| `email` | `string \| null` |  |
| `emails` | `array \| null` |  |
| `name` | `string \| null` |  |
| `role_id` | `string \| null` |  |
| `status` | `string \| null` |  |


</details>

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.users.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
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
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the user |
| `name` | `string` | Full name of the user |
| `email` | `string` | Primary email address of the user |
| `role_id` | `string` | Identifier of the user's role |
| `status` | `string` | Current status of the user (e.g. active, disabled) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the user |
| `data[].name` | `string` | Full name of the user |
| `data[].email` | `string` | Primary email address of the user |
| `data[].role_id` | `string` | Identifier of the user's role |
| `data[].status` | `string` | Current status of the user (e.g. active, disabled) |

</details>

## Custom Fields

### Custom Fields List

Get all custom fields for a given object type

#### Python SDK

```python
await pylon.custom_fields.list(
    object_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_fields",
    "action": "list",
    "params": {
        "object_type": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `object_type` | `"account" \| "issue" \| "contact"` | Yes | The object type of the custom fields. Can be "account", "issue", or "contact". |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `default_value` | `string \| null` |  |
| `default_values` | `array \| null` |  |
| `description` | `string \| null` |  |
| `is_read_only` | `boolean \| null` |  |
| `label` | `string \| null` |  |
| `number_metadata` | `object \| any` |  |
| `object_type` | `string \| null` |  |
| `select_metadata` | `object \| any` |  |
| `slug` | `string \| null` |  |
| `source` | `string \| null` |  |
| `type` | `string \| null` |  |
| `updated_at` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Custom Fields Get

Get a custom field by its ID

#### Python SDK

```python
await pylon.custom_fields.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_fields",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the custom field |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `created_at` | `string \| null` |  |
| `default_value` | `string \| null` |  |
| `default_values` | `array \| null` |  |
| `description` | `string \| null` |  |
| `is_read_only` | `boolean \| null` |  |
| `label` | `string \| null` |  |
| `number_metadata` | `object \| any` |  |
| `object_type` | `string \| null` |  |
| `select_metadata` | `object \| any` |  |
| `slug` | `string \| null` |  |
| `source` | `string \| null` |  |
| `type` | `string \| null` |  |
| `updated_at` | `string \| null` |  |


</details>

### Custom Fields Context Store Search

Search and filter custom fields records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.custom_fields.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_fields",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the custom field |
| `label` | `string` | Display label of the custom field |
| `slug` | `string` | URL-safe identifier for the custom field |
| `type` | `string` | Data type of the custom field (e.g. text, select) |
| `object_type` | `string` | Type of object this custom field applies to (e.g. issue, account) |
| `is_read_only` | `boolean` | Whether the custom field is read-only |
| `created_at` | `string` | Timestamp when the custom field was created, in ISO 8601 format |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the custom field |
| `data[].label` | `string` | Display label of the custom field |
| `data[].slug` | `string` | URL-safe identifier for the custom field |
| `data[].type` | `string` | Data type of the custom field (e.g. text, select) |
| `data[].object_type` | `string` | Type of object this custom field applies to (e.g. issue, account) |
| `data[].is_read_only` | `boolean` | Whether the custom field is read-only |
| `data[].created_at` | `string` | Timestamp when the custom field was created, in ISO 8601 format |

</details>

## Ticket Forms

### Ticket Forms List

Get a list of ticket forms

#### Python SDK

```python
await pylon.ticket_forms.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_forms",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `description_html` | `string \| null` |  |
| `fields` | `array \| null` |  |
| `fields[].description_html` | `string \| null` |  |
| `fields[].name` | `string \| null` |  |
| `fields[].slug` | `string \| null` |  |
| `fields[].type` | `string \| null` |  |
| `is_public` | `boolean \| null` |  |
| `name` | `string \| null` |  |
| `slug` | `string \| null` |  |
| `url` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### Ticket Forms Context Store Search

Search and filter ticket forms records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.ticket_forms.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_forms",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the ticket form |
| `name` | `string` | Display name of the ticket form |
| `slug` | `string` | URL-safe identifier for the ticket form |
| `is_public` | `boolean` | Whether the ticket form is publicly accessible |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the ticket form |
| `data[].name` | `string` | Display name of the ticket form |
| `data[].slug` | `string` | URL-safe identifier for the ticket form |
| `data[].is_public` | `boolean` | Whether the ticket form is publicly accessible |

</details>

## User Roles

### User Roles List

Get a list of all user roles

#### Python SDK

```python
await pylon.user_roles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user_roles",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `slug` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_next_page` | `boolean` |  |

</details>

### User Roles Context Store Search

Search and filter user roles records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pylon.user_roles.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user_roles",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Unique identifier for the user role |
| `name` | `string` | Display name of the user role |
| `slug` | `string` | URL-safe identifier for the user role |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the user role |
| `data[].name` | `string` | Display name of the user role |
| `data[].slug` | `string` | URL-safe identifier for the user role |

</details>

## Tasks

### Tasks Create

Create a new task

#### Python SDK

```python
await pylon.tasks.create(
    title="<str>",
    body_html="<str>",
    status="<str>",
    assignee_id="<str>",
    project_id="<str>",
    milestone_id="<str>",
    due_date="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "create",
    "params": {
        "title": "<str>",
        "body_html": "<str>",
        "status": "<str>",
        "assignee_id": "<str>",
        "project_id": "<str>",
        "milestone_id": "<str>",
        "due_date": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | Yes | The title of the task |
| `body_html` | `string` | No | The body HTML of the task |
| `status` | `string` | No | The status of the task (not_started, in_progress, completed) |
| `assignee_id` | `string` | No | The assignee ID for the task |
| `project_id` | `string` | No | The project ID for the task |
| `milestone_id` | `string` | No | The milestone ID for the task |
| `due_date` | `string` | No | The due date for the task (RFC3339) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.title` | `string \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.status` | `string \| null` |  |
| `data.assignee_id` | `string \| null` |  |
| `data.project_id` | `string \| null` |  |
| `data.milestone_id` | `string \| null` |  |
| `data.due_date` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Tasks Update

Update an existing task by ID

#### Python SDK

```python
await pylon.tasks.update(
    title="<str>",
    body_html="<str>",
    status="<str>",
    assignee_id="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "update",
    "params": {
        "title": "<str>",
        "body_html": "<str>",
        "status": "<str>",
        "assignee_id": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | No | The title of the task |
| `body_html` | `string` | No | The body HTML of the task |
| `status` | `string` | No | The status of the task (not_started, in_progress, completed) |
| `assignee_id` | `string` | No | The assignee ID for the task |
| `id` | `string` | Yes | The ID of the task to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.title` | `string \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.status` | `string \| null` |  |
| `data.assignee_id` | `string \| null` |  |
| `data.project_id` | `string \| null` |  |
| `data.milestone_id` | `string \| null` |  |
| `data.due_date` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Projects

### Projects Create

Create a new project

#### Python SDK

```python
await pylon.projects.create(
    name="<str>",
    account_id="<str>",
    description_html="<str>",
    start_date="<str>",
    end_date="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "create",
    "params": {
        "name": "<str>",
        "account_id": "<str>",
        "description_html": "<str>",
        "start_date": "<str>",
        "end_date": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | The name of the project |
| `account_id` | `string` | Yes | The account ID for the project |
| `description_html` | `string` | No | The HTML description of the project |
| `start_date` | `string` | No | The start date of the project (RFC3339) |
| `end_date` | `string` | No | The end date of the project (RFC3339) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `data.description_html` | `string \| null` |  |
| `data.account_id` | `string \| null` |  |
| `data.owner_id` | `string \| null` |  |
| `data.start_date` | `string \| null` |  |
| `data.end_date` | `string \| null` |  |
| `data.is_archived` | `boolean \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Projects Update

Update an existing project by ID

#### Python SDK

```python
await pylon.projects.update(
    name="<str>",
    description_html="<str>",
    is_archived=True,
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "update",
    "params": {
        "name": "<str>",
        "description_html": "<str>",
        "is_archived": True,
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the project |
| `description_html` | `string` | No | The HTML description of the project |
| `is_archived` | `boolean` | No | Whether the project is archived |
| `id` | `string` | Yes | The ID of the project to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `data.description_html` | `string \| null` |  |
| `data.account_id` | `string \| null` |  |
| `data.owner_id` | `string \| null` |  |
| `data.start_date` | `string \| null` |  |
| `data.end_date` | `string \| null` |  |
| `data.is_archived` | `boolean \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Milestones

### Milestones Create

Create a new milestone

#### Python SDK

```python
await pylon.milestones.create(
    name="<str>",
    project_id="<str>",
    due_date="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "create",
    "params": {
        "name": "<str>",
        "project_id": "<str>",
        "due_date": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | The name of the milestone |
| `project_id` | `string` | Yes | The project ID for the milestone |
| `due_date` | `string` | No | The due date of the milestone (RFC3339) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `data.project_id` | `string \| null` |  |
| `data.due_date` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Milestones Update

Update an existing milestone by ID

#### Python SDK

```python
await pylon.milestones.update(
    name="<str>",
    due_date="<str>",
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "update",
    "params": {
        "name": "<str>",
        "due_date": "<str>",
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | The name of the milestone |
| `due_date` | `string` | No | The due date of the milestone (RFC3339) |
| `id` | `string` | Yes | The ID of the milestone to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.name` | `string \| null` |  |
| `data.project_id` | `string \| null` |  |
| `data.due_date` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Articles

### Articles Create

Create a new article in a knowledge base

#### Python SDK

```python
await pylon.articles.create(
    title="<str>",
    body_html="<str>",
    author_user_id="<str>",
    slug="<str>",
    is_published=True,
    kb_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "articles",
    "action": "create",
    "params": {
        "title": "<str>",
        "body_html": "<str>",
        "author_user_id": "<str>",
        "slug": "<str>",
        "is_published": True,
        "kb_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | Yes | The title of the article |
| `body_html` | `string` | Yes | The HTML body of the article |
| `author_user_id` | `string` | Yes | The ID of the user attributed as the author |
| `slug` | `string` | No | The slug of the article |
| `is_published` | `boolean` | No | Whether the article should be published |
| `kb_id` | `string` | Yes | The ID of the knowledge base |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.title` | `string \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.slug` | `string \| null` |  |
| `data.is_published` | `boolean \| null` |  |
| `data.author_user_id` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

### Articles Update

Update an existing article in a knowledge base

#### Python SDK

```python
await pylon.articles.update(
    title="<str>",
    body_html="<str>",
    kb_id="<str>",
    article_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "articles",
    "action": "update",
    "params": {
        "title": "<str>",
        "body_html": "<str>",
        "kb_id": "<str>",
        "article_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | No | The title of the article |
| `body_html` | `string` | No | The HTML body of the article |
| `kb_id` | `string` | Yes | The ID of the knowledge base |
| `article_id` | `string` | Yes | The ID of the article to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.title` | `string \| null` |  |
| `data.body_html` | `string \| null` |  |
| `data.slug` | `string \| null` |  |
| `data.is_published` | `boolean \| null` |  |
| `data.author_user_id` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `data.updated_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Collections

### Collections Create

Create a new collection in a knowledge base

#### Python SDK

```python
await pylon.collections.create(
    title="<str>",
    description="<str>",
    slug="<str>",
    kb_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collections",
    "action": "create",
    "params": {
        "title": "<str>",
        "description": "<str>",
        "slug": "<str>",
        "kb_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | Yes | The title of the collection |
| `description` | `string` | No | The description of the collection |
| `slug` | `string` | No | The slug of the collection |
| `kb_id` | `string` | Yes | The ID of the knowledge base |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `object` |  |
| `data.id` | `string` |  |
| `data.title` | `string \| null` |  |
| `data.description` | `string \| null` |  |
| `data.slug` | `string \| null` |  |
| `data.created_at` | `string \| null` |  |
| `request_id` | `string` |  |


</details>

## Me

### Me Get

Get the currently authenticated user

#### Python SDK

```python
await pylon.me.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "me",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `avatar_url` | `string \| null` |  |
| `email` | `string \| null` |  |
| `emails` | `array \| null` |  |
| `name` | `string \| null` |  |
| `role_id` | `string \| null` |  |
| `status` | `string \| null` |  |


</details>

