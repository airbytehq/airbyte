# Freshdesk full reference

This is the full reference documentation for the Freshdesk agent connector.

## Supported entities and actions

The Freshdesk connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Tickets | [List](#tickets-list), [Get](#tickets-get), [Search](#tickets-search) |
| Contacts | [List](#contacts-list), [Get](#contacts-get) |
| Agents | [List](#agents-list), [Get](#agents-get), [Search](#agents-search) |
| Groups | [List](#groups-list), [Get](#groups-get), [Search](#groups-search) |
| Companies | [List](#companies-list), [Get](#companies-get) |
| Roles | [List](#roles-list), [Get](#roles-get) |
| Satisfaction Ratings | [List](#satisfaction-ratings-list) |
| Surveys | [List](#surveys-list) |
| Time Entries | [List](#time-entries-list) |
| Ticket Fields | [List](#ticket-fields-list) |

## Tickets

### Tickets List

Returns a paginated list of tickets. By default returns tickets created in the past 30 days. Use updated_since to get older tickets.

#### Python SDK

```python
await freshdesk.tickets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |
| `updated_since` | `string` | No | Return tickets updated since this timestamp (ISO 8601) |
| `order_by` | `"created_at" \| "due_by" \| "updated_at" \| "status"` | No | Sort field |
| `order_type` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `subject` | `null \| string` |  |
| `description` | `null \| string` |  |
| `description_text` | `null \| string` |  |
| `status` | `null \| integer` |  |
| `priority` | `null \| integer` |  |
| `source` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `requester_id` | `null \| integer` |  |
| `responder_id` | `null \| integer` |  |
| `company_id` | `null \| integer` |  |
| `group_id` | `null \| integer` |  |
| `product_id` | `null \| integer` |  |
| `email_config_id` | `null \| integer` |  |
| `cc_emails` | `null \| array` |  |
| `fwd_emails` | `null \| array` |  |
| `reply_cc_emails` | `null \| array` |  |
| `to_emails` | `null \| array` |  |
| `spam` | `null \| boolean` |  |
| `deleted` | `null \| boolean` |  |
| `fr_escalated` | `null \| boolean` |  |
| `is_escalated` | `null \| boolean` |  |
| `fr_due_by` | `null \| string` |  |
| `due_by` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `custom_fields` | `null \| object` |  |
| `attachments` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `association_type` | `null \| integer` |  |
| `associated_tickets_count` | `null \| integer` |  |
| `ticket_cc_emails` | `null \| array` |  |
| `ticket_bcc_emails` | `null \| array` |  |
| `support_email` | `null \| string` |  |
| `source_additional_info` | `null \| object` |  |
| `structured_description` | `null \| object` |  |
| `form_id` | `null \| integer` |  |
| `nr_due_by` | `null \| string` |  |
| `nr_escalated` | `null \| boolean` |  |


</details>

### Tickets Get

Get a single ticket by ID

#### Python SDK

```python
await freshdesk.tickets.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Ticket ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `subject` | `null \| string` |  |
| `description` | `null \| string` |  |
| `description_text` | `null \| string` |  |
| `status` | `null \| integer` |  |
| `priority` | `null \| integer` |  |
| `source` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `requester_id` | `null \| integer` |  |
| `responder_id` | `null \| integer` |  |
| `company_id` | `null \| integer` |  |
| `group_id` | `null \| integer` |  |
| `product_id` | `null \| integer` |  |
| `email_config_id` | `null \| integer` |  |
| `cc_emails` | `null \| array` |  |
| `fwd_emails` | `null \| array` |  |
| `reply_cc_emails` | `null \| array` |  |
| `to_emails` | `null \| array` |  |
| `spam` | `null \| boolean` |  |
| `deleted` | `null \| boolean` |  |
| `fr_escalated` | `null \| boolean` |  |
| `is_escalated` | `null \| boolean` |  |
| `fr_due_by` | `null \| string` |  |
| `due_by` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `custom_fields` | `null \| object` |  |
| `attachments` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `association_type` | `null \| integer` |  |
| `associated_tickets_count` | `null \| integer` |  |
| `ticket_cc_emails` | `null \| array` |  |
| `ticket_bcc_emails` | `null \| array` |  |
| `support_email` | `null \| string` |  |
| `source_additional_info` | `null \| object` |  |
| `structured_description` | `null \| object` |  |
| `form_id` | `null \| integer` |  |
| `nr_due_by` | `null \| string` |  |
| `nr_escalated` | `null \| boolean` |  |


</details>

### Tickets Search

Search and filter tickets records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await freshdesk.tickets.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tickets",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Unique ticket ID |
| `subject` | `string` | Subject of the ticket |
| `description` | `string` | HTML content of the ticket |
| `description_text` | `string` | Plain text content of the ticket |
| `status` | `integer` | Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed |
| `priority` | `integer` | Priority: 1=Low, 2=Medium, 3=High, 4=Urgent |
| `source` | `integer` | Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email |
| `type` | `string` | Ticket type |
| `requester_id` | `integer` | ID of the requester |
| `requester` | `object` | Requester details including name, email, and contact info |
| `responder_id` | `integer` | ID of the agent to whom the ticket is assigned |
| `group_id` | `integer` | ID of the group to which the ticket is assigned |
| `company_id` | `integer` | Company ID of the requester |
| `product_id` | `integer` | ID of the product associated with the ticket |
| `email_config_id` | `integer` | ID of the email config used for the ticket |
| `cc_emails` | `array` | CC email addresses |
| `ticket_cc_emails` | `array` | Ticket CC email addresses |
| `to_emails` | `array` | To email addresses |
| `fwd_emails` | `array` | Forwarded email addresses |
| `reply_cc_emails` | `array` | Reply CC email addresses |
| `tags` | `array` | Tags associated with the ticket |
| `custom_fields` | `object` | Custom fields associated with the ticket |
| `due_by` | `string` | Resolution due by timestamp |
| `fr_due_by` | `string` | First response due by timestamp |
| `fr_escalated` | `boolean` | Whether the first response time was breached |
| `is_escalated` | `boolean` | Whether the ticket is escalated |
| `nr_due_by` | `string` | Next response due by timestamp |
| `nr_escalated` | `boolean` | Whether the next response time was breached |
| `spam` | `boolean` | Whether the ticket is marked as spam |
| `association_type` | `integer` | Association type for parent/child tickets |
| `associated_tickets_count` | `integer` | Number of associated tickets |
| `stats` | `object` | Ticket statistics including response and resolution times |
| `created_at` | `string` | Ticket creation timestamp |
| `updated_at` | `string` | Ticket last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique ticket ID |
| `data[].subject` | `string` | Subject of the ticket |
| `data[].description` | `string` | HTML content of the ticket |
| `data[].description_text` | `string` | Plain text content of the ticket |
| `data[].status` | `integer` | Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed |
| `data[].priority` | `integer` | Priority: 1=Low, 2=Medium, 3=High, 4=Urgent |
| `data[].source` | `integer` | Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email |
| `data[].type` | `string` | Ticket type |
| `data[].requester_id` | `integer` | ID of the requester |
| `data[].requester` | `object` | Requester details including name, email, and contact info |
| `data[].responder_id` | `integer` | ID of the agent to whom the ticket is assigned |
| `data[].group_id` | `integer` | ID of the group to which the ticket is assigned |
| `data[].company_id` | `integer` | Company ID of the requester |
| `data[].product_id` | `integer` | ID of the product associated with the ticket |
| `data[].email_config_id` | `integer` | ID of the email config used for the ticket |
| `data[].cc_emails` | `array` | CC email addresses |
| `data[].ticket_cc_emails` | `array` | Ticket CC email addresses |
| `data[].to_emails` | `array` | To email addresses |
| `data[].fwd_emails` | `array` | Forwarded email addresses |
| `data[].reply_cc_emails` | `array` | Reply CC email addresses |
| `data[].tags` | `array` | Tags associated with the ticket |
| `data[].custom_fields` | `object` | Custom fields associated with the ticket |
| `data[].due_by` | `string` | Resolution due by timestamp |
| `data[].fr_due_by` | `string` | First response due by timestamp |
| `data[].fr_escalated` | `boolean` | Whether the first response time was breached |
| `data[].is_escalated` | `boolean` | Whether the ticket is escalated |
| `data[].nr_due_by` | `string` | Next response due by timestamp |
| `data[].nr_escalated` | `boolean` | Whether the next response time was breached |
| `data[].spam` | `boolean` | Whether the ticket is marked as spam |
| `data[].association_type` | `integer` | Association type for parent/child tickets |
| `data[].associated_tickets_count` | `integer` | Number of associated tickets |
| `data[].stats` | `object` | Ticket statistics including response and resolution times |
| `data[].created_at` | `string` | Ticket creation timestamp |
| `data[].updated_at` | `string` | Ticket last update timestamp |

</details>

## Contacts

### Contacts List

Returns a paginated list of contacts

#### Python SDK

```python
await freshdesk.contacts.list()
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
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |
| `updated_since` | `string` | No | Return contacts updated since this timestamp (ISO 8601) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `phone` | `null \| string` |  |
| `mobile` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `address` | `null \| string` |  |
| `avatar` | `null \| object` |  |
| `company_id` | `null \| integer` |  |
| `view_all_tickets` | `null \| boolean` |  |
| `custom_fields` | `null \| object` |  |
| `deleted` | `null \| boolean` |  |
| `description` | `null \| string` |  |
| `job_title` | `null \| string` |  |
| `language` | `null \| string` |  |
| `twitter_id` | `null \| string` |  |
| `unique_external_id` | `null \| string` |  |
| `other_emails` | `null \| array` |  |
| `other_companies` | `null \| array` |  |
| `tags` | `null \| array` |  |
| `time_zone` | `null \| string` |  |
| `facebook_id` | `null \| string` |  |
| `csat_rating` | `null \| integer` |  |
| `preferred_source` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `visitor_id` | `null \| string` |  |
| `org_contact_id` | `null \| integer` |  |
| `org_contact_id_str` | `null \| string` |  |
| `other_phone_numbers` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Contacts Get

Get a single contact by ID

#### Python SDK

```python
await freshdesk.contacts.get(
    id=0
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
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Contact ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `phone` | `null \| string` |  |
| `mobile` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `address` | `null \| string` |  |
| `avatar` | `null \| object` |  |
| `company_id` | `null \| integer` |  |
| `view_all_tickets` | `null \| boolean` |  |
| `custom_fields` | `null \| object` |  |
| `deleted` | `null \| boolean` |  |
| `description` | `null \| string` |  |
| `job_title` | `null \| string` |  |
| `language` | `null \| string` |  |
| `twitter_id` | `null \| string` |  |
| `unique_external_id` | `null \| string` |  |
| `other_emails` | `null \| array` |  |
| `other_companies` | `null \| array` |  |
| `tags` | `null \| array` |  |
| `time_zone` | `null \| string` |  |
| `facebook_id` | `null \| string` |  |
| `csat_rating` | `null \| integer` |  |
| `preferred_source` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `visitor_id` | `null \| string` |  |
| `org_contact_id` | `null \| integer` |  |
| `org_contact_id_str` | `null \| string` |  |
| `other_phone_numbers` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

## Agents

### Agents List

Returns a paginated list of agents

#### Python SDK

```python
await freshdesk.agents.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `available` | `null \| boolean` |  |
| `available_since` | `null \| string` |  |
| `occasional` | `null \| boolean` |  |
| `signature` | `null \| string` |  |
| `ticket_scope` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `skill_ids` | `null \| array` |  |
| `group_ids` | `null \| array` |  |
| `role_ids` | `null \| array` |  |
| `focus_mode` | `null \| boolean` |  |
| `contact` | `null \| object` |  |
| `last_active_at` | `null \| string` |  |
| `deactivated` | `null \| boolean` |  |
| `agent_operational_status` | `null \| string` |  |
| `org_agent_id` | `null \| string` |  |
| `org_group_ids` | `null \| array` |  |
| `contribution_group_ids` | `null \| array` |  |
| `org_contribution_group_ids` | `null \| array` |  |
| `scope` | `null \| integer \| object` |  |
| `availability` | `null \| array \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Agents Get

Get a single agent by ID

#### Python SDK

```python
await freshdesk.agents.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Agent ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `available` | `null \| boolean` |  |
| `available_since` | `null \| string` |  |
| `occasional` | `null \| boolean` |  |
| `signature` | `null \| string` |  |
| `ticket_scope` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `skill_ids` | `null \| array` |  |
| `group_ids` | `null \| array` |  |
| `role_ids` | `null \| array` |  |
| `focus_mode` | `null \| boolean` |  |
| `contact` | `null \| object` |  |
| `last_active_at` | `null \| string` |  |
| `deactivated` | `null \| boolean` |  |
| `agent_operational_status` | `null \| string` |  |
| `org_agent_id` | `null \| string` |  |
| `org_group_ids` | `null \| array` |  |
| `contribution_group_ids` | `null \| array` |  |
| `org_contribution_group_ids` | `null \| array` |  |
| `scope` | `null \| integer \| object` |  |
| `availability` | `null \| array \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Agents Search

Search and filter agents records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await freshdesk.agents.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Unique agent ID |
| `available` | `boolean` | Whether the agent is available |
| `available_since` | `string` | Timestamp since the agent has been available |
| `contact` | `object` | Contact details of the agent including name, email, phone, and job title |
| `occasional` | `boolean` | Whether the agent is an occasional agent |
| `signature` | `string` | Signature of the agent (HTML) |
| `ticket_scope` | `integer` | Ticket scope: 1=Global, 2=Group, 3=Restricted |
| `type` | `string` | Agent type: support_agent, field_agent, collaborator |
| `last_active_at` | `string` | Timestamp of last agent activity |
| `created_at` | `string` | Agent creation timestamp |
| `updated_at` | `string` | Agent last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique agent ID |
| `data[].available` | `boolean` | Whether the agent is available |
| `data[].available_since` | `string` | Timestamp since the agent has been available |
| `data[].contact` | `object` | Contact details of the agent including name, email, phone, and job title |
| `data[].occasional` | `boolean` | Whether the agent is an occasional agent |
| `data[].signature` | `string` | Signature of the agent (HTML) |
| `data[].ticket_scope` | `integer` | Ticket scope: 1=Global, 2=Group, 3=Restricted |
| `data[].type` | `string` | Agent type: support_agent, field_agent, collaborator |
| `data[].last_active_at` | `string` | Timestamp of last agent activity |
| `data[].created_at` | `string` | Agent creation timestamp |
| `data[].updated_at` | `string` | Agent last update timestamp |

</details>

## Groups

### Groups List

Returns a paginated list of groups

#### Python SDK

```python
await freshdesk.groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `agent_ids` | `null \| array` |  |
| `auto_ticket_assign` | `null \| integer` |  |
| `business_hour_id` | `null \| integer` |  |
| `escalate_to` | `null \| integer` |  |
| `unassigned_for` | `null \| string` |  |
| `group_type` | `null \| string` |  |
| `allow_agents_to_change_availability` | `null \| boolean` |  |
| `agent_availability_status` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Groups Get

Get a single group by ID

#### Python SDK

```python
await freshdesk.groups.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Group ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `agent_ids` | `null \| array` |  |
| `auto_ticket_assign` | `null \| integer` |  |
| `business_hour_id` | `null \| integer` |  |
| `escalate_to` | `null \| integer` |  |
| `unassigned_for` | `null \| string` |  |
| `group_type` | `null \| string` |  |
| `allow_agents_to_change_availability` | `null \| boolean` |  |
| `agent_availability_status` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Groups Search

Search and filter groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await freshdesk.groups.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | Unique group ID |
| `name` | `string` | Name of the group |
| `description` | `string` | Description of the group |
| `auto_ticket_assign` | `integer` | Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based |
| `business_hour_id` | `integer` | ID of the associated business hour |
| `escalate_to` | `integer` | User ID for escalation |
| `group_type` | `string` | Type of the group (e.g., support_agent_group) |
| `unassigned_for` | `string` | Time after which escalation triggers |
| `created_at` | `string` | Group creation timestamp |
| `updated_at` | `string` | Group last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique group ID |
| `data[].name` | `string` | Name of the group |
| `data[].description` | `string` | Description of the group |
| `data[].auto_ticket_assign` | `integer` | Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based |
| `data[].business_hour_id` | `integer` | ID of the associated business hour |
| `data[].escalate_to` | `integer` | User ID for escalation |
| `data[].group_type` | `string` | Type of the group (e.g., support_agent_group) |
| `data[].unassigned_for` | `string` | Time after which escalation triggers |
| `data[].created_at` | `string` | Group creation timestamp |
| `data[].updated_at` | `string` | Group last update timestamp |

</details>

## Companies

### Companies List

Returns a paginated list of companies

#### Python SDK

```python
await freshdesk.companies.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `domains` | `null \| array` |  |
| `note` | `null \| string` |  |
| `health_score` | `null \| string` |  |
| `account_tier` | `null \| string` |  |
| `renewal_date` | `null \| string` |  |
| `industry` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `org_company_id` | `null \| integer \| string` |  |
| `org_company_id_str` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Companies Get

Get a single company by ID

#### Python SDK

```python
await freshdesk.companies.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Company ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `domains` | `null \| array` |  |
| `note` | `null \| string` |  |
| `health_score` | `null \| string` |  |
| `account_tier` | `null \| string` |  |
| `renewal_date` | `null \| string` |  |
| `industry` | `null \| string` |  |
| `custom_fields` | `null \| object` |  |
| `org_company_id` | `null \| integer \| string` |  |
| `org_company_id_str` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

## Roles

### Roles List

Returns a paginated list of roles

#### Python SDK

```python
await freshdesk.roles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "roles",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `default` | `null \| boolean` |  |
| `agent_type` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Roles Get

Get a single role by ID

#### Python SDK

```python
await freshdesk.roles.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "roles",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Role ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `default` | `null \| boolean` |  |
| `agent_type` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

## Satisfaction Ratings

### Satisfaction Ratings List

Returns a paginated list of satisfaction ratings

#### Python SDK

```python
await freshdesk.satisfaction_ratings.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |
| `created_since` | `string` | No | Return ratings created since this timestamp (ISO 8601) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `survey_id` | `null \| integer` |  |
| `user_id` | `null \| integer` |  |
| `agent_id` | `null \| integer` |  |
| `group_id` | `null \| integer` |  |
| `ticket_id` | `null \| integer` |  |
| `feedback` | `null \| string` |  |
| `ratings` | `null \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

## Surveys

### Surveys List

Returns a paginated list of surveys

#### Python SDK

```python
await freshdesk.surveys.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "surveys",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `title` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `questions` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

## Time Entries

### Time Entries List

Returns a paginated list of time entries

#### Python SDK

```python
await freshdesk.time_entries.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_entries",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `agent_id` | `null \| integer` |  |
| `ticket_id` | `null \| integer` |  |
| `company_id` | `null \| integer` |  |
| `billable` | `null \| boolean` |  |
| `note` | `null \| string` |  |
| `time_spent` | `null \| string` |  |
| `timer_running` | `null \| boolean` |  |
| `executed_at` | `null \| string` |  |
| `start_time` | `null \| string` |  |
| `time_spent_in_seconds` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

## Ticket Fields

### Ticket Fields List

Returns a list of all ticket fields

#### Python SDK

```python
await freshdesk.ticket_fields.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `page` | `integer` | No | Page number (starts at 1) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `label` | `null \| string` |  |
| `label_for_customers` | `null \| string` |  |
| `description` | `null \| string` |  |
| `position` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `default` | `null \| boolean` |  |
| `required_for_closure` | `null \| boolean` |  |
| `required_for_agents` | `null \| boolean` |  |
| `required_for_customers` | `null \| boolean` |  |
| `customers_can_edit` | `null \| boolean` |  |
| `displayed_to_customers` | `null \| boolean` |  |
| `customers_can_filter` | `null \| boolean` |  |
| `portal_cc` | `null \| boolean` |  |
| `portal_cc_to` | `null \| string` |  |
| `choices` | `any \| array<string \| object> \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

