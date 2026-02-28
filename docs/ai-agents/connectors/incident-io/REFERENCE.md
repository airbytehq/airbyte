# Incident-Io full reference

This is the full reference documentation for the Incident-Io agent connector.

## Supported entities and actions

The Incident-Io connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Incidents | [List](#incidents-list), [Get](#incidents-get), [Search](#incidents-search) |
| Alerts | [List](#alerts-list), [Get](#alerts-get), [Search](#alerts-search) |
| Escalations | [List](#escalations-list), [Get](#escalations-get), [Search](#escalations-search) |
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Incident Updates | [List](#incident-updates-list), [Search](#incident-updates-search) |
| Incident Roles | [List](#incident-roles-list), [Get](#incident-roles-get), [Search](#incident-roles-search) |
| Incident Statuses | [List](#incident-statuses-list), [Get](#incident-statuses-get), [Search](#incident-statuses-search) |
| Incident Timestamps | [List](#incident-timestamps-list), [Get](#incident-timestamps-get), [Search](#incident-timestamps-search) |
| Severities | [List](#severities-list), [Get](#severities-get), [Search](#severities-search) |
| Custom Fields | [List](#custom-fields-list), [Get](#custom-fields-get), [Search](#custom-fields-search) |
| Catalog Types | [List](#catalog-types-list), [Get](#catalog-types-get), [Search](#catalog-types-search) |
| Schedules | [List](#schedules-list), [Get](#schedules-get), [Search](#schedules-search) |

## Incidents

### Incidents List

List all incidents for the organisation with cursor-based pagination.

#### Python SDK

```python
await incident_io.incidents.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incidents",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Number of incidents per page |
| `after` | `string` | No | Cursor for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `reference` | `null \| string` |  |
| `summary` | `null \| string` |  |
| `mode` | `null \| string` |  |
| `visibility` | `null \| string` |  |
| `permalink` | `null \| string` |  |
| `call_url` | `null \| string` |  |
| `slack_channel_id` | `null \| string` |  |
| `slack_channel_name` | `null \| string` |  |
| `slack_team_id` | `null \| string` |  |
| `has_debrief` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `creator` | `null \| object` |  |
| `incident_status` | `null \| object` |  |
| `severity` | `null \| object` |  |
| `incident_type` | `null \| object` |  |
| `incident_role_assignments` | `null \| array` |  |
| `custom_field_entries` | `null \| array` |  |
| `duration_metrics` | `null \| array` |  |
| `incident_timestamp_values` | `null \| array` |  |
| `workload_minutes_late` | `null \| number` |  |
| `workload_minutes_sleeping` | `null \| number` |  |
| `workload_minutes_total` | `null \| number` |  |
| `workload_minutes_working` | `null \| number` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.after` | `null \| string` |  |
| `pagination.page_size` | `null \| integer` |  |

</details>

### Incidents Get

Get a single incident by ID or numeric reference.

#### Python SDK

```python
await incident_io.incidents.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incidents",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Incident ID or numeric reference |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `reference` | `null \| string` |  |
| `summary` | `null \| string` |  |
| `mode` | `null \| string` |  |
| `visibility` | `null \| string` |  |
| `permalink` | `null \| string` |  |
| `call_url` | `null \| string` |  |
| `slack_channel_id` | `null \| string` |  |
| `slack_channel_name` | `null \| string` |  |
| `slack_team_id` | `null \| string` |  |
| `has_debrief` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `creator` | `null \| object` |  |
| `incident_status` | `null \| object` |  |
| `severity` | `null \| object` |  |
| `incident_type` | `null \| object` |  |
| `incident_role_assignments` | `null \| array` |  |
| `custom_field_entries` | `null \| array` |  |
| `duration_metrics` | `null \| array` |  |
| `incident_timestamp_values` | `null \| array` |  |
| `workload_minutes_late` | `null \| number` |  |
| `workload_minutes_sleeping` | `null \| number` |  |
| `workload_minutes_total` | `null \| number` |  |
| `workload_minutes_working` | `null \| number` |  |


</details>

### Incidents Search

Search and filter incidents records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.incidents.search(
    query={"filter": {"eq": {"call_url": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incidents",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"call_url": "<str>"}}}
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
| `call_url` | `string` | URL of the call associated with the incident |
| `created_at` | `string` | When the incident was created |
| `creator` | `object` | The user who created the incident |
| `custom_field_entries` | `array` | Custom field values for the incident |
| `duration_metrics` | `array` | Duration metrics associated with the incident |
| `has_debrief` | `boolean` | Whether the incident has had a debrief |
| `id` | `string` | Unique identifier for the incident |
| `incident_role_assignments` | `array` | Role assignments for the incident |
| `incident_status` | `object` | Current status of the incident |
| `incident_timestamp_values` | `array` | Timestamp values for the incident |
| `incident_type` | `object` | Type of the incident |
| `mode` | `string` | Mode of the incident: standard, retrospective, test, or tutorial |
| `name` | `string` | Name/title of the incident |
| `permalink` | `string` | Link to the incident in the dashboard |
| `reference` | `string` | Human-readable reference (e.g. INC-123) |
| `severity` | `object` | Severity of the incident |
| `slack_channel_id` | `string` | Slack channel ID for the incident |
| `slack_channel_name` | `string` | Slack channel name for the incident |
| `slack_team_id` | `string` | Slack team/workspace ID |
| `summary` | `string` | Detailed summary of the incident |
| `updated_at` | `string` | When the incident was last updated |
| `visibility` | `string` | Whether the incident is public or private |
| `workload_minutes_late` | `number` | Minutes of workload classified as late |
| `workload_minutes_sleeping` | `number` | Minutes of workload classified as sleeping |
| `workload_minutes_total` | `number` | Total workload minutes |
| `workload_minutes_working` | `number` | Minutes of workload classified as working |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].call_url` | `string` | URL of the call associated with the incident |
| `data[].created_at` | `string` | When the incident was created |
| `data[].creator` | `object` | The user who created the incident |
| `data[].custom_field_entries` | `array` | Custom field values for the incident |
| `data[].duration_metrics` | `array` | Duration metrics associated with the incident |
| `data[].has_debrief` | `boolean` | Whether the incident has had a debrief |
| `data[].id` | `string` | Unique identifier for the incident |
| `data[].incident_role_assignments` | `array` | Role assignments for the incident |
| `data[].incident_status` | `object` | Current status of the incident |
| `data[].incident_timestamp_values` | `array` | Timestamp values for the incident |
| `data[].incident_type` | `object` | Type of the incident |
| `data[].mode` | `string` | Mode of the incident: standard, retrospective, test, or tutorial |
| `data[].name` | `string` | Name/title of the incident |
| `data[].permalink` | `string` | Link to the incident in the dashboard |
| `data[].reference` | `string` | Human-readable reference (e.g. INC-123) |
| `data[].severity` | `object` | Severity of the incident |
| `data[].slack_channel_id` | `string` | Slack channel ID for the incident |
| `data[].slack_channel_name` | `string` | Slack channel name for the incident |
| `data[].slack_team_id` | `string` | Slack team/workspace ID |
| `data[].summary` | `string` | Detailed summary of the incident |
| `data[].updated_at` | `string` | When the incident was last updated |
| `data[].visibility` | `string` | Whether the incident is public or private |
| `data[].workload_minutes_late` | `number` | Minutes of workload classified as late |
| `data[].workload_minutes_sleeping` | `number` | Minutes of workload classified as sleeping |
| `data[].workload_minutes_total` | `number` | Total workload minutes |
| `data[].workload_minutes_working` | `number` | Minutes of workload classified as working |

</details>

## Alerts

### Alerts List

List all alerts for the account with cursor-based pagination.

#### Python SDK

```python
await incident_io.alerts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "alerts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Number of alerts per page |
| `after` | `string` | No | Cursor for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |
| `status` | `null \| string` |  |
| `alert_source_id` | `null \| string` |  |
| `deduplication_key` | `null \| string` |  |
| `source_url` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `resolved_at` | `null \| string` |  |
| `attributes` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.after` | `null \| string` |  |
| `pagination.page_size` | `null \| integer` |  |

</details>

### Alerts Get

Show a single alert by ID.

#### Python SDK

```python
await incident_io.alerts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "alerts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Alert ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |
| `status` | `null \| string` |  |
| `alert_source_id` | `null \| string` |  |
| `deduplication_key` | `null \| string` |  |
| `source_url` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `resolved_at` | `null \| string` |  |
| `attributes` | `null \| array` |  |


</details>

### Alerts Search

Search and filter alerts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.alerts.search(
    query={"filter": {"eq": {"alert_source_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "alerts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"alert_source_id": "<str>"}}}
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
| `alert_source_id` | `string` | ID of the alert source that generated this alert |
| `attributes` | `array` | Structured alert attributes |
| `created_at` | `string` | When the alert was created |
| `deduplication_key` | `string` | Deduplication key uniquely referencing this alert |
| `description` | `string` | Description of the alert |
| `id` | `string` | Unique identifier for the alert |
| `resolved_at` | `string` | When the alert was resolved |
| `source_url` | `string` | Link to the alert in the upstream system |
| `status` | `string` | Status of the alert: firing or resolved |
| `title` | `string` | Title of the alert |
| `updated_at` | `string` | When the alert was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].alert_source_id` | `string` | ID of the alert source that generated this alert |
| `data[].attributes` | `array` | Structured alert attributes |
| `data[].created_at` | `string` | When the alert was created |
| `data[].deduplication_key` | `string` | Deduplication key uniquely referencing this alert |
| `data[].description` | `string` | Description of the alert |
| `data[].id` | `string` | Unique identifier for the alert |
| `data[].resolved_at` | `string` | When the alert was resolved |
| `data[].source_url` | `string` | Link to the alert in the upstream system |
| `data[].status` | `string` | Status of the alert: firing or resolved |
| `data[].title` | `string` | Title of the alert |
| `data[].updated_at` | `string` | When the alert was last updated |

</details>

## Escalations

### Escalations List

List all escalations for the account with cursor-based pagination.

#### Python SDK

```python
await incident_io.escalations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "escalations",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Number of escalations per page |
| `after` | `string` | No | Cursor for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `null \| string` |  |
| `status` | `null \| string` |  |
| `escalation_path_id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `creator` | `null \| object` |  |
| `priority` | `null \| object` |  |
| `events` | `null \| array` |  |
| `related_incidents` | `null \| array` |  |
| `related_alerts` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.after` | `null \| string` |  |
| `pagination.page_size` | `null \| integer` |  |

</details>

### Escalations Get

Show a specific escalation by ID.

#### Python SDK

```python
await incident_io.escalations.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "escalations",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Escalation ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `null \| string` |  |
| `status` | `null \| string` |  |
| `escalation_path_id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `creator` | `null \| object` |  |
| `priority` | `null \| object` |  |
| `events` | `null \| array` |  |
| `related_incidents` | `null \| array` |  |
| `related_alerts` | `null \| array` |  |


</details>

### Escalations Search

Search and filter escalations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.escalations.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "escalations",
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
| `created_at` | `string` | When the escalation was created |
| `creator` | `object` | The creator of this escalation |
| `escalation_path_id` | `string` | ID of the escalation path used |
| `events` | `array` | History of escalation events |
| `id` | `string` | Unique identifier for the escalation |
| `priority` | `object` | Priority of the escalation |
| `related_alerts` | `array` | Alerts related to this escalation |
| `related_incidents` | `array` | Incidents related to this escalation |
| `status` | `string` | Status: pending, triggered, acked, resolved, expired, cancelled |
| `title` | `string` | Title of the escalation |
| `updated_at` | `string` | When the escalation was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When the escalation was created |
| `data[].creator` | `object` | The creator of this escalation |
| `data[].escalation_path_id` | `string` | ID of the escalation path used |
| `data[].events` | `array` | History of escalation events |
| `data[].id` | `string` | Unique identifier for the escalation |
| `data[].priority` | `object` | Priority of the escalation |
| `data[].related_alerts` | `array` | Alerts related to this escalation |
| `data[].related_incidents` | `array` | Incidents related to this escalation |
| `data[].status` | `string` | Status: pending, triggered, acked, resolved, expired, cancelled |
| `data[].title` | `string` | Title of the escalation |
| `data[].updated_at` | `string` | When the escalation was last updated |

</details>

## Users

### Users List

List all users for the organisation with cursor-based pagination.

#### Python SDK

```python
await incident_io.users.list()
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
| `page_size` | `integer` | No | Number of users per page |
| `after` | `string` | No | Cursor for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `role` | `null \| string` |  |
| `slack_user_id` | `null \| string` |  |
| `base_role` | `null \| object` |  |
| `custom_roles` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.after` | `null \| string` |  |
| `pagination.page_size` | `null \| integer` |  |

</details>

### Users Get

Get a single user by ID.

#### Python SDK

```python
await incident_io.users.get(
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
| `id` | `string` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `role` | `null \| string` |  |
| `slack_user_id` | `null \| string` |  |
| `base_role` | `null \| object` |  |
| `custom_roles` | `null \| array` |  |


</details>

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.users.search(
    query={"filter": {"eq": {"base_role": {}}}}
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
        "query": {"filter": {"eq": {"base_role": {}}}}
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
| `base_role` | `object` | Base role assigned to the user |
| `custom_roles` | `array` | Custom roles assigned to the user |
| `email` | `string` | Email address of the user |
| `id` | `string` | Unique identifier for the user |
| `name` | `string` | Full name of the user |
| `role` | `string` | Deprecated role field |
| `slack_user_id` | `string` | Slack user ID |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].base_role` | `object` | Base role assigned to the user |
| `data[].custom_roles` | `array` | Custom roles assigned to the user |
| `data[].email` | `string` | Email address of the user |
| `data[].id` | `string` | Unique identifier for the user |
| `data[].name` | `string` | Full name of the user |
| `data[].role` | `string` | Deprecated role field |
| `data[].slack_user_id` | `string` | Slack user ID |

</details>

## Incident Updates

### Incident Updates List

List all incident updates for the organisation with cursor-based pagination.

#### Python SDK

```python
await incident_io.incident_updates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_updates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Number of incident updates per page |
| `after` | `string` | No | Cursor for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `incident_id` | `null \| string` |  |
| `message` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `new_incident_status` | `null \| object` |  |
| `new_severity` | `null \| object` |  |
| `updater` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.after` | `null \| string` |  |
| `pagination.page_size` | `null \| integer` |  |

</details>

### Incident Updates Search

Search and filter incident updates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.incident_updates.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_updates",
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
| `created_at` | `string` | When the update was created |
| `id` | `string` | Unique identifier for the incident update |
| `incident_id` | `string` | ID of the incident this update belongs to |
| `message` | `string` | Update message content |
| `new_incident_status` | `object` | New incident status set by this update |
| `new_severity` | `object` | New severity set by this update |
| `updater` | `object` | Who made this update |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When the update was created |
| `data[].id` | `string` | Unique identifier for the incident update |
| `data[].incident_id` | `string` | ID of the incident this update belongs to |
| `data[].message` | `string` | Update message content |
| `data[].new_incident_status` | `object` | New incident status set by this update |
| `data[].new_severity` | `object` | New severity set by this update |
| `data[].updater` | `object` | Who made this update |

</details>

## Incident Roles

### Incident Roles List

List all incident roles for the organisation.

#### Python SDK

```python
await incident_io.incident_roles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_roles",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `instructions` | `null \| string` |  |
| `shortform` | `null \| string` |  |
| `role_type` | `null \| string` |  |
| `required` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Incident Roles Get

Get a single incident role by ID.

#### Python SDK

```python
await incident_io.incident_roles.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_roles",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Incident role ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `instructions` | `null \| string` |  |
| `shortform` | `null \| string` |  |
| `role_type` | `null \| string` |  |
| `required` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Incident Roles Search

Search and filter incident roles records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.incident_roles.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_roles",
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
| `created_at` | `string` | When the role was created |
| `description` | `string` | Description of the role |
| `id` | `string` | Unique identifier for the incident role |
| `instructions` | `string` | Instructions for the role holder |
| `name` | `string` | Name of the role |
| `required` | `boolean` | Whether this role must be assigned |
| `role_type` | `string` | Type of role |
| `shortform` | `string` | Short form label for the role |
| `updated_at` | `string` | When the role was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When the role was created |
| `data[].description` | `string` | Description of the role |
| `data[].id` | `string` | Unique identifier for the incident role |
| `data[].instructions` | `string` | Instructions for the role holder |
| `data[].name` | `string` | Name of the role |
| `data[].required` | `boolean` | Whether this role must be assigned |
| `data[].role_type` | `string` | Type of role |
| `data[].shortform` | `string` | Short form label for the role |
| `data[].updated_at` | `string` | When the role was last updated |

</details>

## Incident Statuses

### Incident Statuses List

List all incident statuses for the organisation.

#### Python SDK

```python
await incident_io.incident_statuses.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_statuses",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `category` | `null \| string` |  |
| `rank` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Incident Statuses Get

Get a single incident status by ID.

#### Python SDK

```python
await incident_io.incident_statuses.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_statuses",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Incident status ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `category` | `null \| string` |  |
| `rank` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Incident Statuses Search

Search and filter incident statuses records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.incident_statuses.search(
    query={"filter": {"eq": {"category": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_statuses",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"category": "<str>"}}}
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
| `category` | `string` | Category: triage, active, post-incident, closed, etc. |
| `created_at` | `string` | When the status was created |
| `description` | `string` | Description of the status |
| `id` | `string` | Unique identifier for the status |
| `name` | `string` | Name of the status |
| `rank` | `number` | Rank for ordering |
| `updated_at` | `string` | When the status was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].category` | `string` | Category: triage, active, post-incident, closed, etc. |
| `data[].created_at` | `string` | When the status was created |
| `data[].description` | `string` | Description of the status |
| `data[].id` | `string` | Unique identifier for the status |
| `data[].name` | `string` | Name of the status |
| `data[].rank` | `number` | Rank for ordering |
| `data[].updated_at` | `string` | When the status was last updated |

</details>

## Incident Timestamps

### Incident Timestamps List

List all incident timestamps for the organisation.

#### Python SDK

```python
await incident_io.incident_timestamps.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_timestamps",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `rank` | `null \| number` |  |


</details>

### Incident Timestamps Get

Get a single incident timestamp by ID.

#### Python SDK

```python
await incident_io.incident_timestamps.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_timestamps",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Incident timestamp ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `rank` | `null \| number` |  |


</details>

### Incident Timestamps Search

Search and filter incident timestamps records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.incident_timestamps.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incident_timestamps",
    "action": "search",
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
| `id` | `string` | Unique identifier for the timestamp |
| `name` | `string` | Name of the timestamp |
| `rank` | `number` | Rank for ordering |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the timestamp |
| `data[].name` | `string` | Name of the timestamp |
| `data[].rank` | `number` | Rank for ordering |

</details>

## Severities

### Severities List

List all severities for the organisation.

#### Python SDK

```python
await incident_io.severities.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "severities",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `rank` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Severities Get

Get a single severity by ID.

#### Python SDK

```python
await incident_io.severities.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "severities",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Severity ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `rank` | `null \| number` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Severities Search

Search and filter severities records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.severities.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "severities",
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
| `created_at` | `string` | When the severity was created |
| `description` | `string` | Description of the severity |
| `id` | `string` | Unique identifier for the severity |
| `name` | `string` | Name of the severity |
| `rank` | `number` | Rank for ordering |
| `updated_at` | `string` | When the severity was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | When the severity was created |
| `data[].description` | `string` | Description of the severity |
| `data[].id` | `string` | Unique identifier for the severity |
| `data[].name` | `string` | Name of the severity |
| `data[].rank` | `number` | Rank for ordering |
| `data[].updated_at` | `string` | When the severity was last updated |

</details>

## Custom Fields

### Custom Fields List

List all custom fields for the organisation.

#### Python SDK

```python
await incident_io.custom_fields.list()
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



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `field_type` | `null \| string` |  |
| `catalog_type_id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Custom Fields Get

Get a single custom field by ID.

#### Python SDK

```python
await incident_io.custom_fields.get(
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
| `id` | `string` | Yes | Custom field ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `field_type` | `null \| string` |  |
| `catalog_type_id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Custom Fields Search

Search and filter custom fields records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.custom_fields.search(
    query={"filter": {"eq": {"catalog_type_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_fields",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"catalog_type_id": "<str>"}}}
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
| `catalog_type_id` | `string` | ID of the catalog type associated with this custom field |
| `created_at` | `string` | When the custom field was created |
| `description` | `string` | Description of the custom field |
| `field_type` | `string` | Type of field |
| `id` | `string` | Unique identifier for the custom field |
| `name` | `string` | Name of the custom field |
| `updated_at` | `string` | When the custom field was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].catalog_type_id` | `string` | ID of the catalog type associated with this custom field |
| `data[].created_at` | `string` | When the custom field was created |
| `data[].description` | `string` | Description of the custom field |
| `data[].field_type` | `string` | Type of field |
| `data[].id` | `string` | Unique identifier for the custom field |
| `data[].name` | `string` | Name of the custom field |
| `data[].updated_at` | `string` | When the custom field was last updated |

</details>

## Catalog Types

### Catalog Types List

List all catalog types for the organisation.

#### Python SDK

```python
await incident_io.catalog_types.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalog_types",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `type_name` | `null \| string` |  |
| `color` | `null \| string` |  |
| `icon` | `null \| string` |  |
| `ranked` | `null \| boolean` |  |
| `is_editable` | `null \| boolean` |  |
| `registry_type` | `null \| string` |  |
| `semantic_type` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `last_synced_at` | `null \| string` |  |
| `annotations` | `null \| object` |  |
| `categories` | `null \| array` |  |
| `required_integrations` | `null \| array` |  |
| `schema` | `null \| object` |  |


</details>

### Catalog Types Get

Show a single catalog type by ID.

#### Python SDK

```python
await incident_io.catalog_types.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalog_types",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Catalog type ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `type_name` | `null \| string` |  |
| `color` | `null \| string` |  |
| `icon` | `null \| string` |  |
| `ranked` | `null \| boolean` |  |
| `is_editable` | `null \| boolean` |  |
| `registry_type` | `null \| string` |  |
| `semantic_type` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `last_synced_at` | `null \| string` |  |
| `annotations` | `null \| object` |  |
| `categories` | `null \| array` |  |
| `required_integrations` | `null \| array` |  |
| `schema` | `null \| object` |  |


</details>

### Catalog Types Search

Search and filter catalog types records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.catalog_types.search(
    query={"filter": {"eq": {"annotations": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalog_types",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"annotations": {}}}}
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
| `annotations` | `object` | Annotations metadata |
| `categories` | `array` | Categories this type belongs to |
| `color` | `string` | Display color |
| `created_at` | `string` | When the catalog type was created |
| `description` | `string` | Description of the catalog type |
| `icon` | `string` | Display icon |
| `id` | `string` | Unique identifier for the catalog type |
| `is_editable` | `boolean` | Whether entries can be edited |
| `last_synced_at` | `string` | When the catalog type was last synced |
| `name` | `string` | Name of the catalog type |
| `ranked` | `boolean` | Whether entries are ranked |
| `registry_type` | `string` | Registry type if synced from an integration |
| `required_integrations` | `array` | Integrations required for this type |
| `schema` | `object` | Schema definition for the catalog type |
| `semantic_type` | `string` | Semantic type for special behavior |
| `type_name` | `string` | Programmatic type name |
| `updated_at` | `string` | When the catalog type was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].annotations` | `object` | Annotations metadata |
| `data[].categories` | `array` | Categories this type belongs to |
| `data[].color` | `string` | Display color |
| `data[].created_at` | `string` | When the catalog type was created |
| `data[].description` | `string` | Description of the catalog type |
| `data[].icon` | `string` | Display icon |
| `data[].id` | `string` | Unique identifier for the catalog type |
| `data[].is_editable` | `boolean` | Whether entries can be edited |
| `data[].last_synced_at` | `string` | When the catalog type was last synced |
| `data[].name` | `string` | Name of the catalog type |
| `data[].ranked` | `boolean` | Whether entries are ranked |
| `data[].registry_type` | `string` | Registry type if synced from an integration |
| `data[].required_integrations` | `array` | Integrations required for this type |
| `data[].schema` | `object` | Schema definition for the catalog type |
| `data[].semantic_type` | `string` | Semantic type for special behavior |
| `data[].type_name` | `string` | Programmatic type name |
| `data[].updated_at` | `string` | When the catalog type was last updated |

</details>

## Schedules

### Schedules List

List all on-call schedules with cursor-based pagination.

#### Python SDK

```python
await incident_io.schedules.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schedules",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Number of schedules per page |
| `after` | `string` | No | Cursor for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `timezone` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `annotations` | `null \| object` |  |
| `config` | `null \| object` |  |
| `team_ids` | `null \| array` |  |
| `holidays_public_config` | `null \| object` |  |
| `current_shifts` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.after` | `null \| string` |  |
| `pagination.page_size` | `null \| integer` |  |

</details>

### Schedules Get

Get a single on-call schedule by ID.

#### Python SDK

```python
await incident_io.schedules.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schedules",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Schedule ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `null \| string` |  |
| `timezone` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `annotations` | `null \| object` |  |
| `config` | `null \| object` |  |
| `team_ids` | `null \| array` |  |
| `holidays_public_config` | `null \| object` |  |
| `current_shifts` | `null \| array` |  |


</details>

### Schedules Search

Search and filter schedules records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await incident_io.schedules.search(
    query={"filter": {"eq": {"annotations": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schedules",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"annotations": {}}}}
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
| `annotations` | `object` | Annotations metadata |
| `config` | `object` | Schedule configuration with rotations |
| `created_at` | `string` | When the schedule was created |
| `current_shifts` | `array` | Currently active shifts |
| `holidays_public_config` | `object` | Public holiday configuration for the schedule |
| `id` | `string` | Unique identifier for the schedule |
| `name` | `string` | Name of the schedule |
| `team_ids` | `array` | IDs of teams associated with this schedule |
| `timezone` | `string` | Timezone for the schedule |
| `updated_at` | `string` | When the schedule was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].annotations` | `object` | Annotations metadata |
| `data[].config` | `object` | Schedule configuration with rotations |
| `data[].created_at` | `string` | When the schedule was created |
| `data[].current_shifts` | `array` | Currently active shifts |
| `data[].holidays_public_config` | `object` | Public holiday configuration for the schedule |
| `data[].id` | `string` | Unique identifier for the schedule |
| `data[].name` | `string` | Name of the schedule |
| `data[].team_ids` | `array` | IDs of teams associated with this schedule |
| `data[].timezone` | `string` | Timezone for the schedule |
| `data[].updated_at` | `string` | When the schedule was last updated |

</details>

