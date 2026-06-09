# Snowflake full reference

This is the full reference documentation for the Snowflake agent connector.

## Supported entities and actions

The Snowflake connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Databases | [List](#databases-list) |
| Schemas | [List](#schemas-list) |
| Tables | [List](#tables-list) |
| Views | [List](#views-list) |
| Warehouses | [List](#warehouses-list) |
| Columns | [List](#columns-list) |
| Record | [Get](#record-get), [List](#record-list), [Create](#record-create), [Update](#record-update), [Delete](#record-delete) |
| Result Partitions | [Get](#result-partitions-get) |

## Databases

### Databases List

List databases

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "databases",
  "action": "list"
}'
```

#### Python SDK

```python
await snowflake.databases.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "databases",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `"SHOW DATABASES"` | No | SQL statement to execute |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

## Schemas

### Schemas List

List schemas

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "schemas",
  "action": "list"
}'
```

#### Python SDK

```python
await snowflake.schemas.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "schemas",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `"SHOW SCHEMAS"` | No | SQL statement to execute |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

## Tables

### Tables List

List tables

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "tables",
  "action": "list"
}'
```

#### Python SDK

```python
await snowflake.tables.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tables",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `"SHOW TABLES"` | No | SQL statement to execute |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

## Views

### Views List

List views

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "views",
  "action": "list"
}'
```

#### Python SDK

```python
await snowflake.views.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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
| `statement` | `"SHOW VIEWS"` | No | SQL statement to execute |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

## Warehouses

### Warehouses List

List warehouses

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "warehouses",
  "action": "list"
}'
```

#### Python SDK

```python
await snowflake.warehouses.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "warehouses",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `"SHOW WAREHOUSES"` | No | SQL statement to execute |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

## Columns

### Columns List

List columns

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "columns",
  "action": "list"
}'
```

#### Python SDK

```python
await snowflake.columns.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "columns",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `"SHOW COLUMNS"` | No | SQL statement to execute |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

## Record

### Record Get

Execute a SQL SELECT statement and return the result set. Typically used to retrieve a single row by filtering on a unique identifier (e.g., SELECT * FROM users WHERE id = 42). The result is returned as rows, the same shape as the list action; when the SELECT targets one row the result contains a single row. Intended for row retrieval only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "record",
  "action": "get",
  "params": {
    "statement": "<str>"
  }
}'
```

#### Python SDK

```python
await snowflake.record.get(
    statement="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "record",
    "action": "get",
    "params": {
        "statement": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `string` | Yes | SQL SELECT statement to retrieve a single record (e.g., SELECT * FROM users WHERE id = 42) |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


</details>

### Record List

Execute a SQL SELECT query that returns multiple records from a Snowflake table or view. Use this action when you need to retrieve a set of rows, optionally with filtering, sorting, or limiting (e.g., SELECT * FROM orders WHERE status = 'active' ORDER BY created_at DESC LIMIT 100). Intended for row retrieval only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "record",
  "action": "list",
  "params": {
    "statement": "<str>"
  }
}'
```

#### Python SDK

```python
await snowflake.record.list(
    statement="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "record",
    "action": "list",
    "params": {
        "statement": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `string` | Yes | SQL SELECT statement to retrieve multiple records (e.g., SELECT * FROM orders WHERE status = 'active' LIMIT 100) |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_url` | `string` |  |
| `request_id` | `string` |  |
| `statement_handle` | `string` |  |
| `partition_info` | `array<object>` |  |

</details>

### Record Create

Execute a SQL INSERT statement to create one or more new rows in a Snowflake table (e.g., INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')). Intended for row insertion only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE TABLE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "record",
  "action": "create",
  "params": {
    "statement": "<str>",
    "database": "<str>",
    "schema": "<str>",
    "warehouse": "<str>",
    "role": "<str>",
    "timeout": 0,
    "parameters": {},
    "requestId": "<str>",
    "retry": true
  }
}'
```

#### Python SDK

```python
await snowflake.record.create(
    statement="<str>",
    database="<str>",
    schema="<str>",
    warehouse="<str>",
    role="<str>",
    timeout=0,
    parameters={},
    request_id="<str>",
    retry=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "record",
    "action": "create",
    "params": {
        "statement": "<str>",
        "database": "<str>",
        "schema": "<str>",
        "warehouse": "<str>",
        "role": "<str>",
        "timeout": 0,
        "parameters": {},
        "requestId": "<str>",
        "retry": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `string` | Yes | SQL INSERT statement to create new records (e.g., INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')) |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |
| `requestId` | `string` | No | Unique request ID for this DML statement. Reuse the SAME requestId when resubmitting after a network error or timeout so Snowflake deduplicates instead of executing the statement again. |
| `retry` | `boolean` | No | Set to true when resubmitting a previously-sent statement with the same requestId, so Snowflake treats it as a safe retry rather than a new DML. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


</details>

### Record Update

Execute a SQL UPDATE statement to modify existing rows in a Snowflake table (e.g., UPDATE users SET email = 'new@example.com' WHERE id = 7). Intended for row modification only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, ALTER) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "record",
  "action": "update",
  "params": {
    "statement": "<str>",
    "database": "<str>",
    "schema": "<str>",
    "warehouse": "<str>",
    "role": "<str>",
    "timeout": 0,
    "parameters": {},
    "requestId": "<str>",
    "retry": true
  }
}'
```

#### Python SDK

```python
await snowflake.record.update(
    statement="<str>",
    database="<str>",
    schema="<str>",
    warehouse="<str>",
    role="<str>",
    timeout=0,
    parameters={},
    request_id="<str>",
    retry=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "record",
    "action": "update",
    "params": {
        "statement": "<str>",
        "database": "<str>",
        "schema": "<str>",
        "warehouse": "<str>",
        "role": "<str>",
        "timeout": 0,
        "parameters": {},
        "requestId": "<str>",
        "retry": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `string` | Yes | SQL UPDATE statement to modify existing records (e.g., UPDATE users SET email = 'new@example.com' WHERE id = 7) |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |
| `requestId` | `string` | No | Unique request ID for this DML statement. Reuse the SAME requestId when resubmitting after a network error or timeout so Snowflake deduplicates instead of executing the statement again. |
| `retry` | `boolean` | No | Set to true when resubmitting a previously-sent statement with the same requestId, so Snowflake treats it as a safe retry rather than a new DML. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


</details>

### Record Delete

Execute a SQL DELETE statement to remove rows from a Snowflake table (e.g., DELETE FROM logs WHERE id = 99). Intended for row deletion only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "record",
  "action": "delete",
  "params": {
    "statement": "<str>"
  }
}'
```

#### Python SDK

```python
await snowflake.record.delete(
    statement="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "record",
    "action": "delete",
    "params": {
        "statement": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statement` | `string` | Yes | SQL DELETE statement to remove records (e.g., DELETE FROM logs WHERE id = 99) |
| `database` | `string` | No | Database context for the statement |
| `schema` | `string` | No | Schema context for the statement |
| `warehouse` | `string` | No | Warehouse to use for execution |
| `role` | `string` | No | Role to use for execution |
| `timeout` | `integer` | No | Timeout in seconds for the statement execution |
| `parameters` | `object` | No | Session parameters for the statement execution |
| `requestId` | `string` | No | Unique request ID for this DML statement. Reuse the SAME requestId when resubmitting after a network error or timeout so Snowflake deduplicates instead of executing the statement again. |
| `retry` | `boolean` | No | Set to true when resubmitting a previously-sent statement with the same requestId, so Snowflake treats it as a safe retry rather than a new DML. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


</details>

## Result Partitions

### Result Partitions Get

Continuation helper for Snowflake list actions. Use this only after a databases, schemas, tables, views, warehouses, or columns list response includes a next_page_url or multiple partitionInfo entries. The initial list response contains partition 0; call this action with partition 1, 2, and so on to retrieve additional rows for the same SHOW statement. This is not a standalone Snowflake resource and does not execute new SQL.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "snowflake",
  "entity": "result_partitions",
  "action": "get",
  "params": {
    "statementHandle": "<str>",
    "partition": 0
  }
}'
```

#### Python SDK

```python
await snowflake.result_partitions.get(
    statement_handle="<str>",
    partition=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "result_partitions",
    "action": "get",
    "params": {
        "statementHandle": "<str>",
        "partition": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `statementHandle` | `string` | Yes | Statement handle returned by the initial list response metadata. Reuse this value when fetching additional partitions for that same result set. |
| `partition` | `integer` | Yes | Zero-based partition number to retrieve. The initial list response contains partition 0; request partition 1 or higher for subsequent pages. |
| `requestId` | `string` | No | Optional request ID from the initial list response metadata. Pass it through when available to continue the same Snowflake SQL API request. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `requestId` | `string` |  |
| `resultSetMetaData` | `object` |  |
| `resultSetMetaData.numRows` | `integer` |  |
| `resultSetMetaData.format` | `string` |  |
| `resultSetMetaData.rowType` | `array<object>` |  |
| `resultSetMetaData.rowType[].name` | `string` |  |
| `resultSetMetaData.rowType[].database` | `string` |  |
| `resultSetMetaData.rowType[].schema` | `string` |  |
| `resultSetMetaData.rowType[].table` | `string` |  |
| `resultSetMetaData.rowType[].type` | `string` |  |
| `resultSetMetaData.rowType[].scale` | `integer \| any` |  |
| `resultSetMetaData.rowType[].precision` | `integer \| any` |  |
| `resultSetMetaData.rowType[].length` | `integer \| any` |  |
| `resultSetMetaData.rowType[].nullable` | `boolean` |  |
| `resultSetMetaData.rowType[].byteLength` | `integer \| any` |  |
| `resultSetMetaData.rowType[].collation` | `string \| any` |  |
| `resultSetMetaData.partitionInfo` | `array<object>` |  |
| `resultSetMetaData.partitionInfo[].rowCount` | `integer` |  |
| `resultSetMetaData.partitionInfo[].uncompressedSize` | `integer` |  |
| `resultSetMetaData.partitionInfo[].compressedSize` | `integer` |  |
| `data` | `array<array<string \| any>>` |  |
| `code` | `string` |  |
| `statementStatusUrl` | `string` |  |
| `sqlState` | `string` |  |
| `statementHandle` | `string` |  |
| `message` | `string` |  |
| `createdOn` | `integer` |  |
| `stats` | `object` |  |


</details>

