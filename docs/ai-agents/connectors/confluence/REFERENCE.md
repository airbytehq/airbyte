# Confluence full reference

This is the full reference documentation for the Confluence agent connector.

## Supported entities and actions

The Confluence connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Spaces | [List](#spaces-list), [Get](#spaces-get), [Search](#spaces-search) |
| Pages | [List](#pages-list), [Get](#pages-get), [Search](#pages-search) |
| Blog Posts | [List](#blog-posts-list), [Get](#blog-posts-get), [Search](#blog-posts-search) |
| Groups | [List](#groups-list), [Search](#groups-search) |
| Audit | [List](#audit-list), [Search](#audit-search) |

## Spaces

### Spaces List

Returns all spaces. Only spaces that the user has permission to view will be returned.

#### Python SDK

```python
await confluence.spaces.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spaces",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |
| `limit` | `integer` | No | Maximum number of spaces to return |
| `type` | `"global" \| "personal"` | No | Filter by space type (global or personal) |
| `status` | `"current" \| "archived"` | No | Filter by space status (current or archived) |
| `keys` | `array<string>` | No | Filter by space keys |
| `sort` | `"id" \| "-id" \| "key" \| "-key" \| "name" \| "-name"` | No | Sort order for results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `status` | `string` |  |
| `authorId` | `string` |  |
| `createdAt` | `string` |  |
| `homepageId` | `string` |  |
| `spaceOwnerId` | `string` |  |
| `currentActiveAlias` | `string` |  |
| `description` | `object \| any` |  |
| `icon` | `object \| any` |  |
| `_links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Spaces Get

Returns a specific space.

#### Python SDK

```python
await confluence.spaces.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spaces",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the space |
| `description-format` | `"plain" \| "view"` | No | The format of the space description in the response |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `key` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `status` | `string` |  |
| `authorId` | `string` |  |
| `createdAt` | `string` |  |
| `homepageId` | `string` |  |
| `spaceOwnerId` | `string` |  |
| `currentActiveAlias` | `string` |  |
| `description` | `object \| any` |  |
| `icon` | `object \| any` |  |
| `_links` | `object` |  |


</details>

### Spaces Search

Search and filter spaces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await confluence.spaces.search(
    query={"filter": {"eq": {"_links": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spaces",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"_links": {}}}}
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
| `_links` | `object` | Links related to the space |
| `authorId` | `string` | ID of the user who created the space |
| `createdAt` | `string` | Timestamp when the space was created |
| `description` | `object` | Space description in various formats |
| `homepageId` | `string` | ID of the space homepage |
| `icon` | `object` | Space icon information |
| `id` | `string` | Unique space identifier |
| `key` | `string` | Space key |
| `name` | `string` | Space name |
| `status` | `string` | Space status (current or archived) |
| `type` | `string` | Space type (global or personal) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._links` | `object` | Links related to the space |
| `data[].authorId` | `string` | ID of the user who created the space |
| `data[].createdAt` | `string` | Timestamp when the space was created |
| `data[].description` | `object` | Space description in various formats |
| `data[].homepageId` | `string` | ID of the space homepage |
| `data[].icon` | `object` | Space icon information |
| `data[].id` | `string` | Unique space identifier |
| `data[].key` | `string` | Space key |
| `data[].name` | `string` | Space name |
| `data[].status` | `string` | Space status (current or archived) |
| `data[].type` | `string` | Space type (global or personal) |

</details>

## Pages

### Pages List

Returns all pages. Only pages that the user has permission to view will be returned.

#### Python SDK

```python
await confluence.pages.list()
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
| `cursor` | `string` | No | Cursor for pagination |
| `limit` | `integer` | No | Maximum number of pages to return |
| `space-id` | `array<integer>` | No | Filter pages by space ID(s) |
| `title` | `string` | No | Filter pages by title (exact match) |
| `status` | `array<"current" \| "archived" \| "trashed" \| "draft">` | No | Filter pages by status |
| `sort` | `"id" \| "-id" \| "title" \| "-title" \| "created-date" \| "-created-date" \| "modified-date" \| "-modified-date"` | No | Sort order for results |
| `body-format` | `"storage" \| "atlas_doc_format" \| "view"` | No | The format of the page body in the response |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `status` | `string` |  |
| `title` | `string` |  |
| `spaceId` | `string` |  |
| `parentId` | `string \| any` |  |
| `parentType` | `string \| any` |  |
| `position` | `integer` |  |
| `authorId` | `string` |  |
| `ownerId` | `string` |  |
| `lastOwnerId` | `string \| any` |  |
| `createdAt` | `string` |  |
| `version` | `object` |  |
| `body` | `object` |  |
| `_links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Pages Get

Returns a specific page.

#### Python SDK

```python
await confluence.pages.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the page |
| `body-format` | `"storage" \| "atlas_doc_format" \| "view"` | No | The format of the page body in the response |
| `version` | `integer` | No | Specific version number to retrieve |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `status` | `string` |  |
| `title` | `string` |  |
| `spaceId` | `string` |  |
| `parentId` | `string \| any` |  |
| `parentType` | `string \| any` |  |
| `position` | `integer` |  |
| `authorId` | `string` |  |
| `ownerId` | `string` |  |
| `lastOwnerId` | `string \| any` |  |
| `createdAt` | `string` |  |
| `version` | `object` |  |
| `body` | `object` |  |
| `_links` | `object` |  |


</details>

### Pages Search

Search and filter pages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await confluence.pages.search(
    query={"filter": {"eq": {"_links": {}}}}
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
        "query": {"filter": {"eq": {"_links": {}}}}
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
| `_links` | `object` | Links related to the page |
| `authorId` | `string` | ID of the user who created the page |
| `body` | `object` | Page body content |
| `createdAt` | `string` | Timestamp when the page was created |
| `id` | `string` | Unique page identifier |
| `lastOwnerId` | `string` | ID of the previous page owner |
| `ownerId` | `string` | ID of the current page owner |
| `parentId` | `string` | ID of the parent page |
| `parentType` | `string` | Type of the parent (page or space) |
| `position` | `integer` | Position of the page among siblings |
| `spaceId` | `string` | ID of the space containing this page |
| `status` | `string` | Page status (current, archived, trashed, draft) |
| `title` | `string` | Page title |
| `version` | `object` | Version information |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._links` | `object` | Links related to the page |
| `data[].authorId` | `string` | ID of the user who created the page |
| `data[].body` | `object` | Page body content |
| `data[].createdAt` | `string` | Timestamp when the page was created |
| `data[].id` | `string` | Unique page identifier |
| `data[].lastOwnerId` | `string` | ID of the previous page owner |
| `data[].ownerId` | `string` | ID of the current page owner |
| `data[].parentId` | `string` | ID of the parent page |
| `data[].parentType` | `string` | Type of the parent (page or space) |
| `data[].position` | `integer` | Position of the page among siblings |
| `data[].spaceId` | `string` | ID of the space containing this page |
| `data[].status` | `string` | Page status (current, archived, trashed, draft) |
| `data[].title` | `string` | Page title |
| `data[].version` | `object` | Version information |

</details>

## Blog Posts

### Blog Posts List

Returns all blog posts. Only blog posts that the user has permission to view will be returned.

#### Python SDK

```python
await confluence.blog_posts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blog_posts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |
| `limit` | `integer` | No | Maximum number of blog posts to return |
| `space-id` | `array<integer>` | No | Filter blog posts by space ID(s) |
| `title` | `string` | No | Filter blog posts by title (exact match) |
| `status` | `array<"current" \| "draft" \| "trashed">` | No | Filter blog posts by status |
| `sort` | `"id" \| "-id" \| "title" \| "-title" \| "created-date" \| "-created-date" \| "modified-date" \| "-modified-date"` | No | Sort order for results |
| `body-format` | `"storage" \| "atlas_doc_format" \| "view"` | No | The format of the blog post body in the response |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `status` | `string` |  |
| `title` | `string` |  |
| `spaceId` | `string` |  |
| `authorId` | `string` |  |
| `createdAt` | `string` |  |
| `version` | `object` |  |
| `body` | `object` |  |
| `_links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Blog Posts Get

Returns a specific blog post.

#### Python SDK

```python
await confluence.blog_posts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blog_posts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the blog post |
| `body-format` | `"storage" \| "atlas_doc_format" \| "view"` | No | The format of the blog post body in the response |
| `version` | `integer` | No | Specific version number to retrieve |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `status` | `string` |  |
| `title` | `string` |  |
| `spaceId` | `string` |  |
| `authorId` | `string` |  |
| `createdAt` | `string` |  |
| `version` | `object` |  |
| `body` | `object` |  |
| `_links` | `object` |  |


</details>

### Blog Posts Search

Search and filter blog posts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await confluence.blog_posts.search(
    query={"filter": {"eq": {"_links": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blog_posts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"_links": {}}}}
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
| `_links` | `object` | Links related to the blog post |
| `authorId` | `string` | ID of the user who created the blog post |
| `body` | `object` | Blog post body content |
| `createdAt` | `string` | Timestamp when the blog post was created |
| `id` | `string` | Unique blog post identifier |
| `spaceId` | `string` | ID of the space containing this blog post |
| `status` | `string` | Blog post status (current, draft, trashed) |
| `title` | `string` | Blog post title |
| `version` | `object` | Version information |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._links` | `object` | Links related to the blog post |
| `data[].authorId` | `string` | ID of the user who created the blog post |
| `data[].body` | `object` | Blog post body content |
| `data[].createdAt` | `string` | Timestamp when the blog post was created |
| `data[].id` | `string` | Unique blog post identifier |
| `data[].spaceId` | `string` | ID of the space containing this blog post |
| `data[].status` | `string` | Blog post status (current, draft, trashed) |
| `data[].title` | `string` | Blog post title |
| `data[].version` | `object` | Version information |

</details>

## Groups

### Groups List

Returns all user groups.

#### Python SDK

```python
await confluence.groups.list()
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
| `start` | `integer` | No | Starting index for pagination |
| `limit` | `integer` | No | Maximum number of groups to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string` |  |
| `id` | `string` |  |
| `name` | `string` |  |
| `managedBy` | `string` |  |
| `usageType` | `string` |  |
| `resourceAri` | `string` |  |
| `_links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `start` | `integer` |  |
| `limit` | `integer` |  |
| `size` | `integer` |  |

</details>

### Groups Search

Search and filter groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await confluence.groups.search(
    query={"filter": {"eq": {"_links": {}}}}
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
        "query": {"filter": {"eq": {"_links": {}}}}
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
| `_links` | `object` | Links related to the group |
| `id` | `string` | The unique identifier of the group |
| `name` | `string` | The name of the group |
| `type` | `string` | The type of group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._links` | `object` | Links related to the group |
| `data[].id` | `string` | The unique identifier of the group |
| `data[].name` | `string` | The name of the group |
| `data[].type` | `string` | The type of group |

</details>

## Audit

### Audit List

Returns audit log records.

#### Python SDK

```python
await confluence.audit.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "audit",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `integer` | No | Starting index for pagination |
| `limit` | `integer` | No | Maximum number of audit records to return |
| `startDate` | `string` | No | Start date for filtering audit records (ISO 8601) |
| `endDate` | `string` | No | End date for filtering audit records (ISO 8601) |
| `searchString` | `string` | No | Search string to filter audit records |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `author` | `object` |  |
| `remoteAddress` | `string` |  |
| `creationDate` | `integer` |  |
| `summary` | `string` |  |
| `description` | `string` |  |
| `category` | `string` |  |
| `sysAdmin` | `boolean` |  |
| `superAdmin` | `boolean` |  |
| `affectedObject` | `object` |  |
| `changedValues` | `array` |  |
| `associatedObjects` | `array<object>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `start` | `integer` |  |
| `limit` | `integer` |  |
| `size` | `integer` |  |

</details>

### Audit Search

Search and filter audit records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await confluence.audit.search(
    query={"filter": {"eq": {"affectedObject": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "audit",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"affectedObject": {}}}}
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
| `affectedObject` | `object` | The object that was affected by the audit event. |
| `associatedObjects` | `array` | Any associated objects related to the audit event. |
| `author` | `object` | The user who triggered the audit event. |
| `category` | `string` | The category under which the audit event falls. |
| `changedValues` | `array` | Details of the values that were changed during the audit event. |
| `creationDate` | `integer` | The date and time when the audit event was created. |
| `description` | `string` | A detailed description of the audit event. |
| `remoteAddress` | `string` | The IP address from which the audit event originated. |
| `summary` | `string` | A brief summary or title describing the audit event. |
| `superAdmin` | `boolean` | Indicates if the user triggering the audit event is a super admin. |
| `sysAdmin` | `boolean` | Indicates if the user triggering the audit event is a system admin. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].affectedObject` | `object` | The object that was affected by the audit event. |
| `data[].associatedObjects` | `array` | Any associated objects related to the audit event. |
| `data[].author` | `object` | The user who triggered the audit event. |
| `data[].category` | `string` | The category under which the audit event falls. |
| `data[].changedValues` | `array` | Details of the values that were changed during the audit event. |
| `data[].creationDate` | `integer` | The date and time when the audit event was created. |
| `data[].description` | `string` | A detailed description of the audit event. |
| `data[].remoteAddress` | `string` | The IP address from which the audit event originated. |
| `data[].summary` | `string` | A brief summary or title describing the audit event. |
| `data[].superAdmin` | `boolean` | Indicates if the user triggering the audit event is a super admin. |
| `data[].sysAdmin` | `boolean` | Indicates if the user triggering the audit event is a system admin. |

</details>

