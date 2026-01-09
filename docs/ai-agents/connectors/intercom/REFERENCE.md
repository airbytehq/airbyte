# Intercom full reference

This is the full reference documentation for the Intercom agent connector.

## Supported entities and actions

The Intercom connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](#contacts-list), [Get](#contacts-get) |
| Conversations | [List](#conversations-list), [Get](#conversations-get) |
| Companies | [List](#companies-list), [Get](#companies-get) |
| Teams | [List](#teams-list), [Get](#teams-get) |
| Admins | [List](#admins-list), [Get](#admins-get) |
| Tags | [List](#tags-list), [Get](#tags-get) |
| Segments | [List](#segments-list), [Get](#segments-get) |

### Contacts

#### Contacts List

Returns a paginated list of contacts in the workspace

**Python SDK**

```python
await intercom.contacts.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of contacts to return per page |
| `starting_after` | `string` | No | Cursor for pagination - get contacts after this ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `workspace_id` | `string \| null` |  |
| `external_id` | `string \| null` |  |
| `role` | `string \| null` |  |
| `email` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `name` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `social_profiles` | `object \| any` |  |
| `has_hard_bounced` | `boolean \| null` |  |
| `marked_email_as_spam` | `boolean \| null` |  |
| `unsubscribed_from_emails` | `boolean \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `signed_up_at` | `integer \| null` |  |
| `last_seen_at` | `integer \| null` |  |
| `last_replied_at` | `integer \| null` |  |
| `last_contacted_at` | `integer \| null` |  |
| `last_email_opened_at` | `integer \| null` |  |
| `last_email_clicked_at` | `integer \| null` |  |
| `language_override` | `string \| null` |  |
| `browser` | `string \| null` |  |
| `browser_version` | `string \| null` |  |
| `browser_language` | `string \| null` |  |
| `os` | `string \| null` |  |
| `location` | `object \| any` |  |
| `android_app_name` | `string \| null` |  |
| `android_app_version` | `string \| null` |  |
| `android_device` | `string \| null` |  |
| `android_os_version` | `string \| null` |  |
| `android_sdk_version` | `string \| null` |  |
| `android_last_seen_at` | `integer \| null` |  |
| `ios_app_name` | `string \| null` |  |
| `ios_app_version` | `string \| null` |  |
| `ios_device` | `string \| null` |  |
| `ios_os_version` | `string \| null` |  |
| `ios_sdk_version` | `string \| null` |  |
| `ios_last_seen_at` | `integer \| null` |  |
| `custom_attributes` | `object \| null` |  |
| `tags` | `object \| any` |  |
| `notes` | `object \| any` |  |
| `companies` | `object \| any` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |

</details>

#### Contacts Get

Get a single contact by ID

**Python SDK**

```python
await intercom.contacts.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Contact ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `workspace_id` | `string \| null` |  |
| `external_id` | `string \| null` |  |
| `role` | `string \| null` |  |
| `email` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `name` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `social_profiles` | `object \| any` |  |
| `has_hard_bounced` | `boolean \| null` |  |
| `marked_email_as_spam` | `boolean \| null` |  |
| `unsubscribed_from_emails` | `boolean \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `signed_up_at` | `integer \| null` |  |
| `last_seen_at` | `integer \| null` |  |
| `last_replied_at` | `integer \| null` |  |
| `last_contacted_at` | `integer \| null` |  |
| `last_email_opened_at` | `integer \| null` |  |
| `last_email_clicked_at` | `integer \| null` |  |
| `language_override` | `string \| null` |  |
| `browser` | `string \| null` |  |
| `browser_version` | `string \| null` |  |
| `browser_language` | `string \| null` |  |
| `os` | `string \| null` |  |
| `location` | `object \| any` |  |
| `android_app_name` | `string \| null` |  |
| `android_app_version` | `string \| null` |  |
| `android_device` | `string \| null` |  |
| `android_os_version` | `string \| null` |  |
| `android_sdk_version` | `string \| null` |  |
| `android_last_seen_at` | `integer \| null` |  |
| `ios_app_name` | `string \| null` |  |
| `ios_app_version` | `string \| null` |  |
| `ios_device` | `string \| null` |  |
| `ios_os_version` | `string \| null` |  |
| `ios_sdk_version` | `string \| null` |  |
| `ios_last_seen_at` | `integer \| null` |  |
| `custom_attributes` | `object \| null` |  |
| `tags` | `object \| any` |  |
| `notes` | `object \| any` |  |
| `companies` | `object \| any` |  |


</details>

### Conversations

#### Conversations List

Returns a paginated list of conversations

**Python SDK**

```python
await intercom.conversations.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversations",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of conversations to return per page |
| `starting_after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `waiting_since` | `integer \| null` |  |
| `snoozed_until` | `integer \| null` |  |
| `open` | `boolean \| null` |  |
| `state` | `string \| null` |  |
| `read` | `boolean \| null` |  |
| `priority` | `string \| null` |  |
| `admin_assignee_id` | `integer \| null` |  |
| `team_assignee_id` | `string \| null` |  |
| `tags` | `object \| any` |  |
| `conversation_rating` | `object \| any` |  |
| `source` | `object \| any` |  |
| `contacts` | `object \| any` |  |
| `teammates` | `object \| any` |  |
| `first_contact_reply` | `object \| any` |  |
| `sla_applied` | `object \| any` |  |
| `statistics` | `object \| any` |  |
| `conversation_parts` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |

</details>

#### Conversations Get

Get a single conversation by ID

**Python SDK**

```python
await intercom.conversations.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversations",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Conversation ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `waiting_since` | `integer \| null` |  |
| `snoozed_until` | `integer \| null` |  |
| `open` | `boolean \| null` |  |
| `state` | `string \| null` |  |
| `read` | `boolean \| null` |  |
| `priority` | `string \| null` |  |
| `admin_assignee_id` | `integer \| null` |  |
| `team_assignee_id` | `string \| null` |  |
| `tags` | `object \| any` |  |
| `conversation_rating` | `object \| any` |  |
| `source` | `object \| any` |  |
| `contacts` | `object \| any` |  |
| `teammates` | `object \| any` |  |
| `first_contact_reply` | `object \| any` |  |
| `sla_applied` | `object \| any` |  |
| `statistics` | `object \| any` |  |
| `conversation_parts` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


</details>

### Companies

#### Companies List

Returns a paginated list of companies

**Python SDK**

```python
await intercom.companies.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of companies to return per page |
| `starting_after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `company_id` | `string \| null` |  |
| `plan` | `object \| any` |  |
| `size` | `integer \| null` |  |
| `industry` | `string \| null` |  |
| `website` | `string \| null` |  |
| `remote_created_at` | `integer \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `last_request_at` | `integer \| null` |  |
| `session_count` | `integer \| null` |  |
| `monthly_spend` | `number \| null` |  |
| `user_count` | `integer \| null` |  |
| `tags` | `object \| any` |  |
| `segments` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |

</details>

#### Companies Get

Get a single company by ID

**Python SDK**

```python
await intercom.companies.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Company ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `company_id` | `string \| null` |  |
| `plan` | `object \| any` |  |
| `size` | `integer \| null` |  |
| `industry` | `string \| null` |  |
| `website` | `string \| null` |  |
| `remote_created_at` | `integer \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `last_request_at` | `integer \| null` |  |
| `session_count` | `integer \| null` |  |
| `monthly_spend` | `number \| null` |  |
| `user_count` | `integer \| null` |  |
| `tags` | `object \| any` |  |
| `segments` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


</details>

### Teams

#### Teams List

Returns a list of all teams in the workspace

**Python SDK**

```python
await intercom.teams.list()
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



<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `admin_ids` | `array<integer>` |  |
| `admin_priority_level` | `object \| any` |  |


</details>

#### Teams Get

Get a single team by ID

**Python SDK**

```python
await intercom.teams.get(
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Team ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `admin_ids` | `array<integer>` |  |
| `admin_priority_level` | `object \| any` |  |


</details>

### Admins

#### Admins List

Returns a list of all admins in the workspace

**Python SDK**

```python
await intercom.admins.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "admins",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `email_verified` | `boolean \| null` |  |
| `job_title` | `string \| null` |  |
| `away_mode_enabled` | `boolean \| null` |  |
| `away_mode_reassign` | `boolean \| null` |  |
| `has_inbox_seat` | `boolean \| null` |  |
| `team_ids` | `array<integer>` |  |
| `avatar` | `object \| any` |  |


</details>

#### Admins Get

Get a single admin by ID

**Python SDK**

```python
await intercom.admins.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "admins",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Admin ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `email_verified` | `boolean \| null` |  |
| `job_title` | `string \| null` |  |
| `away_mode_enabled` | `boolean \| null` |  |
| `away_mode_reassign` | `boolean \| null` |  |
| `has_inbox_seat` | `boolean \| null` |  |
| `team_ids` | `array<integer>` |  |
| `avatar` | `object \| any` |  |


</details>

### Tags

#### Tags List

Returns a list of all tags in the workspace

**Python SDK**

```python
await intercom.tags.list()
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



<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `applied_at` | `integer \| null` |  |
| `applied_by` | `object \| any` |  |


</details>

#### Tags Get

Get a single tag by ID

**Python SDK**

```python
await intercom.tags.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Tag ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `applied_at` | `integer \| null` |  |
| `applied_by` | `object \| any` |  |


</details>

### Segments

#### Segments List

Returns a list of all segments in the workspace

**Python SDK**

```python
await intercom.segments.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `include_count` | `boolean` | No | Include count of contacts in each segment |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `person_type` | `string \| null` |  |
| `count` | `integer \| null` |  |


</details>

#### Segments Get

Get a single segment by ID

**Python SDK**

```python
await intercom.segments.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Segment ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `person_type` | `string \| null` |  |
| `count` | `integer \| null` |  |


</details>



## Authentication

The Intercom connector supports the following authentication methods.


### Access Token Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Intercom API Access Token |

#### Example

**Python SDK**

```python
IntercomConnector(
  auth_config=IntercomAuthConfig(
    access_token="<Your Intercom API Access Token>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "d8313939-3782-41b0-be29-b3ca20d8dd3a",
  "auth_config": {
    "access_token": "<Your Intercom API Access Token>"
  },
  "name": "My Intercom Connector"
}'
```

