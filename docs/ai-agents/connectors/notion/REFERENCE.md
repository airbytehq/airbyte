# Notion full reference

This is the full reference documentation for the Notion agent connector.

## Supported entities and actions

The Notion connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get), [Context Store Search](#users-context-store-search) |
| Pages | [List](#pages-list), [Create](#pages-create), [Get](#pages-get), [Update](#pages-update), [Context Store Search](#pages-context-store-search) |
| Data Sources | [List](#data-sources-list), [Get](#data-sources-get), [Update](#data-sources-update), [Context Store Search](#data-sources-context-store-search) |
| Blocks | [List](#blocks-list), [Create](#blocks-create), [Get](#blocks-get), [Update](#blocks-update), [Context Store Search](#blocks-context-store-search) |
| Comments | [List](#comments-list), [Create](#comments-create), [Context Store Search](#comments-context-store-search) |

## Users

### Users List

Returns a paginated list of users for the workspace

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "users",
  "action": "list"
}'
```

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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "users",
  "action": "get",
  "params": {
    "user_id": "<str>"
  }
}'
```

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

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "users",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "avatar_url": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await notion.users.context_store_search(
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
    "action": "context_store_search",
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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "pages",
  "action": "list"
}'
```

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
| `is_archived` | `boolean \| null` |  |
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

### Pages Create

Creates a new page as a child of an existing page or data source

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "pages",
  "action": "create",
  "params": {
    "parent": {},
    "properties": {},
    "children": [],
    "icon": {},
    "cover": {}
  }
}'
```

#### Python SDK

```python
await notion.pages.create(
    parent={},
    properties={},
    children=[],
    icon={},
    cover={}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pages",
    "action": "create",
    "params": {
        "parent": {},
        "properties": {},
        "children": [],
        "icon": {},
        "cover": {}
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `parent` | `object` | Yes | Parent of the page. Provide exactly one of page_id, database_id, data_source_id, or workspace. |
| `properties` | `object` | No | Page properties. For pages under a page, use title property. For data source pages, match the data source schema. |
| `children` | `array<object>` | No | Content blocks to add to the page (max 100) |
| `icon` | `object \| null` | No | Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove. |
| `cover` | `object \| null` | No | Cover image. Supports external URL or file upload. Set to null to remove. |


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
| `is_archived` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `properties` | `object \| null` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Pages Get

Retrieves a page object using the ID specified

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "pages",
  "action": "get",
  "params": {
    "page_id": "<str>"
  }
}'
```

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
| `is_archived` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `properties` | `object \| null` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Pages Update

Updates page properties, icon, cover, or archived status

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "pages",
  "action": "update",
  "params": {
    "properties": {},
    "icon": {},
    "cover": {},
    "archived": true,
    "in_trash": true,
    "page_id": "<str>"
  }
}'
```

#### Python SDK

```python
await notion.pages.update(
    properties={},
    icon={},
    cover={},
    archived=True,
    in_trash=True,
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
    "action": "update",
    "params": {
        "properties": {},
        "icon": {},
        "cover": {},
        "archived": True,
        "in_trash": True,
        "page_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `properties` | `object` | No | Page property values to update. Keys must match the page's property schema. |
| `icon` | `object \| null` | No | Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove. |
| `cover` | `object \| null` | No | Cover image. Supports external URL or file upload. Set to null to remove. |
| `archived` | `boolean` | No | Set to true to archive the page, false to un-archive |
| `in_trash` | `boolean` | No | Set to true to move the page to trash, false to restore |
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
| `is_archived` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `properties` | `object \| null` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Pages Context Store Search

Search and filter pages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "pages",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await notion.pages.context_store_search(
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
    "action": "context_store_search",
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

## Data Sources

### Data Sources List

Returns data sources shared with the integration using the search endpoint

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "data_sources",
  "action": "list"
}'
```

#### Python SDK

```python
await notion.data_sources.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "data_sources",
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
| `database_parent` | `object \| any` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_archived` | `boolean \| null` |  |
| `is_inline` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `request_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Data Sources Get

Retrieves a data source object using the ID specified

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "data_sources",
  "action": "get",
  "params": {
    "data_source_id": "<str>"
  }
}'
```

#### Python SDK

```python
await notion.data_sources.get(
    data_source_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "data_sources",
    "action": "get",
    "params": {
        "data_source_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data_source_id` | `string` | Yes | Data Source ID |


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
| `database_parent` | `object \| any` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_archived` | `boolean \| null` |  |
| `is_inline` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Data Sources Update

Updates a data source's title, description, icon, properties, or trash status

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "data_sources",
  "action": "update",
  "params": {
    "title": [],
    "description": [],
    "properties": {},
    "icon": {},
    "cover": {},
    "archived": true,
    "in_trash": true,
    "data_source_id": "<str>"
  }
}'
```

#### Python SDK

```python
await notion.data_sources.update(
    title=[],
    description=[],
    properties={},
    icon={},
    cover={},
    archived=True,
    in_trash=True,
    data_source_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "data_sources",
    "action": "update",
    "params": {
        "title": [],
        "description": [],
        "properties": {},
        "icon": {},
        "cover": {},
        "archived": True,
        "in_trash": True,
        "data_source_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `array<object>` | No | Updated title of the data source as rich text |
| `title.type` | `string` | No |  |
| `title.text` | `object` | No |  |
| `title.text.content` | `string` | No |  |
| `title.text.link` | `object \| null` | No |  |
| `title.mention` | `object` | No |  |
| `title.equation` | `object` | No |  |
| `title.equation.expression` | `string` | No |  |
| `title.annotations` | `object` | No |  |
| `title.annotations.bold` | `boolean` | No |  |
| `title.annotations.italic` | `boolean` | No |  |
| `title.annotations.strikethrough` | `boolean` | No |  |
| `title.annotations.underline` | `boolean` | No |  |
| `title.annotations.code` | `boolean` | No |  |
| `title.annotations.color` | `string` | No |  |
| `description` | `array<object>` | No | Updated description of the data source as rich text |
| `description.type` | `string` | No |  |
| `description.text` | `object` | No |  |
| `description.text.content` | `string` | No |  |
| `description.text.link` | `object \| null` | No |  |
| `description.mention` | `object` | No |  |
| `description.equation` | `object` | No |  |
| `description.equation.expression` | `string` | No |  |
| `description.annotations` | `object` | No |  |
| `description.annotations.bold` | `boolean` | No |  |
| `description.annotations.italic` | `boolean` | No |  |
| `description.annotations.strikethrough` | `boolean` | No |  |
| `description.annotations.underline` | `boolean` | No |  |
| `description.annotations.code` | `boolean` | No |  |
| `description.annotations.color` | `string` | No |  |
| `properties` | `object` | No | Data source property schema to update. Keys are property names or IDs. Set a property to null to remove it. |
| `icon` | `object \| null` | No | Icon. Supports emoji, external URL, file upload, custom emoji, and Notion native icons. Set to null to remove. |
| `cover` | `object \| null` | No | Cover image. Supports external URL or file upload. Set to null to remove. |
| `archived` | `boolean` | No | Set to true to archive the data source |
| `in_trash` | `boolean` | No | Set to true to move the data source to trash |
| `data_source_id` | `string` | Yes | Data source ID |


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
| `database_parent` | `object \| any` |  |
| `url` | `string \| null` |  |
| `public_url` | `string \| null` |  |
| `archived` | `boolean \| null` |  |
| `in_trash` | `boolean \| null` |  |
| `is_archived` | `boolean \| null` |  |
| `is_inline` | `boolean \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Data Sources Context Store Search

Search and filter data sources records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "data_sources",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await notion.data_sources.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "data_sources",
    "action": "context_store_search",
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
| `archived` | `boolean` | Indicates if the data source is archived or not. |
| `cover` | `object` | URL or reference to the cover image of the data source. |
| `created_by` | `object` | The user who created the data source. |
| `created_time` | `string` | The timestamp when the data source was created. |
| `database_parent` | `object` | The grandparent of the data source (parent of the database). |
| `description` | `array` | Description text associated with the data source. |
| `icon` | `object` | URL or reference to the icon of the data source. |
| `id` | `string` | Unique identifier of the data source. |
| `is_inline` | `boolean` | Indicates if the data source is displayed inline. |
| `last_edited_by` | `object` | The user who last edited the data source. |
| `last_edited_time` | `string` | The timestamp when the data source was last edited. |
| `object` | `object` | The type of object (data_source). |
| `parent` | `object` | The parent database of the data source. |
| `properties` | `array` | Schema of properties for the data source. |
| `public_url` | `string` | Public URL to access the data source. |
| `title` | `array` | Title or name of the data source. |
| `url` | `string` | URL or reference to access the data source. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Indicates if the data source is archived or not. |
| `data[].cover` | `object` | URL or reference to the cover image of the data source. |
| `data[].created_by` | `object` | The user who created the data source. |
| `data[].created_time` | `string` | The timestamp when the data source was created. |
| `data[].database_parent` | `object` | The grandparent of the data source (parent of the database). |
| `data[].description` | `array` | Description text associated with the data source. |
| `data[].icon` | `object` | URL or reference to the icon of the data source. |
| `data[].id` | `string` | Unique identifier of the data source. |
| `data[].is_inline` | `boolean` | Indicates if the data source is displayed inline. |
| `data[].last_edited_by` | `object` | The user who last edited the data source. |
| `data[].last_edited_time` | `string` | The timestamp when the data source was last edited. |
| `data[].object` | `object` | The type of object (data_source). |
| `data[].parent` | `object` | The parent database of the data source. |
| `data[].properties` | `array` | Schema of properties for the data source. |
| `data[].public_url` | `string` | Public URL to access the data source. |
| `data[].title` | `array` | Title or name of the data source. |
| `data[].url` | `string` | URL or reference to access the data source. |

</details>

## Blocks

### Blocks List

Returns a paginated list of child blocks for the specified block

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "blocks",
  "action": "list",
  "params": {
    "block_id": "<str>"
  }
}'
```

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
| `column` | `object \| null` |  |
| `column_list` | `object \| null` |  |
| `synced_block` | `object \| null` |  |
| `template` | `object \| null` |  |
| `link_preview` | `object \| null` |  |
| `link_to_page` | `object \| null` |  |
| `breadcrumb` | `object \| null` |  |
| `unsupported` | `object \| null` |  |
| `request_id` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Blocks Create

Creates and appends new children blocks to the specified parent block or page

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "blocks",
  "action": "create",
  "params": {
    "children": [],
    "block_id": "<str>"
  }
}'
```

#### Python SDK

```python
await notion.blocks.create(
    children=[],
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
    "action": "create",
    "params": {
        "children": [],
        "block_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `children` | `array<object>` | Yes | Array of block objects to append (max 100). Each block must specify a type and corresponding content. |
| `children.type` | `string` | No | Block type: paragraph, heading_1, heading_2, heading_3, bulleted_list_item, numbered_list_item, to_do, toggle, code, quote, callout, divider, bookmark, embed, equation, table_of_contents, image, video, file, pdf, audio, column_list, column, table, synced_block, link_to_page, etc. |
| `children.paragraph` | `object` | No | Paragraph block content |
| `children.paragraph.rich_text` | `array<object>` | No |  |
| `children.paragraph.rich_text.type` | `string` | No |  |
| `children.paragraph.rich_text.text` | `object` | No |  |
| `children.paragraph.rich_text.text.content` | `string` | No |  |
| `children.paragraph.rich_text.text.link` | `object \| null` | No |  |
| `children.paragraph.rich_text.mention` | `object` | No |  |
| `children.paragraph.rich_text.equation` | `object` | No |  |
| `children.paragraph.rich_text.equation.expression` | `string` | No |  |
| `children.paragraph.rich_text.annotations` | `object` | No |  |
| `children.paragraph.rich_text.annotations.bold` | `boolean` | No |  |
| `children.paragraph.rich_text.annotations.italic` | `boolean` | No |  |
| `children.paragraph.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.paragraph.rich_text.annotations.underline` | `boolean` | No |  |
| `children.paragraph.rich_text.annotations.code` | `boolean` | No |  |
| `children.paragraph.rich_text.annotations.color` | `string` | No |  |
| `children.paragraph.color` | `string` | No |  |
| `children.heading_1` | `object` | No | Heading 1 block content |
| `children.heading_1.rich_text` | `array<object>` | No |  |
| `children.heading_1.rich_text.type` | `string` | No |  |
| `children.heading_1.rich_text.text` | `object` | No |  |
| `children.heading_1.rich_text.text.content` | `string` | No |  |
| `children.heading_1.rich_text.text.link` | `object \| null` | No |  |
| `children.heading_1.rich_text.mention` | `object` | No |  |
| `children.heading_1.rich_text.equation` | `object` | No |  |
| `children.heading_1.rich_text.equation.expression` | `string` | No |  |
| `children.heading_1.rich_text.annotations` | `object` | No |  |
| `children.heading_1.rich_text.annotations.bold` | `boolean` | No |  |
| `children.heading_1.rich_text.annotations.italic` | `boolean` | No |  |
| `children.heading_1.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.heading_1.rich_text.annotations.underline` | `boolean` | No |  |
| `children.heading_1.rich_text.annotations.code` | `boolean` | No |  |
| `children.heading_1.rich_text.annotations.color` | `string` | No |  |
| `children.heading_1.color` | `string` | No |  |
| `children.heading_1.is_toggleable` | `boolean` | No |  |
| `children.heading_2` | `object` | No | Heading 2 block content |
| `children.heading_2.rich_text` | `array<object>` | No |  |
| `children.heading_2.rich_text.type` | `string` | No |  |
| `children.heading_2.rich_text.text` | `object` | No |  |
| `children.heading_2.rich_text.text.content` | `string` | No |  |
| `children.heading_2.rich_text.text.link` | `object \| null` | No |  |
| `children.heading_2.rich_text.mention` | `object` | No |  |
| `children.heading_2.rich_text.equation` | `object` | No |  |
| `children.heading_2.rich_text.equation.expression` | `string` | No |  |
| `children.heading_2.rich_text.annotations` | `object` | No |  |
| `children.heading_2.rich_text.annotations.bold` | `boolean` | No |  |
| `children.heading_2.rich_text.annotations.italic` | `boolean` | No |  |
| `children.heading_2.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.heading_2.rich_text.annotations.underline` | `boolean` | No |  |
| `children.heading_2.rich_text.annotations.code` | `boolean` | No |  |
| `children.heading_2.rich_text.annotations.color` | `string` | No |  |
| `children.heading_2.color` | `string` | No |  |
| `children.heading_2.is_toggleable` | `boolean` | No |  |
| `children.heading_3` | `object` | No | Heading 3 block content |
| `children.heading_3.rich_text` | `array<object>` | No |  |
| `children.heading_3.rich_text.type` | `string` | No |  |
| `children.heading_3.rich_text.text` | `object` | No |  |
| `children.heading_3.rich_text.text.content` | `string` | No |  |
| `children.heading_3.rich_text.text.link` | `object \| null` | No |  |
| `children.heading_3.rich_text.mention` | `object` | No |  |
| `children.heading_3.rich_text.equation` | `object` | No |  |
| `children.heading_3.rich_text.equation.expression` | `string` | No |  |
| `children.heading_3.rich_text.annotations` | `object` | No |  |
| `children.heading_3.rich_text.annotations.bold` | `boolean` | No |  |
| `children.heading_3.rich_text.annotations.italic` | `boolean` | No |  |
| `children.heading_3.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.heading_3.rich_text.annotations.underline` | `boolean` | No |  |
| `children.heading_3.rich_text.annotations.code` | `boolean` | No |  |
| `children.heading_3.rich_text.annotations.color` | `string` | No |  |
| `children.heading_3.color` | `string` | No |  |
| `children.heading_3.is_toggleable` | `boolean` | No |  |
| `children.bulleted_list_item` | `object` | No | Bulleted list item content |
| `children.bulleted_list_item.rich_text` | `array<object>` | No |  |
| `children.bulleted_list_item.rich_text.type` | `string` | No |  |
| `children.bulleted_list_item.rich_text.text` | `object` | No |  |
| `children.bulleted_list_item.rich_text.text.content` | `string` | No |  |
| `children.bulleted_list_item.rich_text.text.link` | `object \| null` | No |  |
| `children.bulleted_list_item.rich_text.mention` | `object` | No |  |
| `children.bulleted_list_item.rich_text.equation` | `object` | No |  |
| `children.bulleted_list_item.rich_text.equation.expression` | `string` | No |  |
| `children.bulleted_list_item.rich_text.annotations` | `object` | No |  |
| `children.bulleted_list_item.rich_text.annotations.bold` | `boolean` | No |  |
| `children.bulleted_list_item.rich_text.annotations.italic` | `boolean` | No |  |
| `children.bulleted_list_item.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.bulleted_list_item.rich_text.annotations.underline` | `boolean` | No |  |
| `children.bulleted_list_item.rich_text.annotations.code` | `boolean` | No |  |
| `children.bulleted_list_item.rich_text.annotations.color` | `string` | No |  |
| `children.bulleted_list_item.color` | `string` | No |  |
| `children.numbered_list_item` | `object` | No | Numbered list item content |
| `children.numbered_list_item.rich_text` | `array<object>` | No |  |
| `children.numbered_list_item.rich_text.type` | `string` | No |  |
| `children.numbered_list_item.rich_text.text` | `object` | No |  |
| `children.numbered_list_item.rich_text.text.content` | `string` | No |  |
| `children.numbered_list_item.rich_text.text.link` | `object \| null` | No |  |
| `children.numbered_list_item.rich_text.mention` | `object` | No |  |
| `children.numbered_list_item.rich_text.equation` | `object` | No |  |
| `children.numbered_list_item.rich_text.equation.expression` | `string` | No |  |
| `children.numbered_list_item.rich_text.annotations` | `object` | No |  |
| `children.numbered_list_item.rich_text.annotations.bold` | `boolean` | No |  |
| `children.numbered_list_item.rich_text.annotations.italic` | `boolean` | No |  |
| `children.numbered_list_item.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.numbered_list_item.rich_text.annotations.underline` | `boolean` | No |  |
| `children.numbered_list_item.rich_text.annotations.code` | `boolean` | No |  |
| `children.numbered_list_item.rich_text.annotations.color` | `string` | No |  |
| `children.numbered_list_item.color` | `string` | No |  |
| `children.to_do` | `object` | No | To-do block content |
| `children.to_do.rich_text` | `array<object>` | No |  |
| `children.to_do.rich_text.type` | `string` | No |  |
| `children.to_do.rich_text.text` | `object` | No |  |
| `children.to_do.rich_text.text.content` | `string` | No |  |
| `children.to_do.rich_text.text.link` | `object \| null` | No |  |
| `children.to_do.rich_text.mention` | `object` | No |  |
| `children.to_do.rich_text.equation` | `object` | No |  |
| `children.to_do.rich_text.equation.expression` | `string` | No |  |
| `children.to_do.rich_text.annotations` | `object` | No |  |
| `children.to_do.rich_text.annotations.bold` | `boolean` | No |  |
| `children.to_do.rich_text.annotations.italic` | `boolean` | No |  |
| `children.to_do.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.to_do.rich_text.annotations.underline` | `boolean` | No |  |
| `children.to_do.rich_text.annotations.code` | `boolean` | No |  |
| `children.to_do.rich_text.annotations.color` | `string` | No |  |
| `children.to_do.checked` | `boolean` | No |  |
| `children.to_do.color` | `string` | No |  |
| `children.toggle` | `object` | No | Toggle block content |
| `children.toggle.rich_text` | `array<object>` | No |  |
| `children.toggle.rich_text.type` | `string` | No |  |
| `children.toggle.rich_text.text` | `object` | No |  |
| `children.toggle.rich_text.text.content` | `string` | No |  |
| `children.toggle.rich_text.text.link` | `object \| null` | No |  |
| `children.toggle.rich_text.mention` | `object` | No |  |
| `children.toggle.rich_text.equation` | `object` | No |  |
| `children.toggle.rich_text.equation.expression` | `string` | No |  |
| `children.toggle.rich_text.annotations` | `object` | No |  |
| `children.toggle.rich_text.annotations.bold` | `boolean` | No |  |
| `children.toggle.rich_text.annotations.italic` | `boolean` | No |  |
| `children.toggle.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.toggle.rich_text.annotations.underline` | `boolean` | No |  |
| `children.toggle.rich_text.annotations.code` | `boolean` | No |  |
| `children.toggle.rich_text.annotations.color` | `string` | No |  |
| `children.toggle.color` | `string` | No |  |
| `children.code` | `object` | No | Code block content |
| `children.code.rich_text` | `array<object>` | No |  |
| `children.code.rich_text.type` | `string` | No |  |
| `children.code.rich_text.text` | `object` | No |  |
| `children.code.rich_text.text.content` | `string` | No |  |
| `children.code.rich_text.text.link` | `object \| null` | No |  |
| `children.code.rich_text.mention` | `object` | No |  |
| `children.code.rich_text.equation` | `object` | No |  |
| `children.code.rich_text.equation.expression` | `string` | No |  |
| `children.code.rich_text.annotations` | `object` | No |  |
| `children.code.rich_text.annotations.bold` | `boolean` | No |  |
| `children.code.rich_text.annotations.italic` | `boolean` | No |  |
| `children.code.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.code.rich_text.annotations.underline` | `boolean` | No |  |
| `children.code.rich_text.annotations.code` | `boolean` | No |  |
| `children.code.rich_text.annotations.color` | `string` | No |  |
| `children.code.language` | `string` | No | Programming language for syntax highlighting |
| `children.quote` | `object` | No | Quote block content |
| `children.quote.rich_text` | `array<object>` | No |  |
| `children.quote.rich_text.type` | `string` | No |  |
| `children.quote.rich_text.text` | `object` | No |  |
| `children.quote.rich_text.text.content` | `string` | No |  |
| `children.quote.rich_text.text.link` | `object \| null` | No |  |
| `children.quote.rich_text.mention` | `object` | No |  |
| `children.quote.rich_text.equation` | `object` | No |  |
| `children.quote.rich_text.equation.expression` | `string` | No |  |
| `children.quote.rich_text.annotations` | `object` | No |  |
| `children.quote.rich_text.annotations.bold` | `boolean` | No |  |
| `children.quote.rich_text.annotations.italic` | `boolean` | No |  |
| `children.quote.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.quote.rich_text.annotations.underline` | `boolean` | No |  |
| `children.quote.rich_text.annotations.code` | `boolean` | No |  |
| `children.quote.rich_text.annotations.color` | `string` | No |  |
| `children.quote.color` | `string` | No |  |
| `children.callout` | `object` | No | Callout block content |
| `children.callout.rich_text` | `array<object>` | No |  |
| `children.callout.rich_text.type` | `string` | No |  |
| `children.callout.rich_text.text` | `object` | No |  |
| `children.callout.rich_text.text.content` | `string` | No |  |
| `children.callout.rich_text.text.link` | `object \| null` | No |  |
| `children.callout.rich_text.mention` | `object` | No |  |
| `children.callout.rich_text.equation` | `object` | No |  |
| `children.callout.rich_text.equation.expression` | `string` | No |  |
| `children.callout.rich_text.annotations` | `object` | No |  |
| `children.callout.rich_text.annotations.bold` | `boolean` | No |  |
| `children.callout.rich_text.annotations.italic` | `boolean` | No |  |
| `children.callout.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `children.callout.rich_text.annotations.underline` | `boolean` | No |  |
| `children.callout.rich_text.annotations.code` | `boolean` | No |  |
| `children.callout.rich_text.annotations.color` | `string` | No |  |
| `children.callout.icon` | `object` | No |  |
| `children.callout.color` | `string` | No |  |
| `children.divider` | `object` | No | Divider block (empty object) |
| `children.bookmark` | `object` | No | Bookmark block |
| `children.bookmark.url` | `string` | No | URL to bookmark |
| `children.bookmark.caption` | `array<object>` | No |  |
| `children.bookmark.caption.type` | `string` | No |  |
| `children.bookmark.caption.text` | `object` | No |  |
| `children.bookmark.caption.text.content` | `string` | No |  |
| `children.bookmark.caption.text.link` | `object \| null` | No |  |
| `children.bookmark.caption.mention` | `object` | No |  |
| `children.bookmark.caption.equation` | `object` | No |  |
| `children.bookmark.caption.equation.expression` | `string` | No |  |
| `children.bookmark.caption.annotations` | `object` | No |  |
| `children.bookmark.caption.annotations.bold` | `boolean` | No |  |
| `children.bookmark.caption.annotations.italic` | `boolean` | No |  |
| `children.bookmark.caption.annotations.strikethrough` | `boolean` | No |  |
| `children.bookmark.caption.annotations.underline` | `boolean` | No |  |
| `children.bookmark.caption.annotations.code` | `boolean` | No |  |
| `children.bookmark.caption.annotations.color` | `string` | No |  |
| `children.embed` | `object` | No | Embed block |
| `children.embed.url` | `string` | No | URL to embed |
| `children.equation` | `object` | No | Equation block |
| `children.equation.expression` | `string` | No | LaTeX expression |
| `children.table_of_contents` | `object` | No | Table of contents block |
| `children.table_of_contents.color` | `string` | No |  |
| `children.image` | `object` | No | Media file. Use external URL or file upload. |
| `children.image.type` | `string` | No | File type: external or file_upload |
| `children.image.external` | `object` | No |  |
| `children.image.external.url` | `string` | No |  |
| `children.image.file_upload` | `object` | No |  |
| `children.image.file_upload.id` | `string` | No |  |
| `children.video` | `object` | No | Media file. Use external URL or file upload. |
| `children.video.type` | `string` | No | File type: external or file_upload |
| `children.video.external` | `object` | No |  |
| `children.video.external.url` | `string` | No |  |
| `children.video.file_upload` | `object` | No |  |
| `children.video.file_upload.id` | `string` | No |  |
| `children.file` | `object` | No | Media file. Use external URL or file upload. |
| `children.file.type` | `string` | No | File type: external or file_upload |
| `children.file.external` | `object` | No |  |
| `children.file.external.url` | `string` | No |  |
| `children.file.file_upload` | `object` | No |  |
| `children.file.file_upload.id` | `string` | No |  |
| `children.pdf` | `object` | No | Media file. Use external URL or file upload. |
| `children.pdf.type` | `string` | No | File type: external or file_upload |
| `children.pdf.external` | `object` | No |  |
| `children.pdf.external.url` | `string` | No |  |
| `children.pdf.file_upload` | `object` | No |  |
| `children.pdf.file_upload.id` | `string` | No |  |
| `children.audio` | `object` | No | Media file. Use external URL or file upload. |
| `children.audio.type` | `string` | No | File type: external or file_upload |
| `children.audio.external` | `object` | No |  |
| `children.audio.external.url` | `string` | No |  |
| `children.audio.file_upload` | `object` | No |  |
| `children.audio.file_upload.id` | `string` | No |  |
| `block_id` | `string` | Yes | Block or page ID to append children to |


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
| `column` | `object \| null` |  |
| `column_list` | `object \| null` |  |
| `synced_block` | `object \| null` |  |
| `template` | `object \| null` |  |
| `link_preview` | `object \| null` |  |
| `link_to_page` | `object \| null` |  |
| `breadcrumb` | `object \| null` |  |
| `unsupported` | `object \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Blocks Get

Retrieves a block object using the ID specified

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "blocks",
  "action": "get",
  "params": {
    "block_id": "<str>"
  }
}'
```

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
| `column` | `object \| null` |  |
| `column_list` | `object \| null` |  |
| `synced_block` | `object \| null` |  |
| `template` | `object \| null` |  |
| `link_preview` | `object \| null` |  |
| `link_to_page` | `object \| null` |  |
| `breadcrumb` | `object \| null` |  |
| `unsupported` | `object \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Blocks Update

Updates the content of a block based on its type

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "blocks",
  "action": "update",
  "params": {
    "paragraph": {},
    "heading_1": {},
    "heading_2": {},
    "heading_3": {},
    "bulleted_list_item": {},
    "numbered_list_item": {},
    "to_do": {},
    "toggle": {},
    "code": {},
    "quote": {},
    "callout": {},
    "bookmark": {},
    "embed": {},
    "equation": {},
    "image": {},
    "video": {},
    "file": {},
    "pdf": {},
    "audio": {},
    "table": {},
    "archived": true,
    "block_id": "<str>"
  }
}'
```

#### Python SDK

```python
await notion.blocks.update(
    paragraph={},
    heading_1={},
    heading_2={},
    heading_3={},
    bulleted_list_item={},
    numbered_list_item={},
    to_do={},
    toggle={},
    code={},
    quote={},
    callout={},
    bookmark={},
    embed={},
    equation={},
    image={},
    video={},
    file={},
    pdf={},
    audio={},
    table={},
    archived=True,
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
    "action": "update",
    "params": {
        "paragraph": {},
        "heading_1": {},
        "heading_2": {},
        "heading_3": {},
        "bulleted_list_item": {},
        "numbered_list_item": {},
        "to_do": {},
        "toggle": {},
        "code": {},
        "quote": {},
        "callout": {},
        "bookmark": {},
        "embed": {},
        "equation": {},
        "image": {},
        "video": {},
        "file": {},
        "pdf": {},
        "audio": {},
        "table": {},
        "archived": True,
        "block_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `paragraph` | `object` | No | Updated paragraph content |
| `paragraph.rich_text` | `array<object>` | No |  |
| `paragraph.rich_text.type` | `string` | No |  |
| `paragraph.rich_text.text` | `object` | No |  |
| `paragraph.rich_text.text.content` | `string` | No |  |
| `paragraph.rich_text.text.link` | `object \| null` | No |  |
| `paragraph.rich_text.mention` | `object` | No |  |
| `paragraph.rich_text.equation` | `object` | No |  |
| `paragraph.rich_text.equation.expression` | `string` | No |  |
| `paragraph.rich_text.annotations` | `object` | No |  |
| `paragraph.rich_text.annotations.bold` | `boolean` | No |  |
| `paragraph.rich_text.annotations.italic` | `boolean` | No |  |
| `paragraph.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `paragraph.rich_text.annotations.underline` | `boolean` | No |  |
| `paragraph.rich_text.annotations.code` | `boolean` | No |  |
| `paragraph.rich_text.annotations.color` | `string` | No |  |
| `paragraph.color` | `string` | No |  |
| `heading_1` | `object` | No | Updated heading 1 content |
| `heading_1.rich_text` | `array<object>` | No |  |
| `heading_1.rich_text.type` | `string` | No |  |
| `heading_1.rich_text.text` | `object` | No |  |
| `heading_1.rich_text.text.content` | `string` | No |  |
| `heading_1.rich_text.text.link` | `object \| null` | No |  |
| `heading_1.rich_text.mention` | `object` | No |  |
| `heading_1.rich_text.equation` | `object` | No |  |
| `heading_1.rich_text.equation.expression` | `string` | No |  |
| `heading_1.rich_text.annotations` | `object` | No |  |
| `heading_1.rich_text.annotations.bold` | `boolean` | No |  |
| `heading_1.rich_text.annotations.italic` | `boolean` | No |  |
| `heading_1.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `heading_1.rich_text.annotations.underline` | `boolean` | No |  |
| `heading_1.rich_text.annotations.code` | `boolean` | No |  |
| `heading_1.rich_text.annotations.color` | `string` | No |  |
| `heading_1.color` | `string` | No |  |
| `heading_1.is_toggleable` | `boolean` | No |  |
| `heading_2` | `object` | No | Updated heading 2 content |
| `heading_2.rich_text` | `array<object>` | No |  |
| `heading_2.rich_text.type` | `string` | No |  |
| `heading_2.rich_text.text` | `object` | No |  |
| `heading_2.rich_text.text.content` | `string` | No |  |
| `heading_2.rich_text.text.link` | `object \| null` | No |  |
| `heading_2.rich_text.mention` | `object` | No |  |
| `heading_2.rich_text.equation` | `object` | No |  |
| `heading_2.rich_text.equation.expression` | `string` | No |  |
| `heading_2.rich_text.annotations` | `object` | No |  |
| `heading_2.rich_text.annotations.bold` | `boolean` | No |  |
| `heading_2.rich_text.annotations.italic` | `boolean` | No |  |
| `heading_2.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `heading_2.rich_text.annotations.underline` | `boolean` | No |  |
| `heading_2.rich_text.annotations.code` | `boolean` | No |  |
| `heading_2.rich_text.annotations.color` | `string` | No |  |
| `heading_2.color` | `string` | No |  |
| `heading_2.is_toggleable` | `boolean` | No |  |
| `heading_3` | `object` | No | Updated heading 3 content |
| `heading_3.rich_text` | `array<object>` | No |  |
| `heading_3.rich_text.type` | `string` | No |  |
| `heading_3.rich_text.text` | `object` | No |  |
| `heading_3.rich_text.text.content` | `string` | No |  |
| `heading_3.rich_text.text.link` | `object \| null` | No |  |
| `heading_3.rich_text.mention` | `object` | No |  |
| `heading_3.rich_text.equation` | `object` | No |  |
| `heading_3.rich_text.equation.expression` | `string` | No |  |
| `heading_3.rich_text.annotations` | `object` | No |  |
| `heading_3.rich_text.annotations.bold` | `boolean` | No |  |
| `heading_3.rich_text.annotations.italic` | `boolean` | No |  |
| `heading_3.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `heading_3.rich_text.annotations.underline` | `boolean` | No |  |
| `heading_3.rich_text.annotations.code` | `boolean` | No |  |
| `heading_3.rich_text.annotations.color` | `string` | No |  |
| `heading_3.color` | `string` | No |  |
| `heading_3.is_toggleable` | `boolean` | No |  |
| `bulleted_list_item` | `object` | No | Updated bulleted list item |
| `bulleted_list_item.rich_text` | `array<object>` | No |  |
| `bulleted_list_item.rich_text.type` | `string` | No |  |
| `bulleted_list_item.rich_text.text` | `object` | No |  |
| `bulleted_list_item.rich_text.text.content` | `string` | No |  |
| `bulleted_list_item.rich_text.text.link` | `object \| null` | No |  |
| `bulleted_list_item.rich_text.mention` | `object` | No |  |
| `bulleted_list_item.rich_text.equation` | `object` | No |  |
| `bulleted_list_item.rich_text.equation.expression` | `string` | No |  |
| `bulleted_list_item.rich_text.annotations` | `object` | No |  |
| `bulleted_list_item.rich_text.annotations.bold` | `boolean` | No |  |
| `bulleted_list_item.rich_text.annotations.italic` | `boolean` | No |  |
| `bulleted_list_item.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `bulleted_list_item.rich_text.annotations.underline` | `boolean` | No |  |
| `bulleted_list_item.rich_text.annotations.code` | `boolean` | No |  |
| `bulleted_list_item.rich_text.annotations.color` | `string` | No |  |
| `bulleted_list_item.color` | `string` | No |  |
| `numbered_list_item` | `object` | No | Updated numbered list item |
| `numbered_list_item.rich_text` | `array<object>` | No |  |
| `numbered_list_item.rich_text.type` | `string` | No |  |
| `numbered_list_item.rich_text.text` | `object` | No |  |
| `numbered_list_item.rich_text.text.content` | `string` | No |  |
| `numbered_list_item.rich_text.text.link` | `object \| null` | No |  |
| `numbered_list_item.rich_text.mention` | `object` | No |  |
| `numbered_list_item.rich_text.equation` | `object` | No |  |
| `numbered_list_item.rich_text.equation.expression` | `string` | No |  |
| `numbered_list_item.rich_text.annotations` | `object` | No |  |
| `numbered_list_item.rich_text.annotations.bold` | `boolean` | No |  |
| `numbered_list_item.rich_text.annotations.italic` | `boolean` | No |  |
| `numbered_list_item.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `numbered_list_item.rich_text.annotations.underline` | `boolean` | No |  |
| `numbered_list_item.rich_text.annotations.code` | `boolean` | No |  |
| `numbered_list_item.rich_text.annotations.color` | `string` | No |  |
| `numbered_list_item.color` | `string` | No |  |
| `to_do` | `object` | No | Updated to-do content |
| `to_do.rich_text` | `array<object>` | No |  |
| `to_do.rich_text.type` | `string` | No |  |
| `to_do.rich_text.text` | `object` | No |  |
| `to_do.rich_text.text.content` | `string` | No |  |
| `to_do.rich_text.text.link` | `object \| null` | No |  |
| `to_do.rich_text.mention` | `object` | No |  |
| `to_do.rich_text.equation` | `object` | No |  |
| `to_do.rich_text.equation.expression` | `string` | No |  |
| `to_do.rich_text.annotations` | `object` | No |  |
| `to_do.rich_text.annotations.bold` | `boolean` | No |  |
| `to_do.rich_text.annotations.italic` | `boolean` | No |  |
| `to_do.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `to_do.rich_text.annotations.underline` | `boolean` | No |  |
| `to_do.rich_text.annotations.code` | `boolean` | No |  |
| `to_do.rich_text.annotations.color` | `string` | No |  |
| `to_do.checked` | `boolean` | No |  |
| `to_do.color` | `string` | No |  |
| `toggle` | `object` | No | Updated toggle content |
| `toggle.rich_text` | `array<object>` | No |  |
| `toggle.rich_text.type` | `string` | No |  |
| `toggle.rich_text.text` | `object` | No |  |
| `toggle.rich_text.text.content` | `string` | No |  |
| `toggle.rich_text.text.link` | `object \| null` | No |  |
| `toggle.rich_text.mention` | `object` | No |  |
| `toggle.rich_text.equation` | `object` | No |  |
| `toggle.rich_text.equation.expression` | `string` | No |  |
| `toggle.rich_text.annotations` | `object` | No |  |
| `toggle.rich_text.annotations.bold` | `boolean` | No |  |
| `toggle.rich_text.annotations.italic` | `boolean` | No |  |
| `toggle.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `toggle.rich_text.annotations.underline` | `boolean` | No |  |
| `toggle.rich_text.annotations.code` | `boolean` | No |  |
| `toggle.rich_text.annotations.color` | `string` | No |  |
| `toggle.color` | `string` | No |  |
| `code` | `object` | No | Updated code block content |
| `code.rich_text` | `array<object>` | No |  |
| `code.rich_text.type` | `string` | No |  |
| `code.rich_text.text` | `object` | No |  |
| `code.rich_text.text.content` | `string` | No |  |
| `code.rich_text.text.link` | `object \| null` | No |  |
| `code.rich_text.mention` | `object` | No |  |
| `code.rich_text.equation` | `object` | No |  |
| `code.rich_text.equation.expression` | `string` | No |  |
| `code.rich_text.annotations` | `object` | No |  |
| `code.rich_text.annotations.bold` | `boolean` | No |  |
| `code.rich_text.annotations.italic` | `boolean` | No |  |
| `code.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `code.rich_text.annotations.underline` | `boolean` | No |  |
| `code.rich_text.annotations.code` | `boolean` | No |  |
| `code.rich_text.annotations.color` | `string` | No |  |
| `code.language` | `string` | No |  |
| `code.caption` | `array<object>` | No |  |
| `code.caption.type` | `string` | No |  |
| `code.caption.text` | `object` | No |  |
| `code.caption.text.content` | `string` | No |  |
| `code.caption.text.link` | `object \| null` | No |  |
| `code.caption.mention` | `object` | No |  |
| `code.caption.equation` | `object` | No |  |
| `code.caption.equation.expression` | `string` | No |  |
| `code.caption.annotations` | `object` | No |  |
| `code.caption.annotations.bold` | `boolean` | No |  |
| `code.caption.annotations.italic` | `boolean` | No |  |
| `code.caption.annotations.strikethrough` | `boolean` | No |  |
| `code.caption.annotations.underline` | `boolean` | No |  |
| `code.caption.annotations.code` | `boolean` | No |  |
| `code.caption.annotations.color` | `string` | No |  |
| `quote` | `object` | No | Updated quote content |
| `quote.rich_text` | `array<object>` | No |  |
| `quote.rich_text.type` | `string` | No |  |
| `quote.rich_text.text` | `object` | No |  |
| `quote.rich_text.text.content` | `string` | No |  |
| `quote.rich_text.text.link` | `object \| null` | No |  |
| `quote.rich_text.mention` | `object` | No |  |
| `quote.rich_text.equation` | `object` | No |  |
| `quote.rich_text.equation.expression` | `string` | No |  |
| `quote.rich_text.annotations` | `object` | No |  |
| `quote.rich_text.annotations.bold` | `boolean` | No |  |
| `quote.rich_text.annotations.italic` | `boolean` | No |  |
| `quote.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `quote.rich_text.annotations.underline` | `boolean` | No |  |
| `quote.rich_text.annotations.code` | `boolean` | No |  |
| `quote.rich_text.annotations.color` | `string` | No |  |
| `quote.color` | `string` | No |  |
| `callout` | `object` | No | Updated callout content |
| `callout.rich_text` | `array<object>` | No |  |
| `callout.rich_text.type` | `string` | No |  |
| `callout.rich_text.text` | `object` | No |  |
| `callout.rich_text.text.content` | `string` | No |  |
| `callout.rich_text.text.link` | `object \| null` | No |  |
| `callout.rich_text.mention` | `object` | No |  |
| `callout.rich_text.equation` | `object` | No |  |
| `callout.rich_text.equation.expression` | `string` | No |  |
| `callout.rich_text.annotations` | `object` | No |  |
| `callout.rich_text.annotations.bold` | `boolean` | No |  |
| `callout.rich_text.annotations.italic` | `boolean` | No |  |
| `callout.rich_text.annotations.strikethrough` | `boolean` | No |  |
| `callout.rich_text.annotations.underline` | `boolean` | No |  |
| `callout.rich_text.annotations.code` | `boolean` | No |  |
| `callout.rich_text.annotations.color` | `string` | No |  |
| `callout.icon` | `object` | No |  |
| `callout.color` | `string` | No |  |
| `bookmark` | `object` | No | Updated bookmark |
| `bookmark.url` | `string` | No |  |
| `bookmark.caption` | `array<object>` | No |  |
| `bookmark.caption.type` | `string` | No |  |
| `bookmark.caption.text` | `object` | No |  |
| `bookmark.caption.text.content` | `string` | No |  |
| `bookmark.caption.text.link` | `object \| null` | No |  |
| `bookmark.caption.mention` | `object` | No |  |
| `bookmark.caption.equation` | `object` | No |  |
| `bookmark.caption.equation.expression` | `string` | No |  |
| `bookmark.caption.annotations` | `object` | No |  |
| `bookmark.caption.annotations.bold` | `boolean` | No |  |
| `bookmark.caption.annotations.italic` | `boolean` | No |  |
| `bookmark.caption.annotations.strikethrough` | `boolean` | No |  |
| `bookmark.caption.annotations.underline` | `boolean` | No |  |
| `bookmark.caption.annotations.code` | `boolean` | No |  |
| `bookmark.caption.annotations.color` | `string` | No |  |
| `embed` | `object` | No | Updated embed |
| `embed.url` | `string` | No |  |
| `equation` | `object` | No | Updated equation |
| `equation.expression` | `string` | No |  |
| `image` | `object` | No | Media file. Use external URL or file upload. |
| `image.type` | `string` | No | File type: external or file_upload |
| `image.external` | `object` | No |  |
| `image.external.url` | `string` | No |  |
| `image.file_upload` | `object` | No |  |
| `image.file_upload.id` | `string` | No |  |
| `video` | `object` | No | Media file. Use external URL or file upload. |
| `video.type` | `string` | No | File type: external or file_upload |
| `video.external` | `object` | No |  |
| `video.external.url` | `string` | No |  |
| `video.file_upload` | `object` | No |  |
| `video.file_upload.id` | `string` | No |  |
| `file` | `object` | No | Media file. Use external URL or file upload. |
| `file.type` | `string` | No | File type: external or file_upload |
| `file.external` | `object` | No |  |
| `file.external.url` | `string` | No |  |
| `file.file_upload` | `object` | No |  |
| `file.file_upload.id` | `string` | No |  |
| `pdf` | `object` | No | Media file. Use external URL or file upload. |
| `pdf.type` | `string` | No | File type: external or file_upload |
| `pdf.external` | `object` | No |  |
| `pdf.external.url` | `string` | No |  |
| `pdf.file_upload` | `object` | No |  |
| `pdf.file_upload.id` | `string` | No |  |
| `audio` | `object` | No | Media file. Use external URL or file upload. |
| `audio.type` | `string` | No | File type: external or file_upload |
| `audio.external` | `object` | No |  |
| `audio.external.url` | `string` | No |  |
| `audio.file_upload` | `object` | No |  |
| `audio.file_upload.id` | `string` | No |  |
| `table` | `object` | No | Updated table properties |
| `table.has_column_header` | `boolean` | No |  |
| `table.has_row_header` | `boolean` | No |  |
| `archived` | `boolean` | No | Set to true to archive the block (API version 2025-09-03) |
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
| `column` | `object \| null` |  |
| `column_list` | `object \| null` |  |
| `synced_block` | `object \| null` |  |
| `template` | `object \| null` |  |
| `link_preview` | `object \| null` |  |
| `link_to_page` | `object \| null` |  |
| `breadcrumb` | `object \| null` |  |
| `unsupported` | `object \| null` |  |
| `request_id` | `string \| null` |  |


</details>

### Blocks Context Store Search

Search and filter blocks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "blocks",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await notion.blocks.context_store_search(
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
    "action": "context_store_search",
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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "comments",
  "action": "list",
  "params": {
    "block_id": "<str>"
  }
}'
```

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

### Comments Create

Creates a comment on a page or block, or replies to an existing discussion thread

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "comments",
  "action": "create",
  "params": {
    "parent": {},
    "discussion_id": "<str>",
    "rich_text": []
  }
}'
```

#### Python SDK

```python
await notion.comments.create(
    parent={},
    discussion_id="<str>",
    rich_text=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "create",
    "params": {
        "parent": {},
        "discussion_id": "<str>",
        "rich_text": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `parent` | `object` | No | Parent of the comment. Provide exactly one of page_id or block_id. Mutually exclusive with discussion_id. |
| `discussion_id` | `string` | No | ID of an existing discussion thread to reply to. Mutually exclusive with parent. |
| `rich_text` | `array<object>` | Yes | Content of the comment as rich text |
| `rich_text.type` | `string` | No |  |
| `rich_text.text` | `object` | No |  |
| `rich_text.text.content` | `string` | No |  |
| `rich_text.text.link` | `object \| null` | No |  |
| `rich_text.mention` | `object` | No |  |
| `rich_text.equation` | `object` | No |  |
| `rich_text.equation.expression` | `string` | No |  |
| `rich_text.annotations` | `object` | No |  |
| `rich_text.annotations.bold` | `boolean` | No |  |
| `rich_text.annotations.italic` | `boolean` | No |  |
| `rich_text.annotations.strikethrough` | `boolean` | No |  |
| `rich_text.annotations.underline` | `boolean` | No |  |
| `rich_text.annotations.code` | `boolean` | No |  |
| `rich_text.annotations.color` | `string` | No |  |


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


</details>

### Comments Context Store Search

Search and filter comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "notion",
  "entity": "comments",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "created_by": {}
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await notion.comments.context_store_search(
    query={"filter": {"eq": {"created_by": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"created_by": {}}}}
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
| `created_by` | `object` | User who created the comment. |
| `created_time` | `string` | Date and time when the comment was created. |
| `discussion_id` | `string` | Discussion thread ID. |
| `id` | `string` | Unique identifier for the comment. |
| `last_edited_time` | `string` | Date and time when the comment was last edited. |
| `object` | `string` | Always comment. |
| `parent` | `object` | Parent of the comment. |
| `rich_text` | `array` | Content of the comment as rich text. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_by` | `object` | User who created the comment. |
| `data[].created_time` | `string` | Date and time when the comment was created. |
| `data[].discussion_id` | `string` | Discussion thread ID. |
| `data[].id` | `string` | Unique identifier for the comment. |
| `data[].last_edited_time` | `string` | Date and time when the comment was last edited. |
| `data[].object` | `string` | Always comment. |
| `data[].parent` | `object` | Parent of the comment. |
| `data[].rich_text` | `array` | Content of the comment as rich text. |

</details>

