# Monday full reference

This is the full reference documentation for the Monday agent connector.

## Supported entities and actions

The Monday connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get), [Context Store Search](#users-context-store-search) |
| Boards | [List](#boards-list), [Get](#boards-get), [Context Store Search](#boards-context-store-search) |
| Items | [List](#items-list), [Get](#items-get), [Context Store Search](#items-context-store-search) |
| Teams | [List](#teams-list), [Get](#teams-get), [Context Store Search](#teams-context-store-search) |
| Tags | [List](#tags-list), [Context Store Search](#tags-context-store-search) |
| Updates | [List](#updates-list), [Get](#updates-get), [Context Store Search](#updates-context-store-search) |
| Workspaces | [List](#workspaces-list), [Get](#workspaces-get), [Context Store Search](#workspaces-context-store-search) |
| Activity Logs | [List](#activity-logs-list), [Context Store Search](#activity-logs-context-store-search) |

## Users

### Users List

Returns all users in the Monday.com account

#### Python SDK

```python
await monday.users.list()
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



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `enabled` | `null \| boolean` |  |
| `birthday` | `null \| string` |  |
| `country_code` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `join_date` | `null \| string` |  |
| `is_admin` | `null \| boolean` |  |
| `is_guest` | `null \| boolean` |  |
| `is_pending` | `null \| boolean` |  |
| `is_view_only` | `null \| boolean` |  |
| `is_verified` | `null \| boolean` |  |
| `location` | `null \| string` |  |
| `mobile_phone` | `null \| string` |  |
| `phone` | `null \| string` |  |
| `photo_original` | `null \| string` |  |
| `photo_small` | `null \| string` |  |
| `photo_thumb` | `null \| string` |  |
| `photo_thumb_small` | `null \| string` |  |
| `photo_tiny` | `null \| string` |  |
| `time_zone_identifier` | `null \| string` |  |
| `title` | `null \| string` |  |
| `url` | `null \| string` |  |
| `utc_hours_diff` | `null \| integer` |  |


</details>

### Users Get

Returns a single user by ID

#### Python SDK

```python
await monday.users.get(
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


### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.users.context_store_search(
    query={"filter": {"eq": {"birthday": "<str>"}}}
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
        "query": {"filter": {"eq": {"birthday": "<str>"}}}
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
| `birthday` | `string` | User's birthday |
| `country_code` | `string` | User's country code |
| `created_at` | `string` | When the user was created |
| `email` | `string` | User's email address |
| `enabled` | `boolean` | Whether the user account is enabled |
| `id` | `string` | Unique user identifier |
| `is_admin` | `boolean` | Whether the user is an admin |
| `is_guest` | `boolean` | Whether the user is a guest |
| `is_pending` | `boolean` | Whether the user is pending |
| `is_view_only` | `boolean` | Whether the user is view-only |
| `is_verified` | `boolean` | Whether the user is verified |
| `join_date` | `string` | When the user joined |
| `location` | `string` | User's location |
| `mobile_phone` | `string` | User's mobile phone number |
| `name` | `string` | User's display name |
| `phone` | `string` | User's phone number |
| `photo_original` | `string` | URL to original size photo |
| `photo_small` | `string` | URL to small photo |
| `photo_thumb` | `string` | URL to thumbnail photo |
| `photo_thumb_small` | `string` | URL to small thumbnail photo |
| `photo_tiny` | `string` | URL to tiny photo |
| `time_zone_identifier` | `string` | User's timezone identifier |
| `title` | `string` | User's job title |
| `url` | `string` | User's Monday.com profile URL |
| `utc_hours_diff` | `integer` | UTC hours difference for the user's timezone |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].birthday` | `string` | User's birthday |
| `data[].country_code` | `string` | User's country code |
| `data[].created_at` | `string` | When the user was created |
| `data[].email` | `string` | User's email address |
| `data[].enabled` | `boolean` | Whether the user account is enabled |
| `data[].id` | `string` | Unique user identifier |
| `data[].is_admin` | `boolean` | Whether the user is an admin |
| `data[].is_guest` | `boolean` | Whether the user is a guest |
| `data[].is_pending` | `boolean` | Whether the user is pending |
| `data[].is_view_only` | `boolean` | Whether the user is view-only |
| `data[].is_verified` | `boolean` | Whether the user is verified |
| `data[].join_date` | `string` | When the user joined |
| `data[].location` | `string` | User's location |
| `data[].mobile_phone` | `string` | User's mobile phone number |
| `data[].name` | `string` | User's display name |
| `data[].phone` | `string` | User's phone number |
| `data[].photo_original` | `string` | URL to original size photo |
| `data[].photo_small` | `string` | URL to small photo |
| `data[].photo_thumb` | `string` | URL to thumbnail photo |
| `data[].photo_thumb_small` | `string` | URL to small thumbnail photo |
| `data[].photo_tiny` | `string` | URL to tiny photo |
| `data[].time_zone_identifier` | `string` | User's timezone identifier |
| `data[].title` | `string` | User's job title |
| `data[].url` | `string` | User's Monday.com profile URL |
| `data[].utc_hours_diff` | `integer` | UTC hours difference for the user's timezone |

</details>

## Boards

### Boards List

Returns all boards in the Monday.com account

#### Python SDK

```python
await monday.boards.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "boards",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `board_kind` | `null \| string` |  |
| `type` | `null \| string` |  |
| `description` | `null \| string` |  |
| `permissions` | `null \| string` |  |
| `state` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `columns` | `null \| array` |  |
| `groups` | `null \| array` |  |
| `owners` | `null \| array` |  |
| `creator` | `null \| object` |  |
| `subscribers` | `null \| array` |  |
| `tags` | `null \| array` |  |
| `top_group` | `null \| object` |  |
| `views` | `null \| array` |  |
| `workspace` | `null \| object` |  |


</details>

### Boards Get

Returns a single board by ID

#### Python SDK

```python
await monday.boards.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "boards",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Board ID |


### Boards Context Store Search

Search and filter boards records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.boards.context_store_search(
    query={"filter": {"eq": {"board_kind": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "boards",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"board_kind": "<str>"}}}
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
| `board_kind` | `string` | Board kind (public, private, share) |
| `columns` | `array` | Board columns |
| `communication` | `string` | Board communication value |
| `creator` | `object` | Board creator |
| `description` | `string` | Board description |
| `groups` | `array` | Board groups |
| `id` | `string` | Unique board identifier |
| `name` | `string` | Board name |
| `owners` | `array` | Board owners |
| `permissions` | `string` | Board permissions |
| `state` | `string` | Board state (active, archived, deleted) |
| `subscribers` | `array` | Board subscribers |
| `tags` | `array` | Board tags |
| `top_group` | `object` | Top group on the board |
| `type` | `string` | Board type |
| `updated_at` | `string` | When the board was last updated |
| `updated_at_int` | `integer` | When the board was last updated (Unix timestamp) |
| `updates` | `array` | Board updates |
| `views` | `array` | Board views |
| `workspace` | `object` | Workspace the board belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].board_kind` | `string` | Board kind (public, private, share) |
| `data[].columns` | `array` | Board columns |
| `data[].communication` | `string` | Board communication value |
| `data[].creator` | `object` | Board creator |
| `data[].description` | `string` | Board description |
| `data[].groups` | `array` | Board groups |
| `data[].id` | `string` | Unique board identifier |
| `data[].name` | `string` | Board name |
| `data[].owners` | `array` | Board owners |
| `data[].permissions` | `string` | Board permissions |
| `data[].state` | `string` | Board state (active, archived, deleted) |
| `data[].subscribers` | `array` | Board subscribers |
| `data[].tags` | `array` | Board tags |
| `data[].top_group` | `object` | Top group on the board |
| `data[].type` | `string` | Board type |
| `data[].updated_at` | `string` | When the board was last updated |
| `data[].updated_at_int` | `integer` | When the board was last updated (Unix timestamp) |
| `data[].updates` | `array` | Board updates |
| `data[].views` | `array` | Board views |
| `data[].workspace` | `object` | Workspace the board belongs to |

</details>

## Items

### Items List

Returns items from boards. Queries items through the boards endpoint using items_page for pagination.

#### Python SDK

```python
await monday.items.list(
    board_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "items",
    "action": "list",
    "params": {
        "board_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `board_id` | `string` | Yes | Board ID to fetch items from |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `creator_id` | `null \| string` |  |
| `state` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `board` | `null \| object` |  |
| `group` | `null \| object` |  |
| `parent_item` | `null \| object` |  |
| `column_values` | `null \| array` |  |
| `subscribers` | `null \| array` |  |


</details>

### Items Get

Returns a single item by ID

#### Python SDK

```python
await monday.items.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "items",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Item ID |


### Items Context Store Search

Search and filter items records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.items.context_store_search(
    query={"filter": {"eq": {"assets": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "items",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"assets": []}}}
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
| `assets` | `array` | Files attached to the item |
| `board` | `object` | Board the item belongs to |
| `column_values` | `array` | Item column values |
| `created_at` | `string` | When the item was created |
| `creator_id` | `string` | ID of the user who created the item |
| `group` | `object` | Group the item belongs to |
| `id` | `string` | Unique item identifier |
| `name` | `string` | Item name |
| `parent_item` | `object` | Parent item (for subitems) |
| `state` | `string` | Item state (active, archived, deleted) |
| `subscribers` | `array` | Item subscribers |
| `updated_at` | `string` | When the item was last updated |
| `updated_at_int` | `integer` | When the item was last updated (Unix timestamp) |
| `updates` | `array` | Item updates |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].assets` | `array` | Files attached to the item |
| `data[].board` | `object` | Board the item belongs to |
| `data[].column_values` | `array` | Item column values |
| `data[].created_at` | `string` | When the item was created |
| `data[].creator_id` | `string` | ID of the user who created the item |
| `data[].group` | `object` | Group the item belongs to |
| `data[].id` | `string` | Unique item identifier |
| `data[].name` | `string` | Item name |
| `data[].parent_item` | `object` | Parent item (for subitems) |
| `data[].state` | `string` | Item state (active, archived, deleted) |
| `data[].subscribers` | `array` | Item subscribers |
| `data[].updated_at` | `string` | When the item was last updated |
| `data[].updated_at_int` | `integer` | When the item was last updated (Unix timestamp) |
| `data[].updates` | `array` | Item updates |

</details>

## Teams

### Teams List

Returns all teams in the Monday.com account

#### Python SDK

```python
await monday.teams.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `picture_url` | `null \| string` |  |
| `users` | `null \| array` |  |


</details>

### Teams Get

Returns a single team by ID

#### Python SDK

```python
await monday.teams.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Team ID |


### Teams Context Store Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.teams.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "context_store_search",
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
| `id` | `integer` | Unique team identifier |
| `name` | `string` | Team name |
| `picture_url` | `string` | Team picture URL |
| `users` | `array` | Team members |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique team identifier |
| `data[].name` | `string` | Team name |
| `data[].picture_url` | `string` | Team picture URL |
| `data[].users` | `array` | Team members |

</details>

## Tags

### Tags List

Returns all tags in the Monday.com account

#### Python SDK

```python
await monday.tags.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `color` | `null \| string` |  |


</details>

### Tags Context Store Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.tags.context_store_search(
    query={"filter": {"eq": {"color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"color": "<str>"}}}
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
| `color` | `string` | Tag color |
| `id` | `string` | Unique tag identifier |
| `name` | `string` | Tag name |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].color` | `string` | Tag color |
| `data[].id` | `string` | Unique tag identifier |
| `data[].name` | `string` | Tag name |

</details>

## Updates

### Updates List

Returns all updates (comments/posts) in the Monday.com account

#### Python SDK

```python
await monday.updates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "updates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number for pagination |
| `limit` | `integer` | No | Number of updates to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `body` | `null \| string` |  |
| `text_body` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `creator_id` | `null \| string` |  |
| `item_id` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `replies` | `null \| array` |  |
| `assets` | `null \| array` |  |


</details>

### Updates Get

Returns a single update by ID

#### Python SDK

```python
await monday.updates.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "updates",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Update ID |


### Updates Context Store Search

Search and filter updates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.updates.context_store_search(
    query={"filter": {"eq": {"assets": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "updates",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"assets": []}}}
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
| `assets` | `array` | Files attached to this update |
| `body` | `string` | Update body (HTML) |
| `created_at` | `string` | When the update was created |
| `creator_id` | `string` | ID of the user who created the update |
| `id` | `string` | Unique update identifier |
| `item_id` | `string` | ID of the item this update belongs to |
| `replies` | `array` | Replies to this update |
| `text_body` | `string` | Update body (plain text) |
| `updated_at` | `string` | When the update was last modified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].assets` | `array` | Files attached to this update |
| `data[].body` | `string` | Update body (HTML) |
| `data[].created_at` | `string` | When the update was created |
| `data[].creator_id` | `string` | ID of the user who created the update |
| `data[].id` | `string` | Unique update identifier |
| `data[].item_id` | `string` | ID of the item this update belongs to |
| `data[].replies` | `array` | Replies to this update |
| `data[].text_body` | `string` | Update body (plain text) |
| `data[].updated_at` | `string` | When the update was last modified |

</details>

## Workspaces

### Workspaces List

Returns all workspaces in the Monday.com account

#### Python SDK

```python
await monday.workspaces.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `kind` | `null \| string` |  |
| `description` | `null \| string` |  |
| `state` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `account_product` | `null \| object` |  |
| `owners_subscribers` | `null \| array` |  |
| `settings` | `null \| object` |  |
| `team_owners_subscribers` | `null \| array` |  |
| `teams_subscribers` | `null \| array` |  |
| `users_subscribers` | `null \| array` |  |


</details>

### Workspaces Get

Returns a single workspace by ID

#### Python SDK

```python
await monday.workspaces.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Workspace ID |


### Workspaces Context Store Search

Search and filter workspaces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.workspaces.context_store_search(
    query={"filter": {"eq": {"account_product": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"account_product": {}}}}
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
| `account_product` | `object` | Account product info |
| `created_at` | `string` | When the workspace was created |
| `description` | `string` | Workspace description |
| `id` | `string` | Unique workspace identifier |
| `kind` | `string` | Workspace kind (open, closed) |
| `name` | `string` | Workspace name |
| `owners_subscribers` | `array` | Owner subscribers |
| `settings` | `object` | Workspace settings |
| `state` | `string` | Workspace state |
| `team_owners_subscribers` | `array` | Team owner subscribers |
| `teams_subscribers` | `array` | Team subscribers |
| `users_subscribers` | `array` | User subscribers |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account_product` | `object` | Account product info |
| `data[].created_at` | `string` | When the workspace was created |
| `data[].description` | `string` | Workspace description |
| `data[].id` | `string` | Unique workspace identifier |
| `data[].kind` | `string` | Workspace kind (open, closed) |
| `data[].name` | `string` | Workspace name |
| `data[].owners_subscribers` | `array` | Owner subscribers |
| `data[].settings` | `object` | Workspace settings |
| `data[].state` | `string` | Workspace state |
| `data[].team_owners_subscribers` | `array` | Team owner subscribers |
| `data[].teams_subscribers` | `array` | Team subscribers |
| `data[].users_subscribers` | `array` | User subscribers |

</details>

## Activity Logs

### Activity Logs List

Returns activity logs from boards. Requires a board_id parameter.

#### Python SDK

```python
await monday.activity_logs.list(
    board_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "activity_logs",
    "action": "list",
    "params": {
        "board_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `board_id` | `string` | Yes | Board ID to fetch activity logs from |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `event` | `null \| string` |  |
| `data` | `null \| string` |  |
| `entity` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `user_id` | `null \| string` |  |


</details>

### Activity Logs Context Store Search

Search and filter activity logs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await monday.activity_logs.context_store_search(
    query={"filter": {"eq": {"board_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "activity_logs",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"board_id": 0}}}
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
| `board_id` | `integer` | Board ID the activity belongs to |
| `created_at` | `string` | When the activity occurred |
| `created_at_int` | `integer` | When the activity occurred (Unix timestamp) |
| `data` | `string` | Event data (JSON string) |
| `entity` | `string` | Entity type that was affected |
| `event` | `string` | Event type |
| `id` | `string` | Unique activity log identifier |
| `pulse_id` | `integer` | Item (pulse) ID the activity belongs to |
| `user_id` | `string` | ID of the user who performed the action |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].board_id` | `integer` | Board ID the activity belongs to |
| `data[].created_at` | `string` | When the activity occurred |
| `data[].created_at_int` | `integer` | When the activity occurred (Unix timestamp) |
| `data[].data` | `string` | Event data (JSON string) |
| `data[].entity` | `string` | Entity type that was affected |
| `data[].event` | `string` | Event type |
| `data[].id` | `string` | Unique activity log identifier |
| `data[].pulse_id` | `integer` | Item (pulse) ID the activity belongs to |
| `data[].user_id` | `string` | ID of the user who performed the action |

</details>

