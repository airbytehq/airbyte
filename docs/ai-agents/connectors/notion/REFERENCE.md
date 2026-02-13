# Notion full reference

This is the full reference documentation for the Notion agent connector.

## Supported entities and actions

The Notion connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Pages | [List](#pages-list), [Get](#pages-get), [Search](#pages-search) |
| Databases | [List](#databases-list), [Get](#databases-get), [Search](#databases-search) |
| Blocks | [List](#blocks-list), [Get](#blocks-get), [Search](#blocks-search) |
| Comments | [List](#comments-list) |

## Users

### Users List

Returns a paginated list of users for the workspace

#### Python SDK

```python
await notion.users.list()
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
| `start_cursor` | `string` | No | Pagination cursor for next page |
| `page_size` | `integer` | No | Number of items per page (max 100) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `type` | `string \| null` |  |
| `name` | `string \| null` |  |
| `avatar_url` | `string \| null` |  |
| `person` | `object \| null` |  |
| `bot` | `object \| null` |  |
| `request_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Users Get

Retrieves a single user by ID

#### Python SDK

```python
await notion.users.get(
    user_id="<str>"
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
        "user_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user_id` | `string` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `type` | `string \| null` |  |
| `name` | `string \| null` |  |
| `avatar_url` | `string \| null` |  |
| `person` | `object \| null` |  |
| `bot` | `object \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await notion.users.search(
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
| `avatar_url` | `string` | URL of the user's avatar |
| `bot` | `object` | Bot-specific data |
| `id` | `string` | Unique identifier for the user |
| `name` | `string` | User's display name |
| `object` | `object` | Always user |
| `person` | `object` | Person-specific data |
| `type` | `object` | Type of user (person or bot) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].avatar_url` | `string` | URL of the user's avatar |
| `data[].bot` | `object` | Bot-specific data |
| `data[].id` | `string` | Unique identifier for the user |
| `data[].name` | `string` | User's display name |
| `data[].object` | `object` | Always user |
| `data[].person` | `object` | Person-specific data |
| `data[].type` | `object` | Type of user (person or bot) |

</details>

## Pages

### Pages List

Returns pages shared with the integration using the search endpoint

#### Python SDK

```python
await notion.pages.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pages",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.property` | `string` | No |  |
| `filter.value` | `string` | No |  |
| `sort` | `object` | No |  |
| `sort.direction` | `string` | No |  |
| `sort.timestamp` | `string` | No |  |
| `start_cursor` | `string` | No | Pagination cursor |
| `page_size` | `integer` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `last_edited_by` | `object \| null` |  |
| `cover` | `object \| null` |  |
| `icon` | `object \| null` |  |
| `parent` | `object \| any` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `properties` | `object \| null` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `request_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Pages Get

Retrieves a page object using the ID specified

#### Python SDK

```python
await notion.pages.get(
    page_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pages",
    "action": "get",
    "params": {
        "page_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_id` | `string` | Yes | Page ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `last_edited_by` | `object \| null` |  |
| `cover` | `object \| null` |  |
| `icon` | `object \| null` |  |
| `parent` | `object \| any` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `properties` | `object \| null` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Pages Search

Search and filter pages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await notion.pages.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pages",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates whether the page is archived or not. |
| `cover` | `object` | URL or reference to the page cover image. |
| `created_by` | `object` | User ID or name of the creator of the page. |
| `created_time` | `string` | Date and time when the page was created. |
| `icon` | `object` | URL or reference to the page icon. |
| `id` | `string` | Unique identifier of the page. |
| `in_trash` | `boolean` | Indicates whether the page is in trash or not. |
| `last_edited_by` | `object` | User ID or name of the last editor of the page. |
| `last_edited_time` | `string` | Date and time when the page was last edited. |
| `object` | `object` | Type or category of the page object. |
| `parent` | `object` | ID or reference to the parent page. |
| `properties` | `array` | Custom properties associated with the page. |
| `public_url` | `string` | Publicly accessible URL of the page. |
| `url` | `string` | URL of the page within the service. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates whether the page is archived or not. |
| `data[].cover` | `object` | URL or reference to the page cover image. |
| `data[].created_by` | `object` | User ID or name of the creator of the page. |
| `data[].created_time` | `string` | Date and time when the page was created. |
| `data[].icon` | `object` | URL or reference to the page icon. |
| `data[].id` | `string` | Unique identifier of the page. |
| `data[].in_trash` | `boolean` | Indicates whether the page is in trash or not. |
| `data[].last_edited_by` | `object` | User ID or name of the last editor of the page. |
| `data[].last_edited_time` | `string` | Date and time when the page was last edited. |
| `data[].object` | `object` | Type or category of the page object. |
| `data[].parent` | `object` | ID or reference to the parent page. |
| `data[].properties` | `array` | Custom properties associated with the page. |
| `data[].public_url` | `string` | Publicly accessible URL of the page. |
| `data[].url` | `string` | URL of the page within the service. |

</details>

## Databases

### Databases List

Returns databases shared with the integration using the search endpoint

#### Python SDK

```python
await notion.databases.list()
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
| `filter` | `object` | No |  |
| `filter.property` | `string` | No |  |
| `filter.value` | `string` | No |  |
| `sort` | `object` | No |  |
| `sort.direction` | `string` | No |  |
| `sort.timestamp` | `string` | No |  |
| `start_cursor` | `string` | No | Pagination cursor |
| `page_size` | `integer` | No |  |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `last_edited_by` | `object \| null` |  |
| `title` | `array \| null` |  |
| `title[].type` | `string \| null` |  |
| `title[].text` | `object \| null` |  |
| `title[].annotations` | `object \| null` |  |
| `title[].plain_text` | `string \| null` |  |
| `title[].href` | `string \| null` |  |
| `description` | `array \| null` |  |
| `description[].type` | `string \| null` |  |
| `description[].text` | `object \| null` |  |
| `description[].annotations` | `object \| null` |  |
| `description[].plain_text` | `string \| null` |  |
| `description[].href` | `string \| null` |  |
| `icon` | `object \| null` |  |
| `cover` | `object \| null` |  |
| `properties` | `object \| null` |  |
| `parent` | `object \| any` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_inline` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `request_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Databases Get

Retrieves a database object using the ID specified

#### Python SDK

```python
await notion.databases.get(
    database_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "databases",
    "action": "get",
    "params": {
        "database_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `database_id` | `string` | Yes | Database ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `last_edited_by` | `object \| null` |  |
| `title` | `array \| null` |  |
| `title[].type` | `string \| null` |  |
| `title[].text` | `object \| null` |  |
| `title[].annotations` | `object \| null` |  |
| `title[].plain_text` | `string \| null` |  |
| `title[].href` | `string \| null` |  |
| `description` | `array \| null` |  |
| `description[].type` | `string \| null` |  |
| `description[].text` | `object \| null` |  |
| `description[].annotations` | `object \| null` |  |
| `description[].plain_text` | `string \| null` |  |
| `description[].href` | `string \| null` |  |
| `icon` | `object \| null` |  |
| `cover` | `object \| null` |  |
| `properties` | `object \| null` |  |
| `parent` | `object \| any` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_inline` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Databases Search

Search and filter databases records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await notion.databases.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "databases",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates if the data is archived or not. |
| `cover` | `object` | URL or reference to the cover image of the database. |
| `created_by` | `object` | The user who created the database. |
| `created_time` | `string` | The timestamp when the database was created. |
| `description` | `array` | Description text associated with the database. |
| `icon` | `object` | URL or reference to the icon of the database. |
| `id` | `string` | Unique identifier of the database. |
| `is_inline` | `boolean` | Indicates if the database is displayed inline. |
| `last_edited_by` | `object` | The user who last edited the database. |
| `last_edited_time` | `string` | The timestamp when the database was last edited. |
| `object` | `object` | The type of object represented by the database. |
| `parent` | `object` | Indicates the parent database if it exists. |
| `properties` | `array` | List of key-value pairs defining additional properties of the database. |
| `public_url` | `string` | Public URL to access the database. |
| `title` | `array` | Title or name of the database. |
| `url` | `string` | URL or reference to access the database. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates if the data is archived or not. |
| `data[].cover` | `object` | URL or reference to the cover image of the database. |
| `data[].created_by` | `object` | The user who created the database. |
| `data[].created_time` | `string` | The timestamp when the database was created. |
| `data[].description` | `array` | Description text associated with the database. |
| `data[].icon` | `object` | URL or reference to the icon of the database. |
| `data[].id` | `string` | Unique identifier of the database. |
| `data[].is_inline` | `boolean` | Indicates if the database is displayed inline. |
| `data[].last_edited_by` | `object` | The user who last edited the database. |
| `data[].last_edited_time` | `string` | The timestamp when the database was last edited. |
| `data[].object` | `object` | The type of object represented by the database. |
| `data[].parent` | `object` | Indicates the parent database if it exists. |
| `data[].properties` | `array` | List of key-value pairs defining additional properties of the database. |
| `data[].public_url` | `string` | Public URL to access the database. |
| `data[].title` | `array` | Title or name of the database. |
| `data[].url` | `string` | URL or reference to access the database. |

</details>

## Blocks

### Blocks List

Returns a paginated list of child blocks for the specified block

#### Python SDK

```python
await notion.blocks.list(
    block_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blocks",
    "action": "list",
    "params": {
        "block_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `block_id` | `string` | Yes | Block or page ID |
| `start_cursor` | `string` | No | Pagination cursor for next page |
| `page_size` | `integer` | No | Number of items per page (max 100) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `type` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `last_edited_by` | `object \| null` |  |
| `has_children` | `boolean \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `parent` | `object \| any` |  |
| `paragraph` | `object \| null` |  |
| `heading_1` | `object \| null` |  |
| `heading_2` | `object \| null` |  |
| `heading_3` | `object \| null` |  |
| `bulleted_list_item` | `object \| null` |  |
| `numbered_list_item` | `object \| null` |  |
| `to_do` | `object \| null` |  |
| `toggle` | `object \| null` |  |
| `code` | `object \| null` |  |
| `child_page` | `object \| null` |  |
| `child_database` | `object \| null` |  |
| `callout` | `object \| null` |  |
| `quote` | `object \| null` |  |
| `divider` | `object \| null` |  |
| `table_of_contents` | `object \| null` |  |
| `bookmark` | `object \| null` |  |
| `image` | `object \| null` |  |
| `video` | `object \| null` |  |
| `file` | `object \| null` |  |
| `pdf` | `object \| null` |  |
| `embed` | `object \| null` |  |
| `equation` | `object \| null` |  |
| `table` | `object \| null` |  |
| `table_row` | `object \| null` |  |
| `request_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Blocks Get

Retrieves a block object using the ID specified

#### Python SDK

```python
await notion.blocks.get(
    block_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blocks",
    "action": "get",
    "params": {
        "block_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `block_id` | `string` | Yes | Block ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `type` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `last_edited_by` | `object \| null` |  |
| `has_children` | `boolean \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `parent` | `object \| any` |  |
| `paragraph` | `object \| null` |  |
| `heading_1` | `object \| null` |  |
| `heading_2` | `object \| null` |  |
| `heading_3` | `object \| null` |  |
| `bulleted_list_item` | `object \| null` |  |
| `numbered_list_item` | `object \| null` |  |
| `to_do` | `object \| null` |  |
| `toggle` | `object \| null` |  |
| `code` | `object \| null` |  |
| `child_page` | `object \| null` |  |
| `child_database` | `object \| null` |  |
| `callout` | `object \| null` |  |
| `quote` | `object \| null` |  |
| `divider` | `object \| null` |  |
| `table_of_contents` | `object \| null` |  |
| `bookmark` | `object \| null` |  |
| `image` | `object \| null` |  |
| `video` | `object \| null` |  |
| `file` | `object \| null` |  |
| `pdf` | `object \| null` |  |
| `embed` | `object \| null` |  |
| `equation` | `object \| null` |  |
| `table` | `object \| null` |  |
| `table_row` | `object \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Blocks Search

Search and filter blocks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await notion.blocks.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blocks",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Indicates if the block is archived or not. |
| `bookmark` | `object` | Represents a bookmark within the block |
| `breadcrumb` | `object` | Represents a breadcrumb block. |
| `bulleted_list_item` | `object` | Represents an item in a bulleted list. |
| `callout` | `object` | Describes a callout message or content in the block |
| `child_database` | `object` | Represents a child database block. |
| `child_page` | `object` | Represents a child page block. |
| `code` | `object` | Contains code snippets or blocks in the block content |
| `column` | `object` | Represents a column block. |
| `column_list` | `object` | Represents a list of columns. |
| `created_by` | `object` | The user who created the block. |
| `created_time` | `string` | The timestamp when the block was created. |
| `divider` | `object` | Represents a divider block. |
| `embed` | `object` | Contains embedded content such as videos, tweets, etc. |
| `equation` | `object` | Represents an equation or mathematical formula in the block |
| `file` | `object` | Represents a file block. |
| `has_children` | `boolean` | Indicates if the block has children or not. |
| `heading_1` | `object` | Represents a level 1 heading. |
| `heading_2` | `object` | Represents a level 2 heading. |
| `heading_3` | `object` | Represents a level 3 heading. |
| `id` | `string` | The unique identifier of the block. |
| `image` | `object` | Represents an image block. |
| `last_edited_by` | `object` | The user who last edited the block. |
| `last_edited_time` | `string` | The timestamp when the block was last edited. |
| `link_preview` | `object` | Displays a preview of an external link within the block |
| `link_to_page` | `object` | Provides a link to another page within the block |
| `numbered_list_item` | `object` | Represents an item in a numbered list. |
| `object` | `object` | Represents an object block. |
| `paragraph` | `object` | Represents a paragraph block. |
| `parent` | `object` | The parent block of the current block. |
| `pdf` | `object` | Represents a PDF document block. |
| `quote` | `object` | Represents a quote block. |
| `synced_block` | `object` | Represents a block synced from another source |
| `table` | `object` | Represents a table within the block |
| `table_of_contents` | `object` | Contains information regarding the table of contents |
| `table_row` | `object` | Represents a row in a table within the block |
| `template` | `object` | Specifies a template used within the block |
| `to_do` | `object` | Represents a to-do list or task content |
| `toggle` | `object` | Represents a toggle block. |
| `type` | `object` | The type of the block. |
| `unsupported` | `object` | Represents an unsupported block. |
| `video` | `object` | Represents a video block. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates if the block is archived or not. |
| `data[].bookmark` | `object` | Represents a bookmark within the block |
| `data[].breadcrumb` | `object` | Represents a breadcrumb block. |
| `data[].bulleted_list_item` | `object` | Represents an item in a bulleted list. |
| `data[].callout` | `object` | Describes a callout message or content in the block |
| `data[].child_database` | `object` | Represents a child database block. |
| `data[].child_page` | `object` | Represents a child page block. |
| `data[].code` | `object` | Contains code snippets or blocks in the block content |
| `data[].column` | `object` | Represents a column block. |
| `data[].column_list` | `object` | Represents a list of columns. |
| `data[].created_by` | `object` | The user who created the block. |
| `data[].created_time` | `string` | The timestamp when the block was created. |
| `data[].divider` | `object` | Represents a divider block. |
| `data[].embed` | `object` | Contains embedded content such as videos, tweets, etc. |
| `data[].equation` | `object` | Represents an equation or mathematical formula in the block |
| `data[].file` | `object` | Represents a file block. |
| `data[].has_children` | `boolean` | Indicates if the block has children or not. |
| `data[].heading_1` | `object` | Represents a level 1 heading. |
| `data[].heading_2` | `object` | Represents a level 2 heading. |
| `data[].heading_3` | `object` | Represents a level 3 heading. |
| `data[].id` | `string` | The unique identifier of the block. |
| `data[].image` | `object` | Represents an image block. |
| `data[].last_edited_by` | `object` | The user who last edited the block. |
| `data[].last_edited_time` | `string` | The timestamp when the block was last edited. |
| `data[].link_preview` | `object` | Displays a preview of an external link within the block |
| `data[].link_to_page` | `object` | Provides a link to another page within the block |
| `data[].numbered_list_item` | `object` | Represents an item in a numbered list. |
| `data[].object` | `object` | Represents an object block. |
| `data[].paragraph` | `object` | Represents a paragraph block. |
| `data[].parent` | `object` | The parent block of the current block. |
| `data[].pdf` | `object` | Represents a PDF document block. |
| `data[].quote` | `object` | Represents a quote block. |
| `data[].synced_block` | `object` | Represents a block synced from another source |
| `data[].table` | `object` | Represents a table within the block |
| `data[].table_of_contents` | `object` | Contains information regarding the table of contents |
| `data[].table_row` | `object` | Represents a row in a table within the block |
| `data[].template` | `object` | Specifies a template used within the block |
| `data[].to_do` | `object` | Represents a to-do list or task content |
| `data[].toggle` | `object` | Represents a toggle block. |
| `data[].type` | `object` | The type of the block. |
| `data[].unsupported` | `object` | Represents an unsupported block. |
| `data[].video` | `object` | Represents a video block. |

</details>

## Comments

### Comments List

Returns a list of comments for a specified block or page

#### Python SDK

```python
await notion.comments.list(
    block_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "list",
    "params": {
        "block_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `block_id` | `string` | Yes | Block or page ID to retrieve comments for |
| `start_cursor` | `string` | No | Pagination cursor for next page |
| `page_size` | `integer` | No | Number of items per page (max 100) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `parent` | `object \| any` |  |
| `discussion_id` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `last_edited_time` | `string \| null` |  |
| `created_by` | `object \| null` |  |
| `rich_text` | `array \| null` |  |
| `rich_text[].type` | `string \| null` |  |
| `rich_text[].text` | `object \| null` |  |
| `rich_text[].annotations` | `object \| null` |  |
| `rich_text[].plain_text` | `string \| null` |  |
| `rich_text[].href` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

