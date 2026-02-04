# Klaviyo full reference

This is the full reference documentation for the Klaviyo agent connector.

## Supported entities and actions

The Klaviyo connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Profiles | [List](#profiles-list), [Get](#profiles-get), [Search](#profiles-search) |
| Lists | [List](#lists-list), [Get](#lists-get), [Search](#lists-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Search](#campaigns-search) |
| Events | [List](#events-list), [Search](#events-search) |
| Metrics | [List](#metrics-list), [Get](#metrics-get), [Search](#metrics-search) |
| Flows | [List](#flows-list), [Get](#flows-get), [Search](#flows-search) |
| Email Templates | [List](#email-templates-list), [Get](#email-templates-get), [Search](#email-templates-search) |

## Profiles

### Profiles List

Returns a paginated list of profiles (contacts) in your Klaviyo account

#### Python SDK

```python
await klaviyo.profiles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Profiles Get

Get a single profile by ID

#### Python SDK

```python
await klaviyo.profiles.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Profile ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Profiles Search

Search and filter profiles records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.profiles.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `relationships` | `object` |  |
| `segments` | `object` |  |
| `type` | `string` |  |
| `updated` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.relationships` | `object` |  |
| `hits[].data.segments` | `object` |  |
| `hits[].data.type` | `string` |  |
| `hits[].data.updated` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Lists

### Lists List

Returns a paginated list of all lists in your Klaviyo account

#### Python SDK

```python
await klaviyo.lists.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Lists Get

Get a single list by ID

#### Python SDK

```python
await klaviyo.lists.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | List ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Lists Search

Search and filter lists records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.lists.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `relationships` | `object` |  |
| `type` | `string` |  |
| `updated` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.relationships` | `object` |  |
| `hits[].data.type` | `string` |  |
| `hits[].data.updated` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Campaigns

### Campaigns List

Returns a paginated list of campaigns. A channel filter is required.

#### Python SDK

```python
await klaviyo.campaigns.list(
    filter="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list",
    "params": {
        "filter": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `string` | Yes | Filter by channel (email or sms) |
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Campaigns Get

Get a single campaign by ID

#### Python SDK

```python
await klaviyo.campaigns.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Campaign ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.campaigns.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `relationships` | `object` |  |
| `type` | `string` |  |
| `updated_at` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.relationships` | `object` |  |
| `hits[].data.type` | `string` |  |
| `hits[].data.updated_at` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Events

### Events List

Returns a paginated list of events (actions taken by profiles)

#### Python SDK

```python
await klaviyo.events.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |
| `sort` | `string` | No | Sort order for events |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `relationships` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Events Search

Search and filter events records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.events.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `datetime` | `string` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `relationships` | `object` |  |
| `type` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.datetime` | `string` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.relationships` | `object` |  |
| `hits[].data.type` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Metrics

### Metrics List

Returns a paginated list of metrics (event types)

#### Python SDK

```python
await klaviyo.metrics.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metrics",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Metrics Get

Get a single metric by ID

#### Python SDK

```python
await klaviyo.metrics.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metrics",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Metric ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Metrics Search

Search and filter metrics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.metrics.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "metrics",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `relationships` | `object` |  |
| `type` | `string` |  |
| `updated` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.relationships` | `object` |  |
| `hits[].data.type` | `string` |  |
| `hits[].data.updated` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Flows

### Flows List

Returns a paginated list of flows (automated sequences)

#### Python SDK

```python
await klaviyo.flows.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "flows",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Flows Get

Get a single flow by ID

#### Python SDK

```python
await klaviyo.flows.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "flows",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Flow ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Flows Search

Search and filter flows records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.flows.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "flows",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `relationships` | `object` |  |
| `type` | `string` |  |
| `updated` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.relationships` | `object` |  |
| `hits[].data.type` | `string` |  |
| `hits[].data.updated` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Email Templates

### Email Templates List

Returns a paginated list of email templates

#### Python SDK

```python
await klaviyo.email_templates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "email_templates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of results per page (max 100) |
| `page[cursor]` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Email Templates Get

Get a single email template by ID

#### Python SDK

```python
await klaviyo.email_templates.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "email_templates",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Template ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `type` | `string \| null` |  |
| `attributes` | `object \| null` |  |
| `links` | `object \| null` |  |


</details>

### Email Templates Search

Search and filter email templates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await klaviyo.email_templates.search(
    query={"filter": {"eq": {"attributes": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "email_templates",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"attributes": {}}}}
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
| `attributes` | `object` |  |
| `id` | `string` |  |
| `links` | `object` |  |
| `type` | `string` |  |
| `updated` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.attributes` | `object` |  |
| `hits[].data.id` | `string` |  |
| `hits[].data.links` | `object` |  |
| `hits[].data.type` | `string` |  |
| `hits[].data.updated` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

