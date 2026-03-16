# Harvest full reference

This is the full reference documentation for the Harvest agent connector.

## Supported entities and actions

The Harvest connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Clients | [List](#clients-list), [Get](#clients-get), [Search](#clients-search) |
| Contacts | [List](#contacts-list), [Get](#contacts-get), [Search](#contacts-search) |
| Company | [Get](#company-get), [Search](#company-search) |
| Projects | [List](#projects-list), [Get](#projects-get), [Search](#projects-search) |
| Tasks | [List](#tasks-list), [Get](#tasks-get), [Search](#tasks-search) |
| Time Entries | [List](#time-entries-list), [Get](#time-entries-get), [Search](#time-entries-search) |
| Invoices | [List](#invoices-list), [Get](#invoices-get), [Search](#invoices-search) |
| Invoice Item Categories | [List](#invoice-item-categories-list), [Get](#invoice-item-categories-get), [Search](#invoice-item-categories-search) |
| Estimates | [List](#estimates-list), [Get](#estimates-get), [Search](#estimates-search) |
| Estimate Item Categories | [List](#estimate-item-categories-list), [Get](#estimate-item-categories-get), [Search](#estimate-item-categories-search) |
| Expenses | [List](#expenses-list), [Get](#expenses-get), [Search](#expenses-search) |
| Expense Categories | [List](#expense-categories-list), [Get](#expense-categories-get), [Search](#expense-categories-search) |
| Roles | [List](#roles-list), [Get](#roles-get), [Search](#roles-search) |
| User Assignments | [List](#user-assignments-list), [Search](#user-assignments-search) |
| Task Assignments | [List](#task-assignments-list), [Search](#task-assignments-search) |
| Time Projects | [List](#time-projects-list), [Search](#time-projects-search) |
| Time Tasks | [List](#time-tasks-list), [Search](#time-tasks-search) |

## Users

### Users List

Returns a paginated list of users in the Harvest account

#### Python SDK

```python
await harvest.users.list()
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
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `telephone` | `null \| string` |  |
| `timezone` | `null \| string` |  |
| `has_access_to_all_future_projects` | `null \| boolean` |  |
| `is_contractor` | `null \| boolean` |  |
| `is_active` | `null \| boolean` |  |
| `weekly_capacity` | `null \| integer` |  |
| `default_hourly_rate` | `null \| number` |  |
| `cost_rate` | `null \| number` |  |
| `roles` | `null \| array` |  |
| `access_roles` | `null \| array` |  |
| `avatar_url` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `employee_id` | `null \| string` |  |
| `calendar_integration_enabled` | `null \| boolean` |  |
| `calendar_integration_source` | `null \| string` |  |
| `can_create_projects` | `null \| boolean` |  |
| `permissions_claims` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Users Get

Get a single user by ID

#### Python SDK

```python
await harvest.users.get(
    id=0
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
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `telephone` | `null \| string` |  |
| `timezone` | `null \| string` |  |
| `has_access_to_all_future_projects` | `null \| boolean` |  |
| `is_contractor` | `null \| boolean` |  |
| `is_active` | `null \| boolean` |  |
| `weekly_capacity` | `null \| integer` |  |
| `default_hourly_rate` | `null \| number` |  |
| `cost_rate` | `null \| number` |  |
| `roles` | `null \| array` |  |
| `access_roles` | `null \| array` |  |
| `avatar_url` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `employee_id` | `null \| string` |  |
| `calendar_integration_enabled` | `null \| boolean` |  |
| `calendar_integration_source` | `null \| string` |  |
| `can_create_projects` | `null \| boolean` |  |
| `permissions_claims` | `null \| array` |  |


</details>

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.users.search(
    query={"filter": {"eq": {"avatar_url": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"avatar_url": "<str>"}}}
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
| `avatar_url` | `string` | Avatar URL |
| `cost_rate` | `number` | Cost rate |
| `created_at` | `string` | When created |
| `default_hourly_rate` | `number` | Default hourly rate |
| `email` | `string` | Email address |
| `first_name` | `string` | First name |
| `id` | `integer` | Unique identifier |
| `is_active` | `boolean` | Whether active |
| `is_contractor` | `boolean` | Whether contractor |
| `last_name` | `string` | Last name |
| `roles` | `array` | Assigned roles |
| `telephone` | `string` | Phone number |
| `timezone` | `string` | Timezone |
| `updated_at` | `string` | When last updated |
| `weekly_capacity` | `integer` | Weekly capacity in seconds |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].avatar_url` | `string` | Avatar URL |
| `data[].cost_rate` | `number` | Cost rate |
| `data[].created_at` | `string` | When created |
| `data[].default_hourly_rate` | `number` | Default hourly rate |
| `data[].email` | `string` | Email address |
| `data[].first_name` | `string` | First name |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_active` | `boolean` | Whether active |
| `data[].is_contractor` | `boolean` | Whether contractor |
| `data[].last_name` | `string` | Last name |
| `data[].roles` | `array` | Assigned roles |
| `data[].telephone` | `string` | Phone number |
| `data[].timezone` | `string` | Timezone |
| `data[].updated_at` | `string` | When last updated |
| `data[].weekly_capacity` | `integer` | Weekly capacity in seconds |

</details>

## Clients

### Clients List

Returns a paginated list of clients

#### Python SDK

```python
await harvest.clients.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "clients",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `is_active` | `null \| boolean` |  |
| `address` | `null \| string` |  |
| `statement_key` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Clients Get

Get a single client by ID

#### Python SDK

```python
await harvest.clients.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "clients",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Client ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `is_active` | `null \| boolean` |  |
| `address` | `null \| string` |  |
| `statement_key` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Clients Search

Search and filter clients records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.clients.search(
    query={"filter": {"eq": {"address": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "clients",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"address": "<str>"}}}
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
| `address` | `string` | The client's postal address |
| `created_at` | `string` | When the client record was created |
| `currency` | `string` | The currency used by the client |
| `id` | `integer` | Unique identifier for the client |
| `is_active` | `boolean` | Whether the client is active |
| `name` | `string` | The client's name |
| `updated_at` | `string` | When the client record was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].address` | `string` | The client's postal address |
| `data[].created_at` | `string` | When the client record was created |
| `data[].currency` | `string` | The currency used by the client |
| `data[].id` | `integer` | Unique identifier for the client |
| `data[].is_active` | `boolean` | Whether the client is active |
| `data[].name` | `string` | The client's name |
| `data[].updated_at` | `string` | When the client record was last updated |

</details>

## Contacts

### Contacts List

Returns a paginated list of contacts

#### Python SDK

```python
await harvest.contacts.list()
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
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `title` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `phone_office` | `null \| string` |  |
| `phone_mobile` | `null \| string` |  |
| `fax` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Contacts Get

Get a single contact by ID

#### Python SDK

```python
await harvest.contacts.get(
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
| `title` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `phone_office` | `null \| string` |  |
| `phone_mobile` | `null \| string` |  |
| `fax` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |


</details>

### Contacts Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.contacts.search(
    query={"filter": {"eq": {"client": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"client": {}}}}
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
| `client` | `object` | Client associated with the contact |
| `created_at` | `string` | When created |
| `email` | `string` | Email address |
| `first_name` | `string` | First name |
| `id` | `integer` | Unique identifier |
| `last_name` | `string` | Last name |
| `title` | `string` | Job title |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].client` | `object` | Client associated with the contact |
| `data[].created_at` | `string` | When created |
| `data[].email` | `string` | Email address |
| `data[].first_name` | `string` | First name |
| `data[].id` | `integer` | Unique identifier |
| `data[].last_name` | `string` | Last name |
| `data[].title` | `string` | Job title |
| `data[].updated_at` | `string` | When last updated |

</details>

## Company

### Company Get

Returns the company information for the authenticated account

#### Python SDK

```python
await harvest.company.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "company",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `base_uri` | `null \| string` |  |
| `full_domain` | `null \| string` |  |
| `name` | `null \| string` |  |
| `is_active` | `null \| boolean` |  |
| `week_start_day` | `null \| string` |  |
| `wants_timestamp_timers` | `null \| boolean` |  |
| `time_format` | `null \| string` |  |
| `date_format` | `null \| string` |  |
| `plan_type` | `null \| string` |  |
| `clock` | `null \| string` |  |
| `currency_code_display` | `null \| string` |  |
| `currency_symbol_display` | `null \| string` |  |
| `decimal_symbol` | `null \| string` |  |
| `thousands_separator` | `null \| string` |  |
| `color_scheme` | `null \| string` |  |
| `weekly_capacity` | `null \| integer` |  |
| `expense_feature` | `null \| boolean` |  |
| `invoice_feature` | `null \| boolean` |  |
| `estimate_feature` | `null \| boolean` |  |
| `approval_feature` | `null \| boolean` |  |
| `team_feature` | `null \| boolean` |  |
| `currency` | `null \| string` |  |
| `saml_sign_in_required` | `null \| boolean` |  |
| `day_entry_notes_required` | `null \| boolean` |  |


</details>

### Company Search

Search and filter company records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.company.search(
    query={"filter": {"eq": {"base_uri": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "company",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"base_uri": "<str>"}}}
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
| `base_uri` | `string` | The base URI |
| `currency` | `string` | Currency used by the company |
| `full_domain` | `string` | The full domain name |
| `is_active` | `boolean` | Whether the company is active |
| `name` | `string` | The name of the company |
| `plan_type` | `string` | The plan type |
| `weekly_capacity` | `integer` | Weekly capacity in seconds |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].base_uri` | `string` | The base URI |
| `data[].currency` | `string` | Currency used by the company |
| `data[].full_domain` | `string` | The full domain name |
| `data[].is_active` | `boolean` | Whether the company is active |
| `data[].name` | `string` | The name of the company |
| `data[].plan_type` | `string` | The plan type |
| `data[].weekly_capacity` | `integer` | Weekly capacity in seconds |

</details>

## Projects

### Projects List

Returns a paginated list of projects

#### Python SDK

```python
await harvest.projects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `code` | `null \| string` |  |
| `is_active` | `null \| boolean` |  |
| `is_billable` | `null \| boolean` |  |
| `is_fixed_fee` | `null \| boolean` |  |
| `bill_by` | `null \| string` |  |
| `hourly_rate` | `null \| number` |  |
| `budget_by` | `null \| string` |  |
| `budget_is_monthly` | `null \| boolean` |  |
| `budget` | `null \| number` |  |
| `cost_budget` | `null \| number` |  |
| `cost_budget_include_expenses` | `null \| boolean` |  |
| `notify_when_over_budget` | `null \| boolean` |  |
| `over_budget_notification_percentage` | `null \| number` |  |
| `over_budget_notification_date` | `null \| string` |  |
| `show_budget_to_all` | `null \| boolean` |  |
| `fee` | `null \| number` |  |
| `notes` | `null \| string` |  |
| `starts_on` | `null \| string` |  |
| `ends_on` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Projects Get

Get a single project by ID

#### Python SDK

```python
await harvest.projects.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Project ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `code` | `null \| string` |  |
| `is_active` | `null \| boolean` |  |
| `is_billable` | `null \| boolean` |  |
| `is_fixed_fee` | `null \| boolean` |  |
| `bill_by` | `null \| string` |  |
| `hourly_rate` | `null \| number` |  |
| `budget_by` | `null \| string` |  |
| `budget_is_monthly` | `null \| boolean` |  |
| `budget` | `null \| number` |  |
| `cost_budget` | `null \| number` |  |
| `cost_budget_include_expenses` | `null \| boolean` |  |
| `notify_when_over_budget` | `null \| boolean` |  |
| `over_budget_notification_percentage` | `null \| number` |  |
| `over_budget_notification_date` | `null \| string` |  |
| `show_budget_to_all` | `null \| boolean` |  |
| `fee` | `null \| number` |  |
| `notes` | `null \| string` |  |
| `starts_on` | `null \| string` |  |
| `ends_on` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |


</details>

### Projects Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.projects.search(
    query={"filter": {"eq": {"budget": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"budget": 0.0}}}
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
| `budget` | `number` | Budget amount |
| `client` | `object` | Client details |
| `code` | `string` | Project code |
| `created_at` | `string` | When created |
| `hourly_rate` | `number` | Hourly rate |
| `id` | `integer` | Unique identifier |
| `is_active` | `boolean` | Whether active |
| `is_billable` | `boolean` | Whether billable |
| `name` | `string` | Project name |
| `starts_on` | `string` | Start date |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].budget` | `number` | Budget amount |
| `data[].client` | `object` | Client details |
| `data[].code` | `string` | Project code |
| `data[].created_at` | `string` | When created |
| `data[].hourly_rate` | `number` | Hourly rate |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_active` | `boolean` | Whether active |
| `data[].is_billable` | `boolean` | Whether billable |
| `data[].name` | `string` | Project name |
| `data[].starts_on` | `string` | Start date |
| `data[].updated_at` | `string` | When last updated |

</details>

## Tasks

### Tasks List

Returns a paginated list of tasks

#### Python SDK

```python
await harvest.tasks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `billable_by_default` | `null \| boolean` |  |
| `default_hourly_rate` | `null \| number` |  |
| `is_default` | `null \| boolean` |  |
| `is_active` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Tasks Get

Get a single task by ID

#### Python SDK

```python
await harvest.tasks.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Task ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `billable_by_default` | `null \| boolean` |  |
| `default_hourly_rate` | `null \| number` |  |
| `is_default` | `null \| boolean` |  |
| `is_active` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Tasks Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.tasks.search(
    query={"filter": {"eq": {"billable_by_default": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billable_by_default": True}}}
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
| `billable_by_default` | `boolean` | Whether billable by default |
| `created_at` | `string` | When created |
| `default_hourly_rate` | `number` | Default hourly rate |
| `id` | `integer` | Unique identifier |
| `is_active` | `boolean` | Whether active |
| `name` | `string` | Task name |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billable_by_default` | `boolean` | Whether billable by default |
| `data[].created_at` | `string` | When created |
| `data[].default_hourly_rate` | `number` | Default hourly rate |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_active` | `boolean` | Whether active |
| `data[].name` | `string` | Task name |
| `data[].updated_at` | `string` | When last updated |

</details>

## Time Entries

### Time Entries List

Returns a paginated list of time entries

#### Python SDK

```python
await harvest.time_entries.list()
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
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `spent_date` | `null \| string` |  |
| `hours` | `null \| number` |  |
| `hours_without_timer` | `null \| number` |  |
| `rounded_hours` | `null \| number` |  |
| `notes` | `null \| string` |  |
| `is_locked` | `null \| boolean` |  |
| `locked_reason` | `null \| string` |  |
| `is_closed` | `null \| boolean` |  |
| `is_billed` | `null \| boolean` |  |
| `timer_started_at` | `null \| string` |  |
| `started_time` | `null \| string` |  |
| `ended_time` | `null \| string` |  |
| `is_running` | `null \| boolean` |  |
| `billable` | `null \| boolean` |  |
| `budgeted` | `null \| boolean` |  |
| `billable_rate` | `null \| number` |  |
| `cost_rate` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `approval_status` | `null \| string` |  |
| `is_explicitly_locked` | `null \| boolean` |  |
| `user` | `null \| object` |  |
| `client` | `null \| object` |  |
| `project` | `null \| object` |  |
| `task` | `null \| object` |  |
| `user_assignment` | `null \| object` |  |
| `task_assignment` | `null \| object` |  |
| `external_reference` | `null \| object` |  |
| `invoice` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Time Entries Get

Get a single time entry by ID

#### Python SDK

```python
await harvest.time_entries.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_entries",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Time entry ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `spent_date` | `null \| string` |  |
| `hours` | `null \| number` |  |
| `hours_without_timer` | `null \| number` |  |
| `rounded_hours` | `null \| number` |  |
| `notes` | `null \| string` |  |
| `is_locked` | `null \| boolean` |  |
| `locked_reason` | `null \| string` |  |
| `is_closed` | `null \| boolean` |  |
| `is_billed` | `null \| boolean` |  |
| `timer_started_at` | `null \| string` |  |
| `started_time` | `null \| string` |  |
| `ended_time` | `null \| string` |  |
| `is_running` | `null \| boolean` |  |
| `billable` | `null \| boolean` |  |
| `budgeted` | `null \| boolean` |  |
| `billable_rate` | `null \| number` |  |
| `cost_rate` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `approval_status` | `null \| string` |  |
| `is_explicitly_locked` | `null \| boolean` |  |
| `user` | `null \| object` |  |
| `client` | `null \| object` |  |
| `project` | `null \| object` |  |
| `task` | `null \| object` |  |
| `user_assignment` | `null \| object` |  |
| `task_assignment` | `null \| object` |  |
| `external_reference` | `null \| object` |  |
| `invoice` | `null \| object` |  |


</details>

### Time Entries Search

Search and filter time entries records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.time_entries.search(
    query={"filter": {"eq": {"billable": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_entries",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billable": True}}}
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
| `billable` | `boolean` | Whether billable |
| `client` | `object` | Associated client |
| `created_at` | `string` | When created |
| `hours` | `number` | Hours logged |
| `id` | `integer` | Unique identifier |
| `is_billed` | `boolean` | Whether billed |
| `notes` | `string` | Notes |
| `project` | `object` | Associated project |
| `spent_date` | `string` | Date time was spent |
| `task` | `object` | Associated task |
| `updated_at` | `string` | When last updated |
| `user` | `object` | Associated user |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billable` | `boolean` | Whether billable |
| `data[].client` | `object` | Associated client |
| `data[].created_at` | `string` | When created |
| `data[].hours` | `number` | Hours logged |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_billed` | `boolean` | Whether billed |
| `data[].notes` | `string` | Notes |
| `data[].project` | `object` | Associated project |
| `data[].spent_date` | `string` | Date time was spent |
| `data[].task` | `object` | Associated task |
| `data[].updated_at` | `string` | When last updated |
| `data[].user` | `object` | Associated user |

</details>

## Invoices

### Invoices List

Returns a paginated list of invoices

#### Python SDK

```python
await harvest.invoices.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `client_key` | `null \| string` |  |
| `number` | `null \| string` |  |
| `purchase_order` | `null \| string` |  |
| `amount` | `null \| number` |  |
| `due_amount` | `null \| number` |  |
| `tax` | `null \| number` |  |
| `tax_amount` | `null \| number` |  |
| `tax2` | `null \| number` |  |
| `tax2_amount` | `null \| number` |  |
| `discount` | `null \| number` |  |
| `discount_amount` | `null \| number` |  |
| `subject` | `null \| string` |  |
| `notes` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `state` | `null \| string` |  |
| `period_start` | `null \| string` |  |
| `period_end` | `null \| string` |  |
| `issue_date` | `null \| string` |  |
| `due_date` | `null \| string` |  |
| `payment_term` | `null \| string` |  |
| `payment_options` | `null \| array` |  |
| `sent_at` | `null \| string` |  |
| `paid_at` | `null \| string` |  |
| `paid_date` | `null \| string` |  |
| `closed_at` | `null \| string` |  |
| `recurring_invoice_id` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |
| `estimate` | `null \| object` |  |
| `retainer` | `null \| object` |  |
| `creator` | `null \| object` |  |
| `line_items` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Invoices Get

Get a single invoice by ID

#### Python SDK

```python
await harvest.invoices.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Invoice ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `client_key` | `null \| string` |  |
| `number` | `null \| string` |  |
| `purchase_order` | `null \| string` |  |
| `amount` | `null \| number` |  |
| `due_amount` | `null \| number` |  |
| `tax` | `null \| number` |  |
| `tax_amount` | `null \| number` |  |
| `tax2` | `null \| number` |  |
| `tax2_amount` | `null \| number` |  |
| `discount` | `null \| number` |  |
| `discount_amount` | `null \| number` |  |
| `subject` | `null \| string` |  |
| `notes` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `state` | `null \| string` |  |
| `period_start` | `null \| string` |  |
| `period_end` | `null \| string` |  |
| `issue_date` | `null \| string` |  |
| `due_date` | `null \| string` |  |
| `payment_term` | `null \| string` |  |
| `payment_options` | `null \| array` |  |
| `sent_at` | `null \| string` |  |
| `paid_at` | `null \| string` |  |
| `paid_date` | `null \| string` |  |
| `closed_at` | `null \| string` |  |
| `recurring_invoice_id` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |
| `estimate` | `null \| object` |  |
| `retainer` | `null \| object` |  |
| `creator` | `null \| object` |  |
| `line_items` | `null \| array` |  |


</details>

### Invoices Search

Search and filter invoices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.invoices.search(
    query={"filter": {"eq": {"amount": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoices",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount": 0.0}}}
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
| `amount` | `number` | Total amount |
| `client` | `object` | Client details |
| `created_at` | `string` | When created |
| `currency` | `string` | Currency |
| `due_amount` | `number` | Amount due |
| `due_date` | `string` | Due date |
| `id` | `integer` | Unique identifier |
| `issue_date` | `string` | Issue date |
| `number` | `string` | Invoice number |
| `state` | `string` | Current state |
| `subject` | `string` | Subject |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amount` | `number` | Total amount |
| `data[].client` | `object` | Client details |
| `data[].created_at` | `string` | When created |
| `data[].currency` | `string` | Currency |
| `data[].due_amount` | `number` | Amount due |
| `data[].due_date` | `string` | Due date |
| `data[].id` | `integer` | Unique identifier |
| `data[].issue_date` | `string` | Issue date |
| `data[].number` | `string` | Invoice number |
| `data[].state` | `string` | Current state |
| `data[].subject` | `string` | Subject |
| `data[].updated_at` | `string` | When last updated |

</details>

## Invoice Item Categories

### Invoice Item Categories List

Returns a paginated list of invoice item categories

#### Python SDK

```python
await harvest.invoice_item_categories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoice_item_categories",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `use_as_service` | `null \| boolean` |  |
| `use_as_expense` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Invoice Item Categories Get

Get a single invoice item category by ID

#### Python SDK

```python
await harvest.invoice_item_categories.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoice_item_categories",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Invoice item category ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `use_as_service` | `null \| boolean` |  |
| `use_as_expense` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Invoice Item Categories Search

Search and filter invoice item categories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.invoice_item_categories.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invoice_item_categories",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | When created |
| `id` | `integer` | Unique identifier |
| `name` | `string` | Category name |
| `updated_at` | `string` | When last updated |
| `use_as_expense` | `boolean` | Whether used as expense type |
| `use_as_service` | `boolean` | Whether used as service type |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When created |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Category name |
| `data[].updated_at` | `string` | When last updated |
| `data[].use_as_expense` | `boolean` | Whether used as expense type |
| `data[].use_as_service` | `boolean` | Whether used as service type |

</details>

## Estimates

### Estimates List

Returns a paginated list of estimates

#### Python SDK

```python
await harvest.estimates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "estimates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `client_key` | `null \| string` |  |
| `number` | `null \| string` |  |
| `purchase_order` | `null \| string` |  |
| `amount` | `null \| number` |  |
| `tax` | `null \| number` |  |
| `tax_amount` | `null \| number` |  |
| `tax2` | `null \| number` |  |
| `tax2_amount` | `null \| number` |  |
| `discount` | `null \| number` |  |
| `discount_amount` | `null \| number` |  |
| `subject` | `null \| string` |  |
| `notes` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `state` | `null \| string` |  |
| `issue_date` | `null \| string` |  |
| `sent_at` | `null \| string` |  |
| `accepted_at` | `null \| string` |  |
| `declined_at` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |
| `creator` | `null \| object` |  |
| `line_items` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Estimates Get

Get a single estimate by ID

#### Python SDK

```python
await harvest.estimates.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "estimates",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Estimate ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `client_key` | `null \| string` |  |
| `number` | `null \| string` |  |
| `purchase_order` | `null \| string` |  |
| `amount` | `null \| number` |  |
| `tax` | `null \| number` |  |
| `tax_amount` | `null \| number` |  |
| `tax2` | `null \| number` |  |
| `tax2_amount` | `null \| number` |  |
| `discount` | `null \| number` |  |
| `discount_amount` | `null \| number` |  |
| `subject` | `null \| string` |  |
| `notes` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `state` | `null \| string` |  |
| `issue_date` | `null \| string` |  |
| `sent_at` | `null \| string` |  |
| `accepted_at` | `null \| string` |  |
| `declined_at` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `client` | `null \| object` |  |
| `creator` | `null \| object` |  |
| `line_items` | `null \| array` |  |


</details>

### Estimates Search

Search and filter estimates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.estimates.search(
    query={"filter": {"eq": {"amount": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "estimates",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"amount": 0.0}}}
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
| `amount` | `number` | Total amount |
| `client` | `object` | Client details |
| `created_at` | `string` | When created |
| `currency` | `string` | Currency |
| `id` | `integer` | Unique identifier |
| `issue_date` | `string` | Issue date |
| `number` | `string` | Estimate number |
| `state` | `string` | Current state |
| `subject` | `string` | Subject |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].amount` | `number` | Total amount |
| `data[].client` | `object` | Client details |
| `data[].created_at` | `string` | When created |
| `data[].currency` | `string` | Currency |
| `data[].id` | `integer` | Unique identifier |
| `data[].issue_date` | `string` | Issue date |
| `data[].number` | `string` | Estimate number |
| `data[].state` | `string` | Current state |
| `data[].subject` | `string` | Subject |
| `data[].updated_at` | `string` | When last updated |

</details>

## Estimate Item Categories

### Estimate Item Categories List

Returns a paginated list of estimate item categories

#### Python SDK

```python
await harvest.estimate_item_categories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "estimate_item_categories",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Estimate Item Categories Get

Get a single estimate item category by ID

#### Python SDK

```python
await harvest.estimate_item_categories.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "estimate_item_categories",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Estimate item category ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Estimate Item Categories Search

Search and filter estimate item categories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.estimate_item_categories.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "estimate_item_categories",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | When created |
| `id` | `integer` | Unique identifier |
| `name` | `string` | Category name |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When created |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Category name |
| `data[].updated_at` | `string` | When last updated |

</details>

## Expenses

### Expenses List

Returns a paginated list of expenses

#### Python SDK

```python
await harvest.expenses.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "expenses",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `notes` | `null \| string` |  |
| `total_cost` | `null \| number` |  |
| `units` | `null \| number` |  |
| `is_closed` | `null \| boolean` |  |
| `is_locked` | `null \| boolean` |  |
| `is_billed` | `null \| boolean` |  |
| `locked_reason` | `null \| string` |  |
| `spent_date` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `billable` | `null \| boolean` |  |
| `approval_status` | `null \| string` |  |
| `is_explicitly_locked` | `null \| boolean` |  |
| `receipt` | `null \| object` |  |
| `user` | `null \| object` |  |
| `user_assignment` | `null \| object` |  |
| `project` | `null \| object` |  |
| `expense_category` | `null \| object` |  |
| `client` | `null \| object` |  |
| `invoice` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Expenses Get

Get a single expense by ID

#### Python SDK

```python
await harvest.expenses.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "expenses",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Expense ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `notes` | `null \| string` |  |
| `total_cost` | `null \| number` |  |
| `units` | `null \| number` |  |
| `is_closed` | `null \| boolean` |  |
| `is_locked` | `null \| boolean` |  |
| `is_billed` | `null \| boolean` |  |
| `locked_reason` | `null \| string` |  |
| `spent_date` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `billable` | `null \| boolean` |  |
| `approval_status` | `null \| string` |  |
| `is_explicitly_locked` | `null \| boolean` |  |
| `receipt` | `null \| object` |  |
| `user` | `null \| object` |  |
| `user_assignment` | `null \| object` |  |
| `project` | `null \| object` |  |
| `expense_category` | `null \| object` |  |
| `client` | `null \| object` |  |
| `invoice` | `null \| object` |  |


</details>

### Expenses Search

Search and filter expenses records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.expenses.search(
    query={"filter": {"eq": {"billable": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "expenses",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billable": True}}}
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
| `billable` | `boolean` | Whether billable |
| `client` | `object` | Associated client |
| `created_at` | `string` | When created |
| `expense_category` | `object` | Expense category |
| `id` | `integer` | Unique identifier |
| `is_billed` | `boolean` | Whether billed |
| `notes` | `string` | Notes |
| `project` | `object` | Associated project |
| `spent_date` | `string` | Date spent |
| `total_cost` | `number` | Total cost |
| `updated_at` | `string` | When last updated |
| `user` | `object` | Associated user |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billable` | `boolean` | Whether billable |
| `data[].client` | `object` | Associated client |
| `data[].created_at` | `string` | When created |
| `data[].expense_category` | `object` | Expense category |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_billed` | `boolean` | Whether billed |
| `data[].notes` | `string` | Notes |
| `data[].project` | `object` | Associated project |
| `data[].spent_date` | `string` | Date spent |
| `data[].total_cost` | `number` | Total cost |
| `data[].updated_at` | `string` | When last updated |
| `data[].user` | `object` | Associated user |

</details>

## Expense Categories

### Expense Categories List

Returns a paginated list of expense categories

#### Python SDK

```python
await harvest.expense_categories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "expense_categories",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `unit_name` | `null \| string` |  |
| `unit_price` | `null \| number` |  |
| `is_active` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Expense Categories Get

Get a single expense category by ID

#### Python SDK

```python
await harvest.expense_categories.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "expense_categories",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Expense category ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `unit_name` | `null \| string` |  |
| `unit_price` | `null \| number` |  |
| `is_active` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Expense Categories Search

Search and filter expense categories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.expense_categories.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "expense_categories",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | When created |
| `id` | `integer` | Unique identifier |
| `is_active` | `boolean` | Whether active |
| `name` | `string` | Category name |
| `unit_name` | `string` | Unit name |
| `unit_price` | `number` | Unit price |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When created |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_active` | `boolean` | Whether active |
| `data[].name` | `string` | Category name |
| `data[].unit_name` | `string` | Unit name |
| `data[].unit_price` | `number` | Unit price |
| `data[].updated_at` | `string` | When last updated |

</details>

## Roles

### Roles List

Returns a paginated list of roles

#### Python SDK

```python
await harvest.roles.list()
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
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `user_ids` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Roles Get

Get a single role by ID

#### Python SDK

```python
await harvest.roles.get(
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
| `user_ids` | `null \| array` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Roles Search

Search and filter roles records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.roles.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "roles",
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
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `created_at` | `string` | When created |
| `id` | `integer` | Unique identifier |
| `name` | `string` | Role name |
| `updated_at` | `string` | When last updated |
| `user_ids` | `array` | User IDs with this role |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When created |
| `data[].id` | `integer` | Unique identifier |
| `data[].name` | `string` | Role name |
| `data[].updated_at` | `string` | When last updated |
| `data[].user_ids` | `array` | User IDs with this role |

</details>

## User Assignments

### User Assignments List

Returns a paginated list of user assignments across all projects

#### Python SDK

```python
await harvest.user_assignments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user_assignments",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `is_project_manager` | `null \| boolean` |  |
| `is_active` | `null \| boolean` |  |
| `budget` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `hourly_rate` | `null \| number` |  |
| `use_default_rates` | `null \| boolean` |  |
| `project` | `null \| object` |  |
| `user` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### User Assignments Search

Search and filter user assignments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.user_assignments.search(
    query={"filter": {"eq": {"budget": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "user_assignments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"budget": 0.0}}}
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
| `budget` | `number` | Budget |
| `created_at` | `string` | When created |
| `hourly_rate` | `number` | Hourly rate |
| `id` | `integer` | Unique identifier |
| `is_active` | `boolean` | Whether active |
| `is_project_manager` | `boolean` | Whether project manager |
| `project` | `object` | Associated project |
| `updated_at` | `string` | When last updated |
| `user` | `object` | Associated user |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].budget` | `number` | Budget |
| `data[].created_at` | `string` | When created |
| `data[].hourly_rate` | `number` | Hourly rate |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_active` | `boolean` | Whether active |
| `data[].is_project_manager` | `boolean` | Whether project manager |
| `data[].project` | `object` | Associated project |
| `data[].updated_at` | `string` | When last updated |
| `data[].user` | `object` | Associated user |

</details>

## Task Assignments

### Task Assignments List

Returns a paginated list of task assignments across all projects

#### Python SDK

```python
await harvest.task_assignments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_assignments",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `billable` | `null \| boolean` |  |
| `is_active` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `hourly_rate` | `null \| number` |  |
| `budget` | `null \| number` |  |
| `project` | `null \| object` |  |
| `task` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Task Assignments Search

Search and filter task assignments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.task_assignments.search(
    query={"filter": {"eq": {"billable": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "task_assignments",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billable": True}}}
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
| `billable` | `boolean` | Whether billable |
| `created_at` | `string` | When created |
| `hourly_rate` | `number` | Hourly rate |
| `id` | `integer` | Unique identifier |
| `is_active` | `boolean` | Whether active |
| `project` | `object` | Associated project |
| `task` | `object` | Associated task |
| `updated_at` | `string` | When last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billable` | `boolean` | Whether billable |
| `data[].created_at` | `string` | When created |
| `data[].hourly_rate` | `number` | Hourly rate |
| `data[].id` | `integer` | Unique identifier |
| `data[].is_active` | `boolean` | Whether active |
| `data[].project` | `object` | Associated project |
| `data[].task` | `object` | Associated task |
| `data[].updated_at` | `string` | When last updated |

</details>

## Time Projects

### Time Projects List

Returns time report data grouped by project for a given date range

#### Python SDK

```python
await harvest.time_projects.list(
    from_="<str>",
    to="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_projects",
    "action": "list",
    "params": {
        "from": "<str>",
        "to": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `from` | `string` | Yes | Start date for the report in YYYYMMDD format |
| `to` | `string` | Yes | End date for the report in YYYYMMDD format |
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `project_id` | `null \| integer` |  |
| `project_name` | `null \| string` |  |
| `client_id` | `null \| integer` |  |
| `client_name` | `null \| string` |  |
| `total_hours` | `null \| number` |  |
| `billable_hours` | `null \| number` |  |
| `currency` | `null \| string` |  |
| `billable_amount` | `null \| number` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Time Projects Search

Search and filter time projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.time_projects.search(
    query={"filter": {"eq": {"billable_amount": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_projects",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billable_amount": 0.0}}}
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
| `billable_amount` | `number` | Total billable amount |
| `billable_hours` | `number` | Number of billable hours |
| `client_id` | `integer` | Client identifier |
| `client_name` | `string` | Client name |
| `currency` | `string` | Currency code |
| `project_id` | `integer` | Project identifier |
| `project_name` | `string` | Project name |
| `total_hours` | `number` | Total hours spent |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billable_amount` | `number` | Total billable amount |
| `data[].billable_hours` | `number` | Number of billable hours |
| `data[].client_id` | `integer` | Client identifier |
| `data[].client_name` | `string` | Client name |
| `data[].currency` | `string` | Currency code |
| `data[].project_id` | `integer` | Project identifier |
| `data[].project_name` | `string` | Project name |
| `data[].total_hours` | `number` | Total hours spent |

</details>

## Time Tasks

### Time Tasks List

Returns time report data grouped by task for a given date range

#### Python SDK

```python
await harvest.time_tasks.list(
    from_="<str>",
    to="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_tasks",
    "action": "list",
    "params": {
        "from": "<str>",
        "to": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `from` | `string` | Yes | Start date for the report in YYYYMMDD format |
| `to` | `string` | Yes | End date for the report in YYYYMMDD format |
| `per_page` | `integer` | No | Number of records per page (max 2000) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `task_id` | `null \| integer` |  |
| `task_name` | `null \| string` |  |
| `total_hours` | `null \| number` |  |
| `billable_hours` | `null \| number` |  |
| `currency` | `null \| string` |  |
| `billable_amount` | `null \| number` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Time Tasks Search

Search and filter time tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await harvest.time_tasks.search(
    query={"filter": {"eq": {"billable_amount": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "time_tasks",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"billable_amount": 0.0}}}
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
| `billable_amount` | `number` | Total billable amount |
| `billable_hours` | `number` | Number of billable hours |
| `currency` | `string` | Currency code |
| `task_id` | `integer` | Task identifier |
| `task_name` | `string` | Task name |
| `total_hours` | `number` | Total hours spent |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].billable_amount` | `number` | Total billable amount |
| `data[].billable_hours` | `number` | Number of billable hours |
| `data[].currency` | `string` | Currency code |
| `data[].task_id` | `integer` | Task identifier |
| `data[].task_name` | `string` | Task name |
| `data[].total_hours` | `number` | Total hours spent |

</details>

