# Amplitude full reference

This is the full reference documentation for the Amplitude agent connector.

## Supported entities and actions

The Amplitude connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Annotations | [List](#annotations-list), [Get](#annotations-get), [Search](#annotations-search) |
| Cohorts | [List](#cohorts-list), [Get](#cohorts-get), [Search](#cohorts-search) |
| Events List | [List](#events-list-list), [Search](#events-list-search) |
| Active Users | [List](#active-users-list), [Search](#active-users-search) |
| Average Session Length | [List](#average-session-length-list), [Search](#average-session-length-search) |

## Annotations

### Annotations List

Returns all chart annotations for the project.

#### Python SDK

```python
await amplitude.annotations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "annotations",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `date` | `null \| string` |  |
| `details` | `null \| string` |  |
| `label` | `null \| string` |  |


</details>

### Annotations Get

Retrieves a single chart annotation by ID.

#### Python SDK

```python
await amplitude.annotations.get(
    annotation_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "annotations",
    "action": "get",
    "params": {
        "annotation_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `annotation_id` | `integer` | Yes | The ID of the annotation to retrieve |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `start` | `null \| string` |  |
| `end` | `null \| string` |  |
| `label` | `null \| string` |  |
| `details` | `null \| string` |  |
| `category` | `null \| object` |  |
| `chart_id` | `null \| string` |  |


</details>

### Annotations Search

Search and filter annotations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amplitude.annotations.search(
    query={"filter": {"eq": {"date": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "annotations",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"date": "<str>"}}}
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
| `date` | `string` | The date when the annotation was made |
| `details` | `string` | Additional details or information related to the annotation |
| `id` | `integer` | The unique identifier for the annotation |
| `label` | `string` | The label assigned to the annotation |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].date` | `string` | The date when the annotation was made |
| `data[].details` | `string` | Additional details or information related to the annotation |
| `data[].id` | `integer` | The unique identifier for the annotation |
| `data[].label` | `string` | The label assigned to the annotation |

</details>

## Cohorts

### Cohorts List

Returns all cohorts for the project.

#### Python SDK

```python
await amplitude.cohorts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cohorts",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `appId` | `null \| integer` |  |
| `archived` | `null \| boolean` |  |
| `chart_id` | `null \| string` |  |
| `createdAt` | `null \| integer` |  |
| `definition` | `null \| object` |  |
| `description` | `null \| string` |  |
| `edit_id` | `null \| string` |  |
| `finished` | `null \| boolean` |  |
| `hidden` | `null \| boolean` |  |
| `id` | `null \| string` |  |
| `is_official_content` | `null \| boolean` |  |
| `is_predictive` | `null \| boolean` |  |
| `lastComputed` | `null \| integer` |  |
| `lastMod` | `null \| integer` |  |
| `last_viewed` | `null \| integer` |  |
| `location_id` | `null \| string` |  |
| `metadata` | `null \| array` |  |
| `name` | `null \| string` |  |
| `owners` | `null \| array` |  |
| `popularity` | `null \| integer` |  |
| `published` | `null \| boolean` |  |
| `shortcut_ids` | `null \| array` |  |
| `size` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `view_count` | `null \| integer` |  |
| `viewers` | `null \| array` |  |
| `include_data_app_types` | `null \| array` |  |
| `per_app_metadata` | `null \| object` |  |
| `cohort_definition_type` | `null \| string` |  |
| `cohort_output_type` | `null \| string` |  |
| `is_generated_content` | `null \| boolean` |  |


</details>

### Cohorts Get

Retrieves a single cohort by ID.

#### Python SDK

```python
await amplitude.cohorts.get(
    cohort_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cohorts",
    "action": "get",
    "params": {
        "cohort_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cohort_id` | `string` | Yes | The ID of the cohort to retrieve |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `appId` | `null \| integer` |  |
| `archived` | `null \| boolean` |  |
| `chart_id` | `null \| string` |  |
| `createdAt` | `null \| integer` |  |
| `definition` | `null \| object` |  |
| `description` | `null \| string` |  |
| `edit_id` | `null \| string` |  |
| `finished` | `null \| boolean` |  |
| `hidden` | `null \| boolean` |  |
| `id` | `null \| string` |  |
| `is_official_content` | `null \| boolean` |  |
| `is_predictive` | `null \| boolean` |  |
| `lastComputed` | `null \| integer` |  |
| `lastMod` | `null \| integer` |  |
| `last_viewed` | `null \| integer` |  |
| `location_id` | `null \| string` |  |
| `metadata` | `null \| array` |  |
| `name` | `null \| string` |  |
| `owners` | `null \| array` |  |
| `popularity` | `null \| integer` |  |
| `published` | `null \| boolean` |  |
| `shortcut_ids` | `null \| array` |  |
| `size` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `view_count` | `null \| integer` |  |
| `viewers` | `null \| array` |  |
| `include_data_app_types` | `null \| array` |  |
| `per_app_metadata` | `null \| object` |  |
| `cohort_definition_type` | `null \| string` |  |
| `cohort_output_type` | `null \| string` |  |
| `is_generated_content` | `null \| boolean` |  |


</details>

### Cohorts Search

Search and filter cohorts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amplitude.cohorts.search(
    query={"filter": {"eq": {"appId": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "cohorts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"appId": 0}}}
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
| `appId` | `integer` | The unique identifier of the application |
| `archived` | `boolean` | Indicates if the cohort data is archived |
| `chart_id` | `string` | The identifier of the chart associated with the cohort |
| `createdAt` | `integer` | The timestamp when the cohort was created |
| `definition` | `object` | The specific definition or criteria for the cohort |
| `description` | `string` | A brief explanation or summary of the cohort |
| `edit_id` | `string` | The ID for editing purposes or version control |
| `finished` | `boolean` | Indicates if the cohort data has been finalized |
| `hidden` | `boolean` | Flag to determine if the cohort is hidden from view |
| `id` | `string` | The unique identifier for the cohort |
| `is_official_content` | `boolean` | Indicates if the cohort data is official content |
| `is_predictive` | `boolean` | Flag to indicate if the cohort is predictive |
| `lastComputed` | `integer` | Timestamp of the last computation of cohort data |
| `lastMod` | `integer` | Timestamp of the last modification made to the cohort |
| `last_viewed` | `integer` | Timestamp when the cohort was last viewed |
| `location_id` | `string` | Identifier of the location associated with the cohort |
| `metadata` | `array` | Additional information or data related to the cohort |
| `name` | `string` | The name or title of the cohort |
| `owners` | `array` | The owners or administrators of the cohort |
| `popularity` | `integer` | Popularity rank or score of the cohort |
| `published` | `boolean` | Status indicating if the cohort data is published |
| `shortcut_ids` | `array` | Identifiers of any shortcuts associated with the cohort |
| `size` | `integer` | Size or scale of the cohort data |
| `type` | `string` | The type or category of the cohort |
| `view_count` | `integer` | The total count of views on the cohort data |
| `viewers` | `array` | Users or viewers who have access to the cohort data |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].appId` | `integer` | The unique identifier of the application |
| `data[].archived` | `boolean` | Indicates if the cohort data is archived |
| `data[].chart_id` | `string` | The identifier of the chart associated with the cohort |
| `data[].createdAt` | `integer` | The timestamp when the cohort was created |
| `data[].definition` | `object` | The specific definition or criteria for the cohort |
| `data[].description` | `string` | A brief explanation or summary of the cohort |
| `data[].edit_id` | `string` | The ID for editing purposes or version control |
| `data[].finished` | `boolean` | Indicates if the cohort data has been finalized |
| `data[].hidden` | `boolean` | Flag to determine if the cohort is hidden from view |
| `data[].id` | `string` | The unique identifier for the cohort |
| `data[].is_official_content` | `boolean` | Indicates if the cohort data is official content |
| `data[].is_predictive` | `boolean` | Flag to indicate if the cohort is predictive |
| `data[].lastComputed` | `integer` | Timestamp of the last computation of cohort data |
| `data[].lastMod` | `integer` | Timestamp of the last modification made to the cohort |
| `data[].last_viewed` | `integer` | Timestamp when the cohort was last viewed |
| `data[].location_id` | `string` | Identifier of the location associated with the cohort |
| `data[].metadata` | `array` | Additional information or data related to the cohort |
| `data[].name` | `string` | The name or title of the cohort |
| `data[].owners` | `array` | The owners or administrators of the cohort |
| `data[].popularity` | `integer` | Popularity rank or score of the cohort |
| `data[].published` | `boolean` | Status indicating if the cohort data is published |
| `data[].shortcut_ids` | `array` | Identifiers of any shortcuts associated with the cohort |
| `data[].size` | `integer` | Size or scale of the cohort data |
| `data[].type` | `string` | The type or category of the cohort |
| `data[].view_count` | `integer` | The total count of views on the cohort data |
| `data[].viewers` | `array` | Users or viewers who have access to the cohort data |

</details>

## Events List

### Events List List

Returns the list of event types with the current week's totals, unique users, and percentage of DAU.


#### Python SDK

```python
await amplitude.events_list.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events_list",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `autohidden` | `null \| boolean` |  |
| `clusters_hidden` | `null \| boolean` |  |
| `deleted` | `null \| boolean` |  |
| `display` | `null \| string` |  |
| `flow_hidden` | `null \| boolean` |  |
| `hidden` | `null \| boolean` |  |
| `id` | `number` |  |
| `in_waitroom` | `null \| boolean` |  |
| `name` | `null \| string` |  |
| `non_active` | `null \| boolean` |  |
| `timeline_hidden` | `null \| boolean` |  |
| `totals` | `null \| number` |  |
| `totals_delta` | `null \| number` |  |
| `value` | `null \| string` |  |
| `waitroom_approved` | `null \| boolean` |  |


</details>

### Events List Search

Search and filter events list records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amplitude.events_list.search(
    query={"filter": {"eq": {"autohidden": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events_list",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"autohidden": True}}}
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
| `autohidden` | `boolean` | Whether the event is auto-hidden |
| `clusters_hidden` | `boolean` | Whether the event is hidden from clusters |
| `deleted` | `boolean` | Whether the event is deleted |
| `display` | `string` | Display name of the event |
| `flow_hidden` | `boolean` | Whether the event is hidden from Pathfinder |
| `hidden` | `boolean` | Whether the event is hidden |
| `id` | `number` | Unique identifier for the event type |
| `in_waitroom` | `boolean` | Whether the event is in the waitroom |
| `name` | `string` | Name of the event type |
| `non_active` | `boolean` | Whether the event is marked as inactive |
| `timeline_hidden` | `boolean | number` | Whether the event is hidden from the timeline |
| `totals` | `number` | Total number of times the event occurred this week |
| `totals_delta` | `number` | Change in totals from the previous period |
| `value` | `string` | Raw event name in the data |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].autohidden` | `boolean` | Whether the event is auto-hidden |
| `data[].clusters_hidden` | `boolean` | Whether the event is hidden from clusters |
| `data[].deleted` | `boolean` | Whether the event is deleted |
| `data[].display` | `string` | Display name of the event |
| `data[].flow_hidden` | `boolean` | Whether the event is hidden from Pathfinder |
| `data[].hidden` | `boolean` | Whether the event is hidden |
| `data[].id` | `number` | Unique identifier for the event type |
| `data[].in_waitroom` | `boolean` | Whether the event is in the waitroom |
| `data[].name` | `string` | Name of the event type |
| `data[].non_active` | `boolean` | Whether the event is marked as inactive |
| `data[].timeline_hidden` | `boolean | number` | Whether the event is hidden from the timeline |
| `data[].totals` | `number` | Total number of times the event occurred this week |
| `data[].totals_delta` | `number` | Change in totals from the previous period |
| `data[].value` | `string` | Raw event name in the data |

</details>

## Active Users

### Active Users List

Returns the number of active or new users for each day in the specified date range.


#### Python SDK

```python
await amplitude.active_users.list(
    start="<str>",
    end="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "active_users",
    "action": "list",
    "params": {
        "start": "<str>",
        "end": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `string` | Yes | First date included in data series, formatted YYYYMMDD (e.g. 20220101) |
| `end` | `string` | Yes | Last date included in data series, formatted YYYYMMDD (e.g. 20220131) |
| `m` | `"active" \| "new"` | No | Either 'new' or 'active' to get the desired count. Defaults to 'active'. |
| `i` | `1 \| 7 \| 30` | No | Either 1, 7, or 30 for daily, weekly, and monthly counts. Defaults to 1. |
| `g` | `string` | No | The property to group by (e.g. country, city, platform). |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `series` | `null \| array` |  |
| `seriesCollapsed` | `null \| array` |  |
| `seriesLabels` | `null \| array` |  |
| `seriesMeta` | `null \| array` |  |
| `xValues` | `null \| array` |  |


</details>

### Active Users Search

Search and filter active users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amplitude.active_users.search(
    query={"filter": {"eq": {"date": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "active_users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"date": "<str>"}}}
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
| `date` | `string` | The date for which the active user data is reported |
| `statistics` | `object` | The statistics related to the active users for the given date |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].date` | `string` | The date for which the active user data is reported |
| `data[].statistics` | `object` | The statistics related to the active users for the given date |

</details>

## Average Session Length

### Average Session Length List

Returns the average session length (in seconds) for each day in the specified date range.


#### Python SDK

```python
await amplitude.average_session_length.list(
    start="<str>",
    end="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "average_session_length",
    "action": "list",
    "params": {
        "start": "<str>",
        "end": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `string` | Yes | First date included in data series, formatted YYYYMMDD (e.g. 20220101) |
| `end` | `string` | Yes | Last date included in data series, formatted YYYYMMDD (e.g. 20220131) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `series` | `null \| array` |  |
| `seriesCollapsed` | `null \| array` |  |
| `seriesMeta` | `null \| array` |  |
| `xValues` | `null \| array` |  |


</details>

### Average Session Length Search

Search and filter average session length records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amplitude.average_session_length.search(
    query={"filter": {"eq": {"date": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "average_session_length",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"date": "<str>"}}}
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
| `date` | `string` | The date on which the session occurred |
| `length` | `number` | The duration of the session in seconds |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].date` | `string` | The date on which the session occurred |
| `data[].length` | `number` | The duration of the session in seconds |

</details>

