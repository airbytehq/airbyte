# Airtable full reference

This is the full reference documentation for the Airtable agent connector.

## Supported entities and actions

The Airtable connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Bases | [List](#bases-list), [Search](#bases-search) |
| Tables | [List](#tables-list), [Search](#tables-search) |
| Records | [List](#records-list), [Get](#records-get) |

## Bases

### Bases List

Returns a list of all bases the user has access to

#### Python SDK

```python
await airtable.bases.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bases",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `offset` | `string` | No | Pagination offset from previous response |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `permissionLevel` | `string \| null` |  |


</details>

### Bases Search

Search and filter bases records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await airtable.bases.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bases",
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
| `id` | `string` | Unique identifier for the base |
| `name` | `string` | Name of the base |
| `permissionLevel` | `string` | Permission level for the base |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the base |
| `data[].name` | `string` | Name of the base |
| `data[].permissionLevel` | `string` | Permission level for the base |

</details>

## Tables

### Tables List

Returns a list of all tables in the specified base with their schema information

#### Python SDK

```python
await airtable.tables.list(
    base_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tables",
    "action": "list",
    "params": {
        "base_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `base_id` | `string` | Yes | The ID of the base |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `primaryFieldId` | `string \| null` |  |
| `fields` | `array \| null` |  |
| `fields[].id` | `string \| null` |  |
| `fields[].name` | `string \| null` |  |
| `fields[].type` | `string \| null` |  |
| `fields[].options` | `object \| null` |  |
| `views` | `array \| null` |  |
| `views[].id` | `string \| null` |  |
| `views[].name` | `string \| null` |  |
| `views[].type` | `string \| null` |  |


</details>

### Tables Search

Search and filter tables records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await airtable.tables.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tables",
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
| `id` | `string` | Unique identifier for the table |
| `name` | `string` | Name of the table |
| `primaryFieldId` | `string` | ID of the primary field |
| `fields` | `array` | List of fields in the table |
| `views` | `array` | List of views in the table |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the table |
| `data[].name` | `string` | Name of the table |
| `data[].primaryFieldId` | `string` | ID of the primary field |
| `data[].fields` | `array` | List of fields in the table |
| `data[].views` | `array` | List of views in the table |

</details>

## Records

### Records List

Returns a paginated list of records from the specified table

#### Python SDK

```python
await airtable.records.list(
    base_id="<str>",
    table_id_or_name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "records",
    "action": "list",
    "params": {
        "base_id": "<str>",
        "table_id_or_name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `base_id` | `string` | Yes | The ID of the base |
| `table_id_or_name` | `string` | Yes | The ID or name of the table |
| `offset` | `string` | No | Pagination offset from previous response |
| `pageSize` | `integer` | No | Number of records per page (max 100) |
| `view` | `string` | No | Name or ID of a view to filter records |
| `filterByFormula` | `string` | No | Airtable formula to filter records |
| `sort` | `string` | No | Sort configuration as JSON array |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `createdTime` | `string \| null` |  |
| `fields` | `object \| null` |  |


</details>

### Records Get

Returns a single record by ID from the specified table

#### Python SDK

```python
await airtable.records.get(
    base_id="<str>",
    table_id_or_name="<str>",
    record_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "records",
    "action": "get",
    "params": {
        "base_id": "<str>",
        "table_id_or_name": "<str>",
        "record_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `base_id` | `string` | Yes | The ID of the base |
| `table_id_or_name` | `string` | Yes | The ID or name of the table |
| `record_id` | `string` | Yes | The ID of the record |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `createdTime` | `string \| null` |  |
| `fields` | `object \| null` |  |


</details>

