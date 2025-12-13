# Zendesk-Support

## Supported Entities and Actions

| Entity | Actions |
|--------|---------|
| Tickets | [List](#tickets-list), [Get](#tickets-get) |
| Users | [List](#users-list), [Get](#users-get) |
| Organizations | [List](#organizations-list), [Get](#organizations-get) |
| Groups | [List](#groups-list), [Get](#groups-get) |
| Ticket Comments | [List](#ticket-comments-list) |
| Attachments | [Get](#attachments-get), [Download](#attachments-download) |
| Ticket Audits | [List](#ticket-audits-list), [List](#ticket-audits-list) |
| Ticket Metrics | [List](#ticket-metrics-list) |
| Ticket Fields | [List](#ticket-fields-list), [Get](#ticket-fields-get) |
| Brands | [List](#brands-list), [Get](#brands-get) |
| Views | [List](#views-list), [Get](#views-get) |
| Macros | [List](#macros-list), [Get](#macros-get) |
| Triggers | [List](#triggers-list), [Get](#triggers-get) |
| Automations | [List](#automations-list), [Get](#automations-get) |
| Tags | [List](#tags-list) |
| Satisfaction Ratings | [List](#satisfaction-ratings-list), [Get](#satisfaction-ratings-get) |
| Group Memberships | [List](#group-memberships-list) |
| Organization Memberships | [List](#organization-memberships-list) |
| Sla Policies | [List](#sla-policies-list), [Get](#sla-policies-get) |
| Ticket Forms | [List](#ticket-forms-list), [Get](#ticket-forms-get) |
| Articles | [List](#articles-list), [Get](#articles-get) |
| Article Attachments | [List](#article-attachments-list), [Get](#article-attachments-get), [Download](#article-attachments-download) |

### Tickets

#### Tickets List

Returns a list of all tickets in your account

**Python SDK**

```python
zendesk_support.tickets.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `external_id` | `string` | No | Lists tickets by external id |
| `sort` | `"id" \| "status" \| "updated_at" \| "-id" \| "-status" \| "-updated_at"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `external_id` | `string \| null` |  |
| `type` | `string \| null` |  |
| `subject` | `string \| null` |  |
| `raw_subject` | `string \| null` |  |
| `description` | `string` |  |
| `priority` | `string \| null` |  |
| `status` | `"new" \| "open" \| "pending" \| "hold" \| "solved" \| "closed"` |  |
| `recipient` | `string \| null` |  |
| `requester_id` | `integer` |  |
| `submitter_id` | `integer` |  |
| `assignee_id` | `integer \| null` |  |
| `organization_id` | `integer \| null` |  |
| `group_id` | `integer \| null` |  |
| `collaborator_ids` | `array<integer>` |  |
| `follower_ids` | `array<integer>` |  |
| `email_cc_ids` | `array<integer>` |  |
| `forum_topic_id` | `integer \| null` |  |
| `problem_id` | `integer \| null` |  |
| `has_incidents` | `boolean` |  |
| `is_public` | `boolean` |  |
| `due_at` | `string \| null` |  |
| `tags` | `array<string>` |  |
| `custom_fields` | `array<object>` |  |
| `satisfaction_rating` | `object` |  |
| `sharing_agreement_ids` | `array<integer>` |  |
| `custom_status_id` | `integer` |  |
| `fields` | `array<object>` |  |
| `followup_ids` | `array<integer>` |  |
| `ticket_form_id` | `integer` |  |
| `brand_id` | `integer` |  |
| `allow_channelback` | `boolean` |  |
| `allow_attachments` | `boolean` |  |
| `from_messaging_channel` | `boolean` |  |
| `generated_timestamp` | `integer` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `via` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Tickets Get

Returns a ticket by its ID

**Python SDK**

```python
zendesk_support.tickets.get(
    ticket_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "get",
    "params": {
        "ticket_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_id` | `integer` | Yes | The ID of the ticket |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `external_id` | `string \| null` |  |
| `type` | `string \| null` |  |
| `subject` | `string \| null` |  |
| `raw_subject` | `string \| null` |  |
| `description` | `string` |  |
| `priority` | `string \| null` |  |
| `status` | `"new" \| "open" \| "pending" \| "hold" \| "solved" \| "closed"` |  |
| `recipient` | `string \| null` |  |
| `requester_id` | `integer` |  |
| `submitter_id` | `integer` |  |
| `assignee_id` | `integer \| null` |  |
| `organization_id` | `integer \| null` |  |
| `group_id` | `integer \| null` |  |
| `collaborator_ids` | `array<integer>` |  |
| `follower_ids` | `array<integer>` |  |
| `email_cc_ids` | `array<integer>` |  |
| `forum_topic_id` | `integer \| null` |  |
| `problem_id` | `integer \| null` |  |
| `has_incidents` | `boolean` |  |
| `is_public` | `boolean` |  |
| `due_at` | `string \| null` |  |
| `tags` | `array<string>` |  |
| `custom_fields` | `array<object>` |  |
| `satisfaction_rating` | `object` |  |
| `sharing_agreement_ids` | `array<integer>` |  |
| `custom_status_id` | `integer` |  |
| `fields` | `array<object>` |  |
| `followup_ids` | `array<integer>` |  |
| `ticket_form_id` | `integer` |  |
| `brand_id` | `integer` |  |
| `allow_channelback` | `boolean` |  |
| `allow_attachments` | `boolean` |  |
| `from_messaging_channel` | `boolean` |  |
| `generated_timestamp` | `integer` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `via` | `object` |  |


</details>

### Users

#### Users List

Returns a list of all users in your account

**Python SDK**

```python
zendesk_support.users.list()
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
| `page` | `integer` | No | Page number for pagination |
| `role` | `"end-user" \| "agent" \| "admin"` | No | Filter by role |
| `external_id` | `string` | No | Filter by external id |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `email` | `string \| null` |  |
| `alias` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `time_zone` | `string` |  |
| `locale` | `string` |  |
| `locale_id` | `integer` |  |
| `organization_id` | `integer \| null` |  |
| `role` | `"end-user" \| "agent" \| "admin"` |  |
| `role_type` | `integer \| null` |  |
| `custom_role_id` | `integer \| null` |  |
| `external_id` | `string \| null` |  |
| `tags` | `array<string>` |  |
| `active` | `boolean` |  |
| `verified` | `boolean` |  |
| `shared` | `boolean` |  |
| `shared_agent` | `boolean` |  |
| `shared_phone_number` | `boolean \| null` |  |
| `signature` | `string \| null` |  |
| `details` | `string \| null` |  |
| `notes` | `string \| null` |  |
| `suspended` | `boolean` |  |
| `restricted_agent` | `boolean` |  |
| `only_private_comments` | `boolean` |  |
| `moderator` | `boolean` |  |
| `ticket_restriction` | `string \| null` |  |
| `default_group_id` | `integer \| null` |  |
| `report_csv` | `boolean` |  |
| `photo` | `object \| null` |  |
| `user_fields` | `object` |  |
| `last_login_at` | `string \| null` |  |
| `two_factor_auth_enabled` | `boolean \| null` |  |
| `iana_time_zone` | `string` |  |
| `permanently_deleted` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Users Get

Returns a user by their ID

**Python SDK**

```python
zendesk_support.users.get(
    user_id=0
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
        "user_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_id` | `integer` | Yes | The ID of the user |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `email` | `string \| null` |  |
| `alias` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `time_zone` | `string` |  |
| `locale` | `string` |  |
| `locale_id` | `integer` |  |
| `organization_id` | `integer \| null` |  |
| `role` | `"end-user" \| "agent" \| "admin"` |  |
| `role_type` | `integer \| null` |  |
| `custom_role_id` | `integer \| null` |  |
| `external_id` | `string \| null` |  |
| `tags` | `array<string>` |  |
| `active` | `boolean` |  |
| `verified` | `boolean` |  |
| `shared` | `boolean` |  |
| `shared_agent` | `boolean` |  |
| `shared_phone_number` | `boolean \| null` |  |
| `signature` | `string \| null` |  |
| `details` | `string \| null` |  |
| `notes` | `string \| null` |  |
| `suspended` | `boolean` |  |
| `restricted_agent` | `boolean` |  |
| `only_private_comments` | `boolean` |  |
| `moderator` | `boolean` |  |
| `ticket_restriction` | `string \| null` |  |
| `default_group_id` | `integer \| null` |  |
| `report_csv` | `boolean` |  |
| `photo` | `object \| null` |  |
| `user_fields` | `object` |  |
| `last_login_at` | `string \| null` |  |
| `two_factor_auth_enabled` | `boolean \| null` |  |
| `iana_time_zone` | `string` |  |
| `permanently_deleted` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Organizations

#### Organizations List

Returns a list of all organizations in your account

**Python SDK**

```python
zendesk_support.organizations.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `details` | `string \| null` |  |
| `notes` | `string \| null` |  |
| `group_id` | `integer \| null` |  |
| `shared_tickets` | `boolean` |  |
| `shared_comments` | `boolean` |  |
| `external_id` | `string \| null` |  |
| `domain_names` | `array<string>` |  |
| `tags` | `array<string>` |  |
| `organization_fields` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Organizations Get

Returns an organization by its ID

**Python SDK**

```python
zendesk_support.organizations.get(
    organization_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "get",
    "params": {
        "organization_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_id` | `integer` | Yes | The ID of the organization |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `details` | `string \| null` |  |
| `notes` | `string \| null` |  |
| `group_id` | `integer \| null` |  |
| `shared_tickets` | `boolean` |  |
| `shared_comments` | `boolean` |  |
| `external_id` | `string \| null` |  |
| `domain_names` | `array<string>` |  |
| `tags` | `array<string>` |  |
| `organization_fields` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Groups

#### Groups List

Returns a list of all groups in your account

**Python SDK**

```python
zendesk_support.groups.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `exclude_deleted` | `boolean` | No | Exclude deleted groups |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `default` | `boolean` |  |
| `deleted` | `boolean` |  |
| `is_public` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Groups Get

Returns a group by its ID

**Python SDK**

```python
zendesk_support.groups.get(
    group_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "get",
    "params": {
        "group_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `integer` | Yes | The ID of the group |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `default` | `boolean` |  |
| `deleted` | `boolean` |  |
| `is_public` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Ticket Comments

#### Ticket Comments List

Returns a list of comments for a specific ticket

**Python SDK**

```python
zendesk_support.ticket_comments.list(
    ticket_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_comments",
    "action": "list",
    "params": {
        "ticket_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_id` | `integer` | Yes | The ID of the ticket |
| `page` | `integer` | No | Page number for pagination |
| `include_inline_images` | `boolean` | No | Include inline images in the response |
| `sort` | `"created_at" \| "-created_at"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `string` |  |
| `body` | `string` |  |
| `html_body` | `string` |  |
| `plain_body` | `string` |  |
| `public` | `boolean` |  |
| `author_id` | `integer` |  |
| `attachments` | `array<object>` |  |
| `audit_id` | `integer` |  |
| `via` | `object` |  |
| `metadata` | `object` |  |
| `created_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Attachments

#### Attachments Get

Returns an attachment by its ID

**Python SDK**

```python
zendesk_support.attachments.get(
    attachment_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "get",
    "params": {
        "attachment_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_id` | `integer` | Yes | The ID of the attachment |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `file_name` | `string` |  |
| `content_url` | `string` |  |
| `mapped_content_url` | `string` |  |
| `content_type` | `string` |  |
| `size` | `integer` |  |
| `width` | `integer \| null` |  |
| `height` | `integer \| null` |  |
| `inline` | `boolean` |  |
| `deleted` | `boolean` |  |
| `malware_access_override` | `boolean` |  |
| `malware_scan_result` | `string` |  |
| `url` | `string` |  |
| `thumbnails` | `array<object>` |  |


</details>

#### Attachments Download

Downloads the file content of a ticket attachment

**Python SDK**

```python
async for chunk in zendesk_support.attachments.download(    attachment_id=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "attachments",
    "action": "download",
    "params": {
        "attachment_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_id` | `integer` | Yes | The ID of the attachment |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Ticket Audits

#### Ticket Audits List

Returns a list of all ticket audits

**Python SDK**

```python
zendesk_support.ticket_audits.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_audits",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `ticket_id` | `integer` |  |
| `author_id` | `integer` |  |
| `metadata` | `object` |  |
| `via` | `object` |  |
| `events` | `array<object>` |  |
| `created_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Ticket Audits List

Returns a list of audits for a specific ticket

**Python SDK**

```python
zendesk_support.ticket_audits.list(
    ticket_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_audits",
    "action": "list",
    "params": {
        "ticket_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_id` | `integer` | Yes | The ID of the ticket |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `ticket_id` | `integer` |  |
| `author_id` | `integer` |  |
| `metadata` | `object` |  |
| `via` | `object` |  |
| `events` | `array<object>` |  |
| `created_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Metrics

#### Ticket Metrics List

Returns a list of all ticket metrics

**Python SDK**

```python
zendesk_support.ticket_metrics.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_metrics",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `ticket_id` | `integer` |  |
| `group_stations` | `integer` |  |
| `assignee_stations` | `integer` |  |
| `reopens` | `integer` |  |
| `replies` | `integer` |  |
| `assignee_updated_at` | `string \| null` |  |
| `requester_updated_at` | `string` |  |
| `status_updated_at` | `string` |  |
| `initially_assigned_at` | `string \| null` |  |
| `assigned_at` | `string \| null` |  |
| `solved_at` | `string \| null` |  |
| `latest_comment_added_at` | `string` |  |
| `reply_time_in_minutes` | `object` |  |
| `first_resolution_time_in_minutes` | `object` |  |
| `full_resolution_time_in_minutes` | `object` |  |
| `agent_wait_time_in_minutes` | `object` |  |
| `requester_wait_time_in_minutes` | `object` |  |
| `on_hold_time_in_minutes` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Fields

#### Ticket Fields List

Returns a list of all ticket fields

**Python SDK**

```python
zendesk_support.ticket_fields.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_fields",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `locale` | `string` | No | Locale for the results |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `type` | `string` |  |
| `title` | `string` |  |
| `raw_title` | `string` |  |
| `description` | `string` |  |
| `raw_description` | `string` |  |
| `position` | `integer` |  |
| `active` | `boolean` |  |
| `required` | `boolean` |  |
| `collapsed_for_agents` | `boolean` |  |
| `regexp_for_validation` | `string \| null` |  |
| `title_in_portal` | `string` |  |
| `raw_title_in_portal` | `string` |  |
| `visible_in_portal` | `boolean` |  |
| `editable_in_portal` | `boolean` |  |
| `required_in_portal` | `boolean` |  |
| `tag` | `string \| null` |  |
| `custom_field_options` | `array<object>` |  |
| `system_field_options` | `array<object>` |  |
| `sub_type_id` | `integer` |  |
| `removable` | `boolean` |  |
| `agent_description` | `string \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Ticket Fields Get

Returns a ticket field by its ID

**Python SDK**

```python
zendesk_support.ticket_fields.get(
    ticket_field_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_fields",
    "action": "get",
    "params": {
        "ticket_field_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_field_id` | `integer` | Yes | The ID of the ticket field |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `type` | `string` |  |
| `title` | `string` |  |
| `raw_title` | `string` |  |
| `description` | `string` |  |
| `raw_description` | `string` |  |
| `position` | `integer` |  |
| `active` | `boolean` |  |
| `required` | `boolean` |  |
| `collapsed_for_agents` | `boolean` |  |
| `regexp_for_validation` | `string \| null` |  |
| `title_in_portal` | `string` |  |
| `raw_title_in_portal` | `string` |  |
| `visible_in_portal` | `boolean` |  |
| `editable_in_portal` | `boolean` |  |
| `required_in_portal` | `boolean` |  |
| `tag` | `string \| null` |  |
| `custom_field_options` | `array<object>` |  |
| `system_field_options` | `array<object>` |  |
| `sub_type_id` | `integer` |  |
| `removable` | `boolean` |  |
| `agent_description` | `string \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Brands

#### Brands List

Returns a list of all brands for the account

**Python SDK**

```python
zendesk_support.brands.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "brands",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `brand_url` | `string` |  |
| `subdomain` | `string` |  |
| `host_mapping` | `string \| null` |  |
| `has_help_center` | `boolean` |  |
| `help_center_state` | `string` |  |
| `active` | `boolean` |  |
| `default` | `boolean` |  |
| `is_deleted` | `boolean` |  |
| `logo` | `object \| null` |  |
| `ticket_form_ids` | `array<integer>` |  |
| `signature_template` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Brands Get

Returns a brand by its ID

**Python SDK**

```python
zendesk_support.brands.get(
    brand_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "brands",
    "action": "get",
    "params": {
        "brand_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `brand_id` | `integer` | Yes | The ID of the brand |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `brand_url` | `string` |  |
| `subdomain` | `string` |  |
| `host_mapping` | `string \| null` |  |
| `has_help_center` | `boolean` |  |
| `help_center_state` | `string` |  |
| `active` | `boolean` |  |
| `default` | `boolean` |  |
| `is_deleted` | `boolean` |  |
| `logo` | `object \| null` |  |
| `ticket_form_ids` | `array<integer>` |  |
| `signature_template` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Views

#### Views List

Returns a list of all views for the account

**Python SDK**

```python
zendesk_support.views.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "views",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `access` | `"personal" \| "shared" \| "account"` | No | Filter by access level |
| `active` | `boolean` | No | Filter by active status |
| `group_id` | `integer` | No | Filter by group ID |
| `sort_by` | `"alphabetical" \| "created_at" \| "updated_at" \| "position"` | No | Sort results |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `description` | `string \| null` |  |
| `execution` | `object` |  |
| `conditions` | `object` |  |
| `restriction` | `object \| null` |  |
| `raw_title` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Views Get

Returns a view by its ID

**Python SDK**

```python
zendesk_support.views.get(
    view_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "views",
    "action": "get",
    "params": {
        "view_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `view_id` | `integer` | Yes | The ID of the view |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `description` | `string \| null` |  |
| `execution` | `object` |  |
| `conditions` | `object` |  |
| `restriction` | `object \| null` |  |
| `raw_title` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Macros

#### Macros List

Returns a list of all macros for the account

**Python SDK**

```python
zendesk_support.macros.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "macros",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `access` | `"personal" \| "shared" \| "account"` | No | Filter by access level |
| `active` | `boolean` | No | Filter by active status |
| `category` | `integer` | No | Filter by category |
| `group_id` | `integer` | No | Filter by group ID |
| `only_viewable` | `boolean` | No | Return only viewable macros |
| `sort_by` | `"alphabetical" \| "created_at" \| "updated_at" \| "position"` | No | Sort results |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `description` | `string` |  |
| `actions` | `array<object>` |  |
| `restriction` | `object \| null` |  |
| `raw_title` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Macros Get

Returns a macro by its ID

**Python SDK**

```python
zendesk_support.macros.get(
    macro_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "macros",
    "action": "get",
    "params": {
        "macro_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `macro_id` | `integer` | Yes | The ID of the macro |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `description` | `string` |  |
| `actions` | `array<object>` |  |
| `restriction` | `object \| null` |  |
| `raw_title` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Triggers

#### Triggers List

Returns a list of all triggers for the account

**Python SDK**

```python
zendesk_support.triggers.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "triggers",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `active` | `boolean` | No | Filter by active status |
| `category_id` | `string` | No | Filter by category ID |
| `sort` | `"alphabetical" \| "created_at" \| "updated_at" \| "position"` | No | Sort results |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `description` | `string \| null` |  |
| `conditions` | `object` |  |
| `actions` | `array<object>` |  |
| `raw_title` | `string` |  |
| `category_id` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Triggers Get

Returns a trigger by its ID

**Python SDK**

```python
zendesk_support.triggers.get(
    trigger_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "triggers",
    "action": "get",
    "params": {
        "trigger_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `trigger_id` | `integer` | Yes | The ID of the trigger |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `description` | `string \| null` |  |
| `conditions` | `object` |  |
| `actions` | `array<object>` |  |
| `raw_title` | `string` |  |
| `category_id` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Automations

#### Automations List

Returns a list of all automations for the account

**Python SDK**

```python
zendesk_support.automations.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "automations",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `active` | `boolean` | No | Filter by active status |
| `sort` | `"alphabetical" \| "created_at" \| "updated_at" \| "position"` | No | Sort results |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `conditions` | `object` |  |
| `actions` | `array<object>` |  |
| `raw_title` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Automations Get

Returns an automation by its ID

**Python SDK**

```python
zendesk_support.automations.get(
    automation_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "automations",
    "action": "get",
    "params": {
        "automation_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `automation_id` | `integer` | Yes | The ID of the automation |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `active` | `boolean` |  |
| `position` | `integer` |  |
| `conditions` | `object` |  |
| `actions` | `array<object>` |  |
| `raw_title` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Tags

#### Tags List

Returns a list of all tags used in the account

**Python SDK**

```python
zendesk_support.tags.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `count` | `integer` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Satisfaction Ratings

#### Satisfaction Ratings List

Returns a list of all satisfaction ratings

**Python SDK**

```python
zendesk_support.satisfaction_ratings.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "satisfaction_ratings",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `score` | `"offered" \| "unoffered" \| "received" \| "good" \| "bad"` | No | Filter by score |
| `start_time` | `integer` | No | Start time (Unix epoch) |
| `end_time` | `integer` | No | End time (Unix epoch) |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `assignee_id` | `integer \| null` |  |
| `group_id` | `integer \| null` |  |
| `requester_id` | `integer` |  |
| `ticket_id` | `integer` |  |
| `score` | `string` |  |
| `comment` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `reason_id` | `integer \| null` |  |
| `reason_code` | `integer \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Satisfaction Ratings Get

Returns a satisfaction rating by its ID

**Python SDK**

```python
zendesk_support.satisfaction_ratings.get(
    satisfaction_rating_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "satisfaction_ratings",
    "action": "get",
    "params": {
        "satisfaction_rating_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `satisfaction_rating_id` | `integer` | Yes | The ID of the satisfaction rating |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `assignee_id` | `integer \| null` |  |
| `group_id` | `integer \| null` |  |
| `requester_id` | `integer` |  |
| `ticket_id` | `integer` |  |
| `score` | `string` |  |
| `comment` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `reason_id` | `integer \| null` |  |
| `reason_code` | `integer \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Group Memberships

#### Group Memberships List

Returns a list of all group memberships

**Python SDK**

```python
zendesk_support.group_memberships.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_memberships",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `user_id` | `integer` |  |
| `group_id` | `integer` |  |
| `default` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Organization Memberships

#### Organization Memberships List

Returns a list of all organization memberships

**Python SDK**

```python
zendesk_support.organization_memberships.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organization_memberships",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `user_id` | `integer` |  |
| `organization_id` | `integer` |  |
| `default` | `boolean` |  |
| `organization_name` | `string` |  |
| `view_tickets` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Sla Policies

#### Sla Policies List

Returns a list of all SLA policies

**Python SDK**

```python
zendesk_support.sla_policies.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sla_policies",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `description` | `string` |  |
| `position` | `integer` |  |
| `filter` | `object` |  |
| `policy_metrics` | `array<object>` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Sla Policies Get

Returns an SLA policy by its ID

**Python SDK**

```python
zendesk_support.sla_policies.get(
    sla_policy_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sla_policies",
    "action": "get",
    "params": {
        "sla_policy_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sla_policy_id` | `integer` | Yes | The ID of the SLA policy |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `description` | `string` |  |
| `position` | `integer` |  |
| `filter` | `object` |  |
| `policy_metrics` | `array<object>` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Ticket Forms

#### Ticket Forms List

Returns a list of all ticket forms for the account

**Python SDK**

```python
zendesk_support.ticket_forms.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_forms",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `active` | `boolean` | No | Filter by active status |
| `end_user_visible` | `boolean` | No | Filter by end user visibility |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `display_name` | `string` |  |
| `raw_name` | `string` |  |
| `raw_display_name` | `string` |  |
| `position` | `integer` |  |
| `active` | `boolean` |  |
| `end_user_visible` | `boolean` |  |
| `default` | `boolean` |  |
| `in_all_brands` | `boolean` |  |
| `restricted_brand_ids` | `array<integer>` |  |
| `ticket_field_ids` | `array<integer>` |  |
| `agent_conditions` | `array<object>` |  |
| `end_user_conditions` | `array<object>` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Ticket Forms Get

Returns a ticket form by its ID

**Python SDK**

```python
zendesk_support.ticket_forms.get(
    ticket_form_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_forms",
    "action": "get",
    "params": {
        "ticket_form_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_form_id` | `integer` | Yes | The ID of the ticket form |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `name` | `string` |  |
| `display_name` | `string` |  |
| `raw_name` | `string` |  |
| `raw_display_name` | `string` |  |
| `position` | `integer` |  |
| `active` | `boolean` |  |
| `end_user_visible` | `boolean` |  |
| `default` | `boolean` |  |
| `in_all_brands` | `boolean` |  |
| `restricted_brand_ids` | `array<integer>` |  |
| `ticket_field_ids` | `array<integer>` |  |
| `agent_conditions` | `array<object>` |  |
| `end_user_conditions` | `array<object>` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Articles

#### Articles List

Returns a list of all articles in the Help Center

**Python SDK**

```python
zendesk_support.articles.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "articles",
    "action": "list"
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `sort_by` | `"created_at" \| "updated_at" \| "title" \| "position"` | No | Sort articles by field |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `html_url` | `string` |  |
| `title` | `string` |  |
| `body` | `string` |  |
| `locale` | `string` |  |
| `author_id` | `integer` |  |
| `section_id` | `integer` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `vote_sum` | `integer` |  |
| `vote_count` | `integer` |  |
| `label_names` | `array<string>` |  |
| `draft` | `boolean` |  |
| `promoted` | `boolean` |  |
| `position` | `integer` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Articles Get

Retrieves the details of a specific article

**Python SDK**

```python
zendesk_support.articles.get(
    id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "articles",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | The unique ID of the article |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `html_url` | `string` |  |
| `title` | `string` |  |
| `body` | `string` |  |
| `locale` | `string` |  |
| `author_id` | `integer` |  |
| `section_id` | `integer` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `vote_sum` | `integer` |  |
| `vote_count` | `integer` |  |
| `label_names` | `array<string>` |  |
| `draft` | `boolean` |  |
| `promoted` | `boolean` |  |
| `position` | `integer` |  |


</details>

### Article Attachments

#### Article Attachments List

Returns a list of all attachments for a specific article

**Python SDK**

```python
zendesk_support.article_attachments.list(
    article_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "article_attachments",
    "action": "list",
    "params": {
        "article_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `article_id` | `integer` | Yes | The unique ID of the article |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `article_id` | `integer` |  |
| `file_name` | `string` |  |
| `content_type` | `string` |  |
| `content_url` | `string` |  |
| `size` | `integer` |  |
| `inline` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

#### Article Attachments Get

Retrieves the metadata of a specific attachment for a specific article

**Python SDK**

```python
zendesk_support.article_attachments.get(
    article_id=0,
    attachment_id=0
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "article_attachments",
    "action": "get",
    "params": {
        "article_id": 0,
        "attachment_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `article_id` | `integer` | Yes | The unique ID of the article |
| `attachment_id` | `integer` | Yes | The unique ID of the attachment |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `article_id` | `integer` |  |
| `file_name` | `string` |  |
| `content_type` | `string` |  |
| `content_url` | `string` |  |
| `size` | `integer` |  |
| `inline` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

#### Article Attachments Download

Downloads the file content of a specific attachment

**Python SDK**

```python
async for chunk in zendesk_support.article_attachments.download(    article_id=0,    attachment_id=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "article_attachments",
    "action": "download",
    "params": {
        "article_id": 0,
        "attachment_id": 0
    }
}'
```


**Params**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `article_id` | `integer` | Yes | The unique ID of the article |
| `attachment_id` | `integer` | Yes | The unique ID of the attachment |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |




## Configuration

The connector requires the following configuration variables:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `subdomain` | `string` | Yes | your-subdomain | Your Zendesk subdomain |

These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.


## Authentication

The Zendesk-Support connector supports the following authentication methods:


### OAuth 2.0

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | OAuth 2.0 access token |
| `refresh_token` | `str` | No | OAuth 2.0 refresh token (optional) |

#### Example

**Python SDK**

```python
ZendeskSupportConnector(
  auth_config=ZendeskSupportAuthConfig(
    access_token="<OAuth 2.0 access token>",
    refresh_token="<OAuth 2.0 refresh token (optional)>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "79c1aa37-dae3-42ae-b333-d1c105477715",
  "auth_config": {
    "access_token": "<OAuth 2.0 access token>",
    "refresh_token": "<OAuth 2.0 refresh token (optional)>"
  },
  "name": "My Zendesk-Support Connector"
}'
```


### API Token

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `email` | `str` | Yes | Your Zendesk account email address |
| `api_token` | `str` | Yes | Your Zendesk API token from Admin Center |

#### Example

**Python SDK**

```python
ZendeskSupportConnector(
  auth_config=ZendeskSupportAuthConfig(
    email="<Your Zendesk account email address>",
    api_token="<Your Zendesk API token from Admin Center>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "79c1aa37-dae3-42ae-b333-d1c105477715",
  "auth_config": {
    "email": "<Your Zendesk account email address>",
    "api_token": "<Your Zendesk API token from Admin Center>"
  },
  "name": "My Zendesk-Support Connector"
}'
```

