# Zendesk-Support full reference

This is the full reference documentation for the Zendesk-Support agent connector.

## Supported entities and actions

The Zendesk-Support connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Tickets | [List](#tickets-list), [Get](#tickets-get), [Search](#tickets-search) |
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Organizations | [List](#organizations-list), [Get](#organizations-get), [Search](#organizations-search) |
| Groups | [List](#groups-list), [Get](#groups-get), [Search](#groups-search) |
| Ticket Comments | [List](#ticket-comments-list), [Search](#ticket-comments-search) |
| Attachments | [Get](#attachments-get), [Download](#attachments-download) |
| Ticket Audits | [List](#ticket-audits-list), [List](#ticket-audits-list), [Search](#ticket-audits-search) |
| Ticket Metrics | [List](#ticket-metrics-list), [Search](#ticket-metrics-search) |
| Ticket Fields | [List](#ticket-fields-list), [Get](#ticket-fields-get), [Search](#ticket-fields-search) |
| Brands | [List](#brands-list), [Get](#brands-get), [Search](#brands-search) |
| Views | [List](#views-list), [Get](#views-get) |
| Macros | [List](#macros-list), [Get](#macros-get) |
| Triggers | [List](#triggers-list), [Get](#triggers-get) |
| Automations | [List](#automations-list), [Get](#automations-get) |
| Tags | [List](#tags-list), [Search](#tags-search) |
| Satisfaction Ratings | [List](#satisfaction-ratings-list), [Get](#satisfaction-ratings-get), [Search](#satisfaction-ratings-search) |
| Group Memberships | [List](#group-memberships-list) |
| Organization Memberships | [List](#organization-memberships-list) |
| Sla Policies | [List](#sla-policies-list), [Get](#sla-policies-get) |
| Ticket Forms | [List](#ticket-forms-list), [Get](#ticket-forms-get), [Search](#ticket-forms-search) |
| Articles | [List](#articles-list), [Get](#articles-get) |
| Article Attachments | [List](#article-attachments-list), [Get](#article-attachments-get), [Download](#article-attachments-download) |

## Tickets

### Tickets List

Returns a list of all tickets in your account

#### Python SDK

```python
await zendesk_support.tickets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `external_id` | `string` | No | Lists tickets by external id |
| `sort` | `"id" \| "status" \| "updated_at" \| "-id" \| "-status" \| "-updated_at"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Tickets Get

Returns a ticket by its ID

#### Python SDK

```python
await zendesk_support.tickets.get(
    ticket_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_id` | `integer` | Yes | The ID of the ticket |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Tickets Search

Search and filter tickets records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.tickets.search(
    query={"filter": {"eq": {"allow_attachments": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"allow_attachments": True}}}
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
| `allow_attachments` | `boolean` | Boolean indicating whether attachments are allowed on the ticket |
| `allow_channelback` | `boolean` | Boolean indicating whether agents can reply to the ticket through the original channel |
| `assignee_id` | `integer` | Unique identifier of the agent currently assigned to the ticket |
| `brand_id` | `integer` | Unique identifier of the brand associated with the ticket in multi-brand accounts |
| `collaborator_ids` | `array` | Array of user identifiers who are collaborating on the ticket |
| `created_at` | `string` | Timestamp indicating when the ticket was created |
| `custom_fields` | `array` | Array of custom field values specific to the account's ticket configuration |
| `custom_status_id` | `integer` | Unique identifier of the custom status applied to the ticket |
| `deleted_ticket_form_id` | `integer` | The ID of the ticket form that was previously associated with this ticket but has since been deleted |
| `description` | `string` | Initial description or content of the ticket when it was created |
| `due_at` | `string` | Timestamp indicating when the ticket is due for completion or resolution |
| `email_cc_ids` | `array` | Array of user identifiers who are CC'd on ticket email notifications |
| `external_id` | `string` | External identifier for the ticket, used for integrations with other systems |
| `fields` | `array` | Array of ticket field values including both system and custom fields |
| `follower_ids` | `array` | Array of user identifiers who are following the ticket for updates |
| `followup_ids` | `array` | Array of identifiers for follow-up tickets related to this ticket |
| `forum_topic_id` | `integer` | Unique identifier linking the ticket to a forum topic if applicable |
| `from_messaging_channel` | `boolean` | Boolean indicating whether the ticket originated from a messaging channel |
| `generated_timestamp` | `integer` | Timestamp updated for all ticket updates including system changes, used for incremental export |
| `group_id` | `integer` | Unique identifier of the agent group assigned to handle the ticket |
| `has_incidents` | `boolean` | Boolean indicating whether this problem ticket has related incident tickets |
| `id` | `integer` | Unique identifier for the ticket |
| `is_public` | `boolean` | Boolean indicating whether the ticket is publicly visible |
| `organization_id` | `integer` | Unique identifier of the organization associated with the ticket |
| `priority` | `string` | Priority level assigned to the ticket (e.g., urgent, high, normal, low) |
| `problem_id` | `integer` | Unique identifier of the problem ticket if this is an incident ticket |
| `raw_subject` | `string` | Original unprocessed subject line before any system modifications |
| `recipient` | `string` | Email address or identifier of the ticket recipient |
| `requester_id` | `integer` | Unique identifier of the user who requested or created the ticket |
| `satisfaction_rating` | `object | string` | Object containing customer satisfaction rating data for the ticket |
| `sharing_agreement_ids` | `array` | Array of sharing agreement identifiers if the ticket is shared across Zendesk instances |
| `status` | `string` | Current status of the ticket (e.g., new, open, pending, solved, closed) |
| `subject` | `string` | Subject line of the ticket describing the issue or request |
| `submitter_id` | `integer` | Unique identifier of the user who submitted the ticket on behalf of the requester |
| `tags` | `array` | Array of tags applied to the ticket for categorization and filtering |
| `ticket_form_id` | `integer` | Unique identifier of the ticket form used when creating the ticket |
| `type` | `string` | Type of ticket (e.g., problem, incident, question, task) |
| `updated_at` | `string` | Timestamp indicating when the ticket was last updated with a ticket event |
| `url` | `string` | API URL to access the full ticket resource |
| `via` | `object` | Object describing the channel and method through which the ticket was created |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.allow_attachments` | `boolean` | Boolean indicating whether attachments are allowed on the ticket |
| `hits[].data.allow_channelback` | `boolean` | Boolean indicating whether agents can reply to the ticket through the original channel |
| `hits[].data.assignee_id` | `integer` | Unique identifier of the agent currently assigned to the ticket |
| `hits[].data.brand_id` | `integer` | Unique identifier of the brand associated with the ticket in multi-brand accounts |
| `hits[].data.collaborator_ids` | `array` | Array of user identifiers who are collaborating on the ticket |
| `hits[].data.created_at` | `string` | Timestamp indicating when the ticket was created |
| `hits[].data.custom_fields` | `array` | Array of custom field values specific to the account's ticket configuration |
| `hits[].data.custom_status_id` | `integer` | Unique identifier of the custom status applied to the ticket |
| `hits[].data.deleted_ticket_form_id` | `integer` | The ID of the ticket form that was previously associated with this ticket but has since been deleted |
| `hits[].data.description` | `string` | Initial description or content of the ticket when it was created |
| `hits[].data.due_at` | `string` | Timestamp indicating when the ticket is due for completion or resolution |
| `hits[].data.email_cc_ids` | `array` | Array of user identifiers who are CC'd on ticket email notifications |
| `hits[].data.external_id` | `string` | External identifier for the ticket, used for integrations with other systems |
| `hits[].data.fields` | `array` | Array of ticket field values including both system and custom fields |
| `hits[].data.follower_ids` | `array` | Array of user identifiers who are following the ticket for updates |
| `hits[].data.followup_ids` | `array` | Array of identifiers for follow-up tickets related to this ticket |
| `hits[].data.forum_topic_id` | `integer` | Unique identifier linking the ticket to a forum topic if applicable |
| `hits[].data.from_messaging_channel` | `boolean` | Boolean indicating whether the ticket originated from a messaging channel |
| `hits[].data.generated_timestamp` | `integer` | Timestamp updated for all ticket updates including system changes, used for incremental export |
| `hits[].data.group_id` | `integer` | Unique identifier of the agent group assigned to handle the ticket |
| `hits[].data.has_incidents` | `boolean` | Boolean indicating whether this problem ticket has related incident tickets |
| `hits[].data.id` | `integer` | Unique identifier for the ticket |
| `hits[].data.is_public` | `boolean` | Boolean indicating whether the ticket is publicly visible |
| `hits[].data.organization_id` | `integer` | Unique identifier of the organization associated with the ticket |
| `hits[].data.priority` | `string` | Priority level assigned to the ticket (e.g., urgent, high, normal, low) |
| `hits[].data.problem_id` | `integer` | Unique identifier of the problem ticket if this is an incident ticket |
| `hits[].data.raw_subject` | `string` | Original unprocessed subject line before any system modifications |
| `hits[].data.recipient` | `string` | Email address or identifier of the ticket recipient |
| `hits[].data.requester_id` | `integer` | Unique identifier of the user who requested or created the ticket |
| `hits[].data.satisfaction_rating` | `object | string` | Object containing customer satisfaction rating data for the ticket |
| `hits[].data.sharing_agreement_ids` | `array` | Array of sharing agreement identifiers if the ticket is shared across Zendesk instances |
| `hits[].data.status` | `string` | Current status of the ticket (e.g., new, open, pending, solved, closed) |
| `hits[].data.subject` | `string` | Subject line of the ticket describing the issue or request |
| `hits[].data.submitter_id` | `integer` | Unique identifier of the user who submitted the ticket on behalf of the requester |
| `hits[].data.tags` | `array` | Array of tags applied to the ticket for categorization and filtering |
| `hits[].data.ticket_form_id` | `integer` | Unique identifier of the ticket form used when creating the ticket |
| `hits[].data.type` | `string` | Type of ticket (e.g., problem, incident, question, task) |
| `hits[].data.updated_at` | `string` | Timestamp indicating when the ticket was last updated with a ticket event |
| `hits[].data.url` | `string` | API URL to access the full ticket resource |
| `hits[].data.via` | `object` | Object describing the channel and method through which the ticket was created |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Users

### Users List

Returns a list of all users in your account

#### Python SDK

```python
await zendesk_support.users.list()
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
| `page` | `integer` | No | Page number for pagination |
| `role` | `"end-user" \| "agent" \| "admin"` | No | Filter by role |
| `external_id` | `string` | No | Filter by external id |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Users Get

Returns a user by their ID

#### Python SDK

```python
await zendesk_support.users.get(
    user_id=0
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
        "user_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_id` | `integer` | Yes | The ID of the user |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.users.search(
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
| `active` | `boolean` | Indicates if the user account is currently active |
| `alias` | `string` | Alternative name or nickname for the user |
| `chat_only` | `boolean` | Indicates if the user can only interact via chat |
| `created_at` | `string` | Timestamp indicating when the user was created |
| `custom_role_id` | `integer` | Identifier for a custom role assigned to the user |
| `default_group_id` | `integer` | Identifier of the default group assigned to the user |
| `details` | `string` | Additional descriptive information about the user |
| `email` | `string` | Email address of the user |
| `external_id` | `string` | External system identifier for the user, used for integrations |
| `iana_time_zone` | `string` | IANA standard time zone identifier for the user |
| `id` | `integer` | Unique identifier for the user |
| `last_login_at` | `string` | Timestamp of the user's most recent login |
| `locale` | `string` | Locale setting determining language and regional format preferences |
| `locale_id` | `integer` | Identifier for the user's locale preference |
| `moderator` | `boolean` | Indicates if the user has moderator privileges |
| `name` | `string` | Display name of the user |
| `notes` | `string` | Internal notes about the user, visible only to agents |
| `only_private_comments` | `boolean` | Indicates if the user can only make private comments on tickets |
| `organization_id` | `integer` | Identifier of the organization the user belongs to |
| `permanently_deleted` | `boolean` | Indicates if the user has been permanently deleted from the system |
| `phone` | `string` | Phone number of the user |
| `photo` | `object` | Profile photo or avatar of the user |
| `report_csv` | `boolean` | Indicates if the user receives reports in CSV format |
| `restricted_agent` | `boolean` | Indicates if the agent has restricted access permissions |
| `role` | `string` | Role assigned to the user defining their permissions level |
| `role_type` | `integer` | Type classification of the user's role |
| `shared` | `boolean` | Indicates if the user is shared across multiple accounts |
| `shared_agent` | `boolean` | Indicates if the user is a shared agent across multiple brands or accounts |
| `shared_phone_number` | `boolean` | Indicates if the phone number is shared with other users |
| `signature` | `string` | Email signature text for the user |
| `suspended` | `boolean` | Indicates if the user account is suspended |
| `tags` | `array` | Labels or tags associated with the user for categorization |
| `ticket_restriction` | `string` | Defines which tickets the user can access based on restrictions |
| `time_zone` | `string` | Time zone setting for the user |
| `two_factor_auth_enabled` | `boolean` | Indicates if two-factor authentication is enabled for the user |
| `updated_at` | `string` | Timestamp indicating when the user was last updated |
| `url` | `string` | API endpoint URL for accessing the user's detailed information |
| `user_fields` | `object` | Custom field values specific to the user, stored as key-value pairs |
| `verified` | `boolean` | Indicates if the user's identity has been verified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.active` | `boolean` | Indicates if the user account is currently active |
| `hits[].data.alias` | `string` | Alternative name or nickname for the user |
| `hits[].data.chat_only` | `boolean` | Indicates if the user can only interact via chat |
| `hits[].data.created_at` | `string` | Timestamp indicating when the user was created |
| `hits[].data.custom_role_id` | `integer` | Identifier for a custom role assigned to the user |
| `hits[].data.default_group_id` | `integer` | Identifier of the default group assigned to the user |
| `hits[].data.details` | `string` | Additional descriptive information about the user |
| `hits[].data.email` | `string` | Email address of the user |
| `hits[].data.external_id` | `string` | External system identifier for the user, used for integrations |
| `hits[].data.iana_time_zone` | `string` | IANA standard time zone identifier for the user |
| `hits[].data.id` | `integer` | Unique identifier for the user |
| `hits[].data.last_login_at` | `string` | Timestamp of the user's most recent login |
| `hits[].data.locale` | `string` | Locale setting determining language and regional format preferences |
| `hits[].data.locale_id` | `integer` | Identifier for the user's locale preference |
| `hits[].data.moderator` | `boolean` | Indicates if the user has moderator privileges |
| `hits[].data.name` | `string` | Display name of the user |
| `hits[].data.notes` | `string` | Internal notes about the user, visible only to agents |
| `hits[].data.only_private_comments` | `boolean` | Indicates if the user can only make private comments on tickets |
| `hits[].data.organization_id` | `integer` | Identifier of the organization the user belongs to |
| `hits[].data.permanently_deleted` | `boolean` | Indicates if the user has been permanently deleted from the system |
| `hits[].data.phone` | `string` | Phone number of the user |
| `hits[].data.photo` | `object` | Profile photo or avatar of the user |
| `hits[].data.report_csv` | `boolean` | Indicates if the user receives reports in CSV format |
| `hits[].data.restricted_agent` | `boolean` | Indicates if the agent has restricted access permissions |
| `hits[].data.role` | `string` | Role assigned to the user defining their permissions level |
| `hits[].data.role_type` | `integer` | Type classification of the user's role |
| `hits[].data.shared` | `boolean` | Indicates if the user is shared across multiple accounts |
| `hits[].data.shared_agent` | `boolean` | Indicates if the user is a shared agent across multiple brands or accounts |
| `hits[].data.shared_phone_number` | `boolean` | Indicates if the phone number is shared with other users |
| `hits[].data.signature` | `string` | Email signature text for the user |
| `hits[].data.suspended` | `boolean` | Indicates if the user account is suspended |
| `hits[].data.tags` | `array` | Labels or tags associated with the user for categorization |
| `hits[].data.ticket_restriction` | `string` | Defines which tickets the user can access based on restrictions |
| `hits[].data.time_zone` | `string` | Time zone setting for the user |
| `hits[].data.two_factor_auth_enabled` | `boolean` | Indicates if two-factor authentication is enabled for the user |
| `hits[].data.updated_at` | `string` | Timestamp indicating when the user was last updated |
| `hits[].data.url` | `string` | API endpoint URL for accessing the user's detailed information |
| `hits[].data.user_fields` | `object` | Custom field values specific to the user, stored as key-value pairs |
| `hits[].data.verified` | `boolean` | Indicates if the user's identity has been verified |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Organizations

### Organizations List

Returns a list of all organizations in your account

#### Python SDK

```python
await zendesk_support.organizations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Organizations Get

Returns an organization by its ID

#### Python SDK

```python
await zendesk_support.organizations.get(
    organization_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_id` | `integer` | Yes | The ID of the organization |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Organizations Search

Search and filter organizations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.organizations.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
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
| `created_at` | `string` | Timestamp when the organization was created |
| `deleted_at` | `string` | Timestamp when the organization was deleted |
| `details` | `string` | Details about the organization, such as the address |
| `domain_names` | `array` | Array of domain names associated with this organization for automatic user assignment |
| `external_id` | `string` | Unique external identifier to associate the organization to an external record (case-insensitive) |
| `group_id` | `integer` | ID of the group where new tickets from users in this organization are automatically assigned |
| `id` | `integer` | Unique identifier automatically assigned when the organization is created |
| `name` | `string` | Unique name for the organization (mandatory field) |
| `notes` | `string` | Notes about the organization |
| `organization_fields` | `object` | Key-value object for custom organization fields |
| `shared_comments` | `boolean` | Boolean indicating whether end users in this organization can comment on each other's tickets |
| `shared_tickets` | `boolean` | Boolean indicating whether end users in this organization can see each other's tickets |
| `tags` | `array` | Array of tags associated with the organization |
| `updated_at` | `string` | Timestamp of the last update to the organization |
| `url` | `string` | The API URL of this organization |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.created_at` | `string` | Timestamp when the organization was created |
| `hits[].data.deleted_at` | `string` | Timestamp when the organization was deleted |
| `hits[].data.details` | `string` | Details about the organization, such as the address |
| `hits[].data.domain_names` | `array` | Array of domain names associated with this organization for automatic user assignment |
| `hits[].data.external_id` | `string` | Unique external identifier to associate the organization to an external record (case-insensitive) |
| `hits[].data.group_id` | `integer` | ID of the group where new tickets from users in this organization are automatically assigned |
| `hits[].data.id` | `integer` | Unique identifier automatically assigned when the organization is created |
| `hits[].data.name` | `string` | Unique name for the organization (mandatory field) |
| `hits[].data.notes` | `string` | Notes about the organization |
| `hits[].data.organization_fields` | `object` | Key-value object for custom organization fields |
| `hits[].data.shared_comments` | `boolean` | Boolean indicating whether end users in this organization can comment on each other's tickets |
| `hits[].data.shared_tickets` | `boolean` | Boolean indicating whether end users in this organization can see each other's tickets |
| `hits[].data.tags` | `array` | Array of tags associated with the organization |
| `hits[].data.updated_at` | `string` | Timestamp of the last update to the organization |
| `hits[].data.url` | `string` | The API URL of this organization |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Groups

### Groups List

Returns a list of all groups in your account

#### Python SDK

```python
await zendesk_support.groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `exclude_deleted` | `boolean` | No | Exclude deleted groups |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Groups Get

Returns a group by its ID

#### Python SDK

```python
await zendesk_support.groups.get(
    group_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `integer` | Yes | The ID of the group |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Groups Search

Search and filter groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.groups.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
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
| `created_at` | `string` | Timestamp indicating when the group was created |
| `default` | `boolean` | Indicates if the group is the default one for the account |
| `deleted` | `boolean` | Indicates whether the group has been deleted |
| `description` | `string` | The description of the group |
| `id` | `integer` | Unique identifier automatically assigned when creating groups |
| `is_public` | `boolean` | Indicates if the group is public (true) or private (false) |
| `name` | `string` | The name of the group |
| `updated_at` | `string` | Timestamp indicating when the group was last updated |
| `url` | `string` | The API URL of the group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.created_at` | `string` | Timestamp indicating when the group was created |
| `hits[].data.default` | `boolean` | Indicates if the group is the default one for the account |
| `hits[].data.deleted` | `boolean` | Indicates whether the group has been deleted |
| `hits[].data.description` | `string` | The description of the group |
| `hits[].data.id` | `integer` | Unique identifier automatically assigned when creating groups |
| `hits[].data.is_public` | `boolean` | Indicates if the group is public (true) or private (false) |
| `hits[].data.name` | `string` | The name of the group |
| `hits[].data.updated_at` | `string` | Timestamp indicating when the group was last updated |
| `hits[].data.url` | `string` | The API URL of the group |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ticket Comments

### Ticket Comments List

Returns a list of comments for a specific ticket

#### Python SDK

```python
await zendesk_support.ticket_comments.list(
    ticket_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_id` | `integer` | Yes | The ID of the ticket |
| `page` | `integer` | No | Page number for pagination |
| `include_inline_images` | `boolean` | No | Include inline images in the response |
| `sort` | `"created_at" \| "-created_at"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Comments Search

Search and filter ticket comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.ticket_comments.search(
    query={"filter": {"eq": {"attachments": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_comments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attachments": []}}}
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
| `attachments` | `array` | List of files or media attached to the comment |
| `audit_id` | `integer` | Identifier of the audit record associated with this comment event |
| `author_id` | `integer` | Identifier of the user who created the comment |
| `body` | `string` | Content of the comment in its original format |
| `created_at` | `string` | Timestamp when the comment was created |
| `event_type` | `string` | Specific classification of the event within the ticket event stream |
| `html_body` | `string` | HTML-formatted content of the comment |
| `id` | `integer` | Unique identifier for the comment event |
| `metadata` | `object` | Additional structured information about the comment not covered by standard fields |
| `plain_body` | `string` | Plain text content of the comment without formatting |
| `public` | `boolean` | Boolean indicating whether the comment is visible to end users or is an internal note |
| `ticket_id` | `integer` | Identifier of the ticket to which this comment belongs |
| `timestamp` | `integer` | Timestamp of when the event occurred in the incremental export stream |
| `type` | `string` | Type of event, typically indicating this is a comment event |
| `uploads` | `array` | Array of upload tokens or identifiers for files being attached to the comment |
| `via` | `object` | Channel or method through which the comment was submitted |
| `via_reference_id` | `integer` | Reference identifier for the channel through which the comment was created |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attachments` | `array` | List of files or media attached to the comment |
| `hits[].data.audit_id` | `integer` | Identifier of the audit record associated with this comment event |
| `hits[].data.author_id` | `integer` | Identifier of the user who created the comment |
| `hits[].data.body` | `string` | Content of the comment in its original format |
| `hits[].data.created_at` | `string` | Timestamp when the comment was created |
| `hits[].data.event_type` | `string` | Specific classification of the event within the ticket event stream |
| `hits[].data.html_body` | `string` | HTML-formatted content of the comment |
| `hits[].data.id` | `integer` | Unique identifier for the comment event |
| `hits[].data.metadata` | `object` | Additional structured information about the comment not covered by standard fields |
| `hits[].data.plain_body` | `string` | Plain text content of the comment without formatting |
| `hits[].data.public` | `boolean` | Boolean indicating whether the comment is visible to end users or is an internal note |
| `hits[].data.ticket_id` | `integer` | Identifier of the ticket to which this comment belongs |
| `hits[].data.timestamp` | `integer` | Timestamp of when the event occurred in the incremental export stream |
| `hits[].data.type` | `string` | Type of event, typically indicating this is a comment event |
| `hits[].data.uploads` | `array` | Array of upload tokens or identifiers for files being attached to the comment |
| `hits[].data.via` | `object` | Channel or method through which the comment was submitted |
| `hits[].data.via_reference_id` | `integer` | Reference identifier for the channel through which the comment was created |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Attachments

### Attachments Get

Returns an attachment by its ID

#### Python SDK

```python
await zendesk_support.attachments.get(
    attachment_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_id` | `integer` | Yes | The ID of the attachment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Attachments Download

Downloads the file content of a ticket attachment

#### Python SDK

```python
async for chunk in zendesk_support.attachments.download(    attachment_id=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `attachment_id` | `integer` | Yes | The ID of the attachment |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


## Ticket Audits

### Ticket Audits List

Returns a list of all ticket audits

#### Python SDK

```python
await zendesk_support.ticket_audits.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_audits",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `ticket_id` | `integer` |  |
| `author_id` | `integer` |  |
| `metadata` | `object` |  |
| `via` | `object` |  |
| `events` | `array<object>` |  |
| `created_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Audits List

Returns a list of audits for a specific ticket

#### Python SDK

```python
await zendesk_support.ticket_audits.list(
    ticket_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_id` | `integer` | Yes | The ID of the ticket |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `ticket_id` | `integer` |  |
| `author_id` | `integer` |  |
| `metadata` | `object` |  |
| `via` | `object` |  |
| `events` | `array<object>` |  |
| `created_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Audits Search

Search and filter ticket audits records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.ticket_audits.search(
    query={"filter": {"eq": {"attachments": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_audits",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attachments": []}}}
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
| `attachments` | `array` | Files or documents attached to the audit |
| `author_id` | `integer` | The unique identifier of the user who created the audit |
| `created_at` | `string` | Timestamp indicating when the audit was created |
| `events` | `array` | Array of events that occurred in this audit, such as field changes, comments, or tag updates |
| `id` | `integer` | Unique identifier for the audit record, automatically assigned when the audit is created |
| `metadata` | `object` | Custom and system data associated with the audit |
| `ticket_id` | `integer` | The unique identifier of the ticket associated with this audit |
| `via` | `object` | Describes how the audit was created, providing context about the creation source |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attachments` | `array` | Files or documents attached to the audit |
| `hits[].data.author_id` | `integer` | The unique identifier of the user who created the audit |
| `hits[].data.created_at` | `string` | Timestamp indicating when the audit was created |
| `hits[].data.events` | `array` | Array of events that occurred in this audit, such as field changes, comments, or tag updates |
| `hits[].data.id` | `integer` | Unique identifier for the audit record, automatically assigned when the audit is created |
| `hits[].data.metadata` | `object` | Custom and system data associated with the audit |
| `hits[].data.ticket_id` | `integer` | The unique identifier of the ticket associated with this audit |
| `hits[].data.via` | `object` | Describes how the audit was created, providing context about the creation source |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ticket Metrics

### Ticket Metrics List

Returns a list of all ticket metrics

#### Python SDK

```python
await zendesk_support.ticket_metrics.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_metrics",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Metrics Search

Search and filter ticket metrics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.ticket_metrics.search(
    query={"filter": {"eq": {"agent_wait_time_in_minutes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_metrics",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"agent_wait_time_in_minutes": {}}}}
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
| `agent_wait_time_in_minutes` | `object` | Number of minutes the agent spent waiting during calendar and business hours |
| `assigned_at` | `string` | Timestamp when the ticket was assigned |
| `assignee_stations` | `integer` | Number of assignees the ticket had |
| `assignee_updated_at` | `string` | Timestamp when the assignee last updated the ticket |
| `created_at` | `string` | Timestamp when the metric record was created |
| `custom_status_updated_at` | `string` | Timestamp when the ticket's custom status was last updated |
| `first_resolution_time_in_minutes` | `object` | Number of minutes to the first resolution time during calendar and business hours |
| `full_resolution_time_in_minutes` | `object` | Number of minutes to the full resolution during calendar and business hours |
| `generated_timestamp` | `integer` | Timestamp of when record was last updated |
| `group_stations` | `integer` | Number of groups the ticket passed through |
| `id` | `integer` | Unique identifier for the ticket metric record |
| `initially_assigned_at` | `string` | Timestamp when the ticket was initially assigned |
| `instance_id` | `integer` | ID of the Zendesk instance associated with the ticket |
| `latest_comment_added_at` | `string` | Timestamp when the latest comment was added |
| `metric` | `string` | Ticket metrics data |
| `on_hold_time_in_minutes` | `object` | Number of minutes on hold |
| `reopens` | `integer` | Total number of times the ticket was reopened |
| `replies` | `integer` | The number of public replies added to a ticket by an agent |
| `reply_time_in_minutes` | `object` | Number of minutes to the first reply during calendar and business hours |
| `reply_time_in_seconds` | `object` | Number of seconds to the first reply during calendar hours, only available for Messaging tickets |
| `requester_updated_at` | `string` | Timestamp when the requester last updated the ticket |
| `requester_wait_time_in_minutes` | `object` | Number of minutes the requester spent waiting during calendar and business hours |
| `solved_at` | `string` | Timestamp when the ticket was solved |
| `status` | `object` | The current status of the ticket (open, pending, solved, etc.). |
| `status_updated_at` | `string` | Timestamp when the status of the ticket was last updated |
| `ticket_id` | `integer` | Identifier of the associated ticket |
| `time` | `string` | Time related to the ticket |
| `type` | `string` | Type of ticket |
| `updated_at` | `string` | Timestamp when the metric record was last updated |
| `url` | `string` | The API url of the ticket metric |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.agent_wait_time_in_minutes` | `object` | Number of minutes the agent spent waiting during calendar and business hours |
| `hits[].data.assigned_at` | `string` | Timestamp when the ticket was assigned |
| `hits[].data.assignee_stations` | `integer` | Number of assignees the ticket had |
| `hits[].data.assignee_updated_at` | `string` | Timestamp when the assignee last updated the ticket |
| `hits[].data.created_at` | `string` | Timestamp when the metric record was created |
| `hits[].data.custom_status_updated_at` | `string` | Timestamp when the ticket's custom status was last updated |
| `hits[].data.first_resolution_time_in_minutes` | `object` | Number of minutes to the first resolution time during calendar and business hours |
| `hits[].data.full_resolution_time_in_minutes` | `object` | Number of minutes to the full resolution during calendar and business hours |
| `hits[].data.generated_timestamp` | `integer` | Timestamp of when record was last updated |
| `hits[].data.group_stations` | `integer` | Number of groups the ticket passed through |
| `hits[].data.id` | `integer` | Unique identifier for the ticket metric record |
| `hits[].data.initially_assigned_at` | `string` | Timestamp when the ticket was initially assigned |
| `hits[].data.instance_id` | `integer` | ID of the Zendesk instance associated with the ticket |
| `hits[].data.latest_comment_added_at` | `string` | Timestamp when the latest comment was added |
| `hits[].data.metric` | `string` | Ticket metrics data |
| `hits[].data.on_hold_time_in_minutes` | `object` | Number of minutes on hold |
| `hits[].data.reopens` | `integer` | Total number of times the ticket was reopened |
| `hits[].data.replies` | `integer` | The number of public replies added to a ticket by an agent |
| `hits[].data.reply_time_in_minutes` | `object` | Number of minutes to the first reply during calendar and business hours |
| `hits[].data.reply_time_in_seconds` | `object` | Number of seconds to the first reply during calendar hours, only available for Messaging tickets |
| `hits[].data.requester_updated_at` | `string` | Timestamp when the requester last updated the ticket |
| `hits[].data.requester_wait_time_in_minutes` | `object` | Number of minutes the requester spent waiting during calendar and business hours |
| `hits[].data.solved_at` | `string` | Timestamp when the ticket was solved |
| `hits[].data.status` | `object` | The current status of the ticket (open, pending, solved, etc.). |
| `hits[].data.status_updated_at` | `string` | Timestamp when the status of the ticket was last updated |
| `hits[].data.ticket_id` | `integer` | Identifier of the associated ticket |
| `hits[].data.time` | `string` | Time related to the ticket |
| `hits[].data.type` | `string` | Type of ticket |
| `hits[].data.updated_at` | `string` | Timestamp when the metric record was last updated |
| `hits[].data.url` | `string` | The API url of the ticket metric |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ticket Fields

### Ticket Fields List

Returns a list of all ticket fields

#### Python SDK

```python
await zendesk_support.ticket_fields.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_fields",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `locale` | `string` | No | Locale for the results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Fields Get

Returns a ticket field by its ID

#### Python SDK

```python
await zendesk_support.ticket_fields.get(
    ticket_field_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_field_id` | `integer` | Yes | The ID of the ticket field |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Ticket Fields Search

Search and filter ticket fields records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.ticket_fields.search(
    query={"filter": {"eq": {"active": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_fields",
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
| `active` | `boolean` | Whether this field is currently available for use |
| `agent_description` | `string` | A description of the ticket field that only agents can see |
| `collapsed_for_agents` | `boolean` | If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields |
| `created_at` | `string` | Timestamp when the custom ticket field was created |
| `custom_field_options` | `array` | Array of option objects for custom ticket fields of type multiselect or tagger |
| `custom_statuses` | `array` | List of customized ticket statuses, only present for system ticket fields of type custom_status |
| `description` | `string` | Text describing the purpose of the ticket field to users |
| `editable_in_portal` | `boolean` | Whether this field is editable by end users in Help Center |
| `id` | `integer` | Unique identifier for the ticket field, automatically assigned when created |
| `key` | `string` | Internal identifier or reference key for the field |
| `position` | `integer` | The relative position of the ticket field on a ticket, controlling display order |
| `raw_description` | `string` | The dynamic content placeholder if present, or the description value if not |
| `raw_title` | `string` | The dynamic content placeholder if present, or the title value if not |
| `raw_title_in_portal` | `string` | The dynamic content placeholder if present, or the title_in_portal value if not |
| `regexp_for_validation` | `string` | For regexp fields only, the validation pattern for a field value to be deemed valid |
| `removable` | `boolean` | If false, this field is a system field that must be present on all tickets |
| `required` | `boolean` | If true, agents must enter a value in the field to change the ticket status to solved |
| `required_in_portal` | `boolean` | If true, end users must enter a value in the field to create a request |
| `sub_type_id` | `integer` | For system ticket fields of type priority and status, controlling available options |
| `system_field_options` | `array` | Array of options for system ticket fields of type tickettype, priority, or status |
| `tag` | `string` | For checkbox fields only, a tag added to tickets when the checkbox field is selected |
| `title` | `string` | The title of the ticket field displayed to agents |
| `title_in_portal` | `string` | The title of the ticket field displayed to end users in Help Center |
| `type` | `string` | Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger |
| `updated_at` | `string` | Timestamp when the custom ticket field was last updated |
| `url` | `string` | The API URL for this ticket field resource |
| `visible_in_portal` | `boolean` | Whether this field is visible to end users in Help Center |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.active` | `boolean` | Whether this field is currently available for use |
| `hits[].data.agent_description` | `string` | A description of the ticket field that only agents can see |
| `hits[].data.collapsed_for_agents` | `boolean` | If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields |
| `hits[].data.created_at` | `string` | Timestamp when the custom ticket field was created |
| `hits[].data.custom_field_options` | `array` | Array of option objects for custom ticket fields of type multiselect or tagger |
| `hits[].data.custom_statuses` | `array` | List of customized ticket statuses, only present for system ticket fields of type custom_status |
| `hits[].data.description` | `string` | Text describing the purpose of the ticket field to users |
| `hits[].data.editable_in_portal` | `boolean` | Whether this field is editable by end users in Help Center |
| `hits[].data.id` | `integer` | Unique identifier for the ticket field, automatically assigned when created |
| `hits[].data.key` | `string` | Internal identifier or reference key for the field |
| `hits[].data.position` | `integer` | The relative position of the ticket field on a ticket, controlling display order |
| `hits[].data.raw_description` | `string` | The dynamic content placeholder if present, or the description value if not |
| `hits[].data.raw_title` | `string` | The dynamic content placeholder if present, or the title value if not |
| `hits[].data.raw_title_in_portal` | `string` | The dynamic content placeholder if present, or the title_in_portal value if not |
| `hits[].data.regexp_for_validation` | `string` | For regexp fields only, the validation pattern for a field value to be deemed valid |
| `hits[].data.removable` | `boolean` | If false, this field is a system field that must be present on all tickets |
| `hits[].data.required` | `boolean` | If true, agents must enter a value in the field to change the ticket status to solved |
| `hits[].data.required_in_portal` | `boolean` | If true, end users must enter a value in the field to create a request |
| `hits[].data.sub_type_id` | `integer` | For system ticket fields of type priority and status, controlling available options |
| `hits[].data.system_field_options` | `array` | Array of options for system ticket fields of type tickettype, priority, or status |
| `hits[].data.tag` | `string` | For checkbox fields only, a tag added to tickets when the checkbox field is selected |
| `hits[].data.title` | `string` | The title of the ticket field displayed to agents |
| `hits[].data.title_in_portal` | `string` | The title of the ticket field displayed to end users in Help Center |
| `hits[].data.type` | `string` | Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger |
| `hits[].data.updated_at` | `string` | Timestamp when the custom ticket field was last updated |
| `hits[].data.url` | `string` | The API URL for this ticket field resource |
| `hits[].data.visible_in_portal` | `boolean` | Whether this field is visible to end users in Help Center |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Brands

### Brands List

Returns a list of all brands for the account

#### Python SDK

```python
await zendesk_support.brands.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "brands",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Brands Get

Returns a brand by its ID

#### Python SDK

```python
await zendesk_support.brands.get(
    brand_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `brand_id` | `integer` | Yes | The ID of the brand |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Brands Search

Search and filter brands records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.brands.search(
    query={"filter": {"eq": {"active": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "brands",
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
| `active` | `boolean` | Indicates whether the brand is set as active |
| `brand_url` | `string` | The public URL of the brand |
| `created_at` | `string` | Timestamp when the brand was created |
| `default` | `boolean` | Indicates whether the brand is the default brand for tickets generated from non-branded channels |
| `has_help_center` | `boolean` | Indicates whether the brand has a Help Center enabled |
| `help_center_state` | `string` | The state of the Help Center, with allowed values of enabled, disabled, or restricted |
| `host_mapping` | `string` | The host mapping configuration for the brand, visible only to administrators |
| `id` | `integer` | Unique identifier automatically assigned when the brand is created |
| `is_deleted` | `boolean` | Indicates whether the brand has been deleted |
| `logo` | `string` | Brand logo image file represented as an Attachment object |
| `name` | `string` | The name of the brand |
| `signature_template` | `string` | The signature template used for the brand |
| `subdomain` | `string` | The subdomain associated with the brand |
| `ticket_form_ids` | `array` | Array of ticket form IDs that are available for use by this brand |
| `updated_at` | `string` | Timestamp when the brand was last updated |
| `url` | `string` | The API URL for accessing this brand resource |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.active` | `boolean` | Indicates whether the brand is set as active |
| `hits[].data.brand_url` | `string` | The public URL of the brand |
| `hits[].data.created_at` | `string` | Timestamp when the brand was created |
| `hits[].data.default` | `boolean` | Indicates whether the brand is the default brand for tickets generated from non-branded channels |
| `hits[].data.has_help_center` | `boolean` | Indicates whether the brand has a Help Center enabled |
| `hits[].data.help_center_state` | `string` | The state of the Help Center, with allowed values of enabled, disabled, or restricted |
| `hits[].data.host_mapping` | `string` | The host mapping configuration for the brand, visible only to administrators |
| `hits[].data.id` | `integer` | Unique identifier automatically assigned when the brand is created |
| `hits[].data.is_deleted` | `boolean` | Indicates whether the brand has been deleted |
| `hits[].data.logo` | `string` | Brand logo image file represented as an Attachment object |
| `hits[].data.name` | `string` | The name of the brand |
| `hits[].data.signature_template` | `string` | The signature template used for the brand |
| `hits[].data.subdomain` | `string` | The subdomain associated with the brand |
| `hits[].data.ticket_form_ids` | `array` | Array of ticket form IDs that are available for use by this brand |
| `hits[].data.updated_at` | `string` | Timestamp when the brand was last updated |
| `hits[].data.url` | `string` | The API URL for accessing this brand resource |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Views

### Views List

Returns a list of all views for the account

#### Python SDK

```python
await zendesk_support.views.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "views",
    "action": "list"
}'
```


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Views Get

Returns a view by its ID

#### Python SDK

```python
await zendesk_support.views.get(
    view_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `view_id` | `integer` | Yes | The ID of the view |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Macros

### Macros List

Returns a list of all macros for the account

#### Python SDK

```python
await zendesk_support.macros.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "macros",
    "action": "list"
}'
```


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Macros Get

Returns a macro by its ID

#### Python SDK

```python
await zendesk_support.macros.get(
    macro_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `macro_id` | `integer` | Yes | The ID of the macro |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Triggers

### Triggers List

Returns a list of all triggers for the account

#### Python SDK

```python
await zendesk_support.triggers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "triggers",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `active` | `boolean` | No | Filter by active status |
| `category_id` | `string` | No | Filter by category ID |
| `sort` | `"alphabetical" \| "created_at" \| "updated_at" \| "position"` | No | Sort results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Triggers Get

Returns a trigger by its ID

#### Python SDK

```python
await zendesk_support.triggers.get(
    trigger_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `trigger_id` | `integer` | Yes | The ID of the trigger |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Automations

### Automations List

Returns a list of all automations for the account

#### Python SDK

```python
await zendesk_support.automations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "automations",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `active` | `boolean` | No | Filter by active status |
| `sort` | `"alphabetical" \| "created_at" \| "updated_at" \| "position"` | No | Sort results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Automations Get

Returns an automation by its ID

#### Python SDK

```python
await zendesk_support.automations.get(
    automation_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `automation_id` | `integer` | Yes | The ID of the automation |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Tags

### Tags List

Returns a list of all tags used in the account

#### Python SDK

```python
await zendesk_support.tags.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `count` | `integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Tags Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.tags.search(
    query={"filter": {"eq": {"count": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"count": 0}}}
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
| `count` | `integer` | The number of times this tag has been used across resources |
| `name` | `string` | The tag name string used to label and categorize resources |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.count` | `integer` | The number of times this tag has been used across resources |
| `hits[].data.name` | `string` | The tag name string used to label and categorize resources |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Satisfaction Ratings

### Satisfaction Ratings List

Returns a list of all satisfaction ratings

#### Python SDK

```python
await zendesk_support.satisfaction_ratings.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "satisfaction_ratings",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `score` | `"offered" \| "unoffered" \| "received" \| "good" \| "bad"` | No | Filter by score |
| `start_time` | `integer` | No | Start time (Unix epoch) |
| `end_time` | `integer` | No | End time (Unix epoch) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Satisfaction Ratings Get

Returns a satisfaction rating by its ID

#### Python SDK

```python
await zendesk_support.satisfaction_ratings.get(
    satisfaction_rating_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `satisfaction_rating_id` | `integer` | Yes | The ID of the satisfaction rating |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Satisfaction Ratings Search

Search and filter satisfaction ratings records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.satisfaction_ratings.search(
    query={"filter": {"eq": {"assignee_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "satisfaction_ratings",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"assignee_id": 0}}}
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
| `assignee_id` | `integer` | The identifier of the agent assigned to the ticket at the time the rating was submitted |
| `comment` | `string` | Optional comment provided by the requester with the rating |
| `created_at` | `string` | Timestamp indicating when the satisfaction rating was created |
| `group_id` | `integer` | The identifier of the group assigned to the ticket at the time the rating was submitted |
| `id` | `integer` | Unique identifier for the satisfaction rating, automatically assigned upon creation |
| `reason` | `string` | Free-text reason for a bad rating provided by the requester in a follow-up question |
| `reason_id` | `integer` | Identifier for the predefined reason given for a negative rating |
| `requester_id` | `integer` | The identifier of the ticket requester who submitted the satisfaction rating |
| `score` | `string` | The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad' |
| `ticket_id` | `integer` | The identifier of the ticket being rated |
| `updated_at` | `string` | Timestamp indicating when the satisfaction rating was last updated |
| `url` | `string` | The API URL of this satisfaction rating resource |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.assignee_id` | `integer` | The identifier of the agent assigned to the ticket at the time the rating was submitted |
| `hits[].data.comment` | `string` | Optional comment provided by the requester with the rating |
| `hits[].data.created_at` | `string` | Timestamp indicating when the satisfaction rating was created |
| `hits[].data.group_id` | `integer` | The identifier of the group assigned to the ticket at the time the rating was submitted |
| `hits[].data.id` | `integer` | Unique identifier for the satisfaction rating, automatically assigned upon creation |
| `hits[].data.reason` | `string` | Free-text reason for a bad rating provided by the requester in a follow-up question |
| `hits[].data.reason_id` | `integer` | Identifier for the predefined reason given for a negative rating |
| `hits[].data.requester_id` | `integer` | The identifier of the ticket requester who submitted the satisfaction rating |
| `hits[].data.score` | `string` | The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad' |
| `hits[].data.ticket_id` | `integer` | The identifier of the ticket being rated |
| `hits[].data.updated_at` | `string` | Timestamp indicating when the satisfaction rating was last updated |
| `hits[].data.url` | `string` | The API URL of this satisfaction rating resource |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Group Memberships

### Group Memberships List

Returns a list of all group memberships

#### Python SDK

```python
await zendesk_support.group_memberships.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_memberships",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `url` | `string` |  |
| `user_id` | `integer` |  |
| `group_id` | `integer` |  |
| `default` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

## Organization Memberships

### Organization Memberships List

Returns a list of all organization memberships

#### Python SDK

```python
await zendesk_support.organization_memberships.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organization_memberships",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

## Sla Policies

### Sla Policies List

Returns a list of all SLA policies

#### Python SDK

```python
await zendesk_support.sla_policies.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sla_policies",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Sla Policies Get

Returns an SLA policy by its ID

#### Python SDK

```python
await zendesk_support.sla_policies.get(
    sla_policy_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sla_policy_id` | `integer` | Yes | The ID of the SLA policy |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Ticket Forms

### Ticket Forms List

Returns a list of all ticket forms for the account

#### Python SDK

```python
await zendesk_support.ticket_forms.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `page` | `integer` | No | Page number for pagination |
| `active` | `boolean` | No | Filter by active status |
| `end_user_visible` | `boolean` | No | Filter by end user visibility |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Ticket Forms Get

Returns a ticket form by its ID

#### Python SDK

```python
await zendesk_support.ticket_forms.get(
    ticket_form_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ticket_form_id` | `integer` | Yes | The ID of the ticket form |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Ticket Forms Search

Search and filter ticket forms records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_support.ticket_forms.search(
    query={"filter": {"eq": {"active": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ticket_forms",
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
| `active` | `boolean` | Indicates if the form is set as active |
| `agent_conditions` | `array` | Array of condition sets for agent workspaces |
| `created_at` | `string` | Timestamp when the ticket form was created |
| `default` | `boolean` | Indicates if the form is the default form for this account |
| `display_name` | `string` | The name of the form that is displayed to an end user |
| `end_user_conditions` | `array` | Array of condition sets for end user products |
| `end_user_visible` | `boolean` | Indicates if the form is visible to the end user |
| `id` | `integer` | Unique identifier for the ticket form, automatically assigned when creating the form |
| `in_all_brands` | `boolean` | Indicates if the form is available for use in all brands on this account |
| `name` | `string` | The name of the ticket form |
| `position` | `integer` | The position of this form among other forms in the account, such as in a dropdown |
| `raw_display_name` | `string` | The dynamic content placeholder if present, or the display_name value if not |
| `raw_name` | `string` | The dynamic content placeholder if present, or the name value if not |
| `restricted_brand_ids` | `array` | IDs of all brands that this ticket form is restricted to |
| `ticket_field_ids` | `array` | IDs of all ticket fields included in this ticket form |
| `updated_at` | `string` | Timestamp of the last update to the ticket form |
| `url` | `string` | URL of the ticket form |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.active` | `boolean` | Indicates if the form is set as active |
| `hits[].data.agent_conditions` | `array` | Array of condition sets for agent workspaces |
| `hits[].data.created_at` | `string` | Timestamp when the ticket form was created |
| `hits[].data.default` | `boolean` | Indicates if the form is the default form for this account |
| `hits[].data.display_name` | `string` | The name of the form that is displayed to an end user |
| `hits[].data.end_user_conditions` | `array` | Array of condition sets for end user products |
| `hits[].data.end_user_visible` | `boolean` | Indicates if the form is visible to the end user |
| `hits[].data.id` | `integer` | Unique identifier for the ticket form, automatically assigned when creating the form |
| `hits[].data.in_all_brands` | `boolean` | Indicates if the form is available for use in all brands on this account |
| `hits[].data.name` | `string` | The name of the ticket form |
| `hits[].data.position` | `integer` | The position of this form among other forms in the account, such as in a dropdown |
| `hits[].data.raw_display_name` | `string` | The dynamic content placeholder if present, or the display_name value if not |
| `hits[].data.raw_name` | `string` | The dynamic content placeholder if present, or the name value if not |
| `hits[].data.restricted_brand_ids` | `array` | IDs of all brands that this ticket form is restricted to |
| `hits[].data.ticket_field_ids` | `array` | IDs of all ticket fields included in this ticket form |
| `hits[].data.updated_at` | `string` | Timestamp of the last update to the ticket form |
| `hits[].data.url` | `string` | URL of the ticket form |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Articles

### Articles List

Returns a list of all articles in the Help Center

#### Python SDK

```python
await zendesk_support.articles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "articles",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `sort_by` | `"created_at" \| "updated_at" \| "title" \| "position"` | No | Sort articles by field |
| `sort_order` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Articles Get

Retrieves the details of a specific article

#### Python SDK

```python
await zendesk_support.articles.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | The unique ID of the article |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Article Attachments

### Article Attachments List

Returns a list of all attachments for a specific article

#### Python SDK

```python
await zendesk_support.article_attachments.list(
    article_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `article_id` | `integer` | Yes | The unique ID of the article |
| `page` | `integer` | No | Page number for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |
| `previous_page` | `string \| null` |  |
| `count` | `integer` |  |

</details>

### Article Attachments Get

Retrieves the metadata of a specific attachment for a specific article

#### Python SDK

```python
await zendesk_support.article_attachments.get(
    article_id=0,
    attachment_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `article_id` | `integer` | Yes | The unique ID of the article |
| `attachment_id` | `integer` | Yes | The unique ID of the attachment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Article Attachments Download

Downloads the file content of a specific attachment

#### Python SDK

```python
async for chunk in zendesk_support.article_attachments.download(    article_id=0,    attachment_id=0):# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `article_id` | `integer` | Yes | The unique ID of the article |
| `attachment_id` | `integer` | Yes | The unique ID of the attachment |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


