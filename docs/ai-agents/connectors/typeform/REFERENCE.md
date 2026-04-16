# Typeform full reference

This is the full reference documentation for the Typeform agent connector.

## Supported entities and actions

The Typeform connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Forms | [List](#forms-list), [Get](#forms-get), [Search](#forms-search) |
| Responses | [List](#responses-list), [Search](#responses-search) |
| Webhooks | [List](#webhooks-list), [Search](#webhooks-search) |
| Workspaces | [List](#workspaces-list), [Search](#workspaces-search) |
| Images | [List](#images-list), [Search](#images-search) |
| Themes | [List](#themes-list), [Search](#themes-search) |

## Forms

### Forms List

Returns a paginated list of forms in the account

#### Python SDK

```python
await typeform.forms.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "forms",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number to retrieve |
| `page_size` | `integer` | No | Number of forms per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `type` | `null \| string` |  |
| `title` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `last_updated_at` | `null \| string` |  |
| `published_at` | `null \| string` |  |
| `workspace` | `null \| object` |  |
| `theme` | `null \| object` |  |
| `settings` | `null \| object` |  |
| `welcome_screens` | `null \| array` |  |
| `thankyou_screens` | `null \| array` |  |
| `logic` | `null \| array` |  |
| `fields` | `null \| array` |  |
| `self` | `null \| object` |  |
| `_links` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `null \| integer` |  |
| `page_count` | `null \| integer` |  |

</details>

### Forms Get

Retrieves a single form by its ID, including fields, settings, and logic

#### Python SDK

```python
await typeform.forms.get(
    form_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "forms",
    "action": "get",
    "params": {
        "form_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `form_id` | `string` | Yes | Unique ID of the form |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `type` | `null \| string` |  |
| `title` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `last_updated_at` | `null \| string` |  |
| `published_at` | `null \| string` |  |
| `workspace` | `null \| object` |  |
| `theme` | `null \| object` |  |
| `settings` | `null \| object` |  |
| `welcome_screens` | `null \| array` |  |
| `thankyou_screens` | `null \| array` |  |
| `logic` | `null \| array` |  |
| `fields` | `null \| array` |  |
| `self` | `null \| object` |  |
| `_links` | `null \| object` |  |


</details>

### Forms Search

Search and filter forms records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await typeform.forms.search(
    query={"filter": {"eq": {"_links": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "forms",
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
| `_links` | `object` | Links to related resources |
| `created_at` | `string` | Date and time when the form was created |
| `fields` | `array` | List of fields within the form |
| `id` | `string` | Unique identifier of the form |
| `last_updated_at` | `string` | Date and time when the form was last updated |
| `logic` | `array` | Logic rules or conditions applied to the form fields |
| `published_at` | `string` | Date and time when the form was published |
| `settings` | `object` | Settings and configurations for the form |
| `thankyou_screens` | `array` | Thank you screen configurations |
| `theme` | `object` | Theme settings for the form |
| `title` | `string` | Title of the form |
| `type` | `string` | Type of the form |
| `welcome_screens` | `array` | Welcome screen configurations |
| `workspace` | `object` | Workspace details where the form belongs |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._links` | `object` | Links to related resources |
| `data[].created_at` | `string` | Date and time when the form was created |
| `data[].fields` | `array` | List of fields within the form |
| `data[].id` | `string` | Unique identifier of the form |
| `data[].last_updated_at` | `string` | Date and time when the form was last updated |
| `data[].logic` | `array` | Logic rules or conditions applied to the form fields |
| `data[].published_at` | `string` | Date and time when the form was published |
| `data[].settings` | `object` | Settings and configurations for the form |
| `data[].thankyou_screens` | `array` | Thank you screen configurations |
| `data[].theme` | `object` | Theme settings for the form |
| `data[].title` | `string` | Title of the form |
| `data[].type` | `string` | Type of the form |
| `data[].welcome_screens` | `array` | Welcome screen configurations |
| `data[].workspace` | `object` | Workspace details where the form belongs |

</details>

## Responses

### Responses List

Returns a paginated list of responses for a given form

#### Python SDK

```python
await typeform.responses.list(
    form_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "responses",
    "action": "list",
    "params": {
        "form_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `form_id` | `string` | Yes | Unique ID of the form |
| `page_size` | `integer` | No | Number of responses per page |
| `since` | `string` | No | Limit responses to those submitted since the specified date/time (ISO 8601 format, e.g. 2021-03-01T00:00:00Z) |
| `until` | `string` | No | Limit responses to those submitted until the specified date/time (ISO 8601 format) |
| `after` | `string` | No | Cursor token for pagination; returns responses after this token |
| `before` | `string` | No | Cursor token for pagination; returns responses before this token |
| `sort` | `string` | No | Sort order for responses, e.g. submitted_at,asc |
| `completed` | `boolean` | No | Filter by completed status (true or false) |
| `query` | `string` | No | Search query to filter responses |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `response_id` | `null \| string` |  |
| `response_type` | `null \| string` |  |
| `landed_at` | `null \| string` |  |
| `landing_id` | `null \| string` |  |
| `submitted_at` | `null \| string` |  |
| `token` | `null \| string` |  |
| `form_id` | `null \| string` |  |
| `metadata` | `null \| object` |  |
| `variables` | `null \| array` |  |
| `hidden` | `null \| object` |  |
| `calculated` | `null \| object` |  |
| `answers` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `null \| integer` |  |
| `page_count` | `null \| integer` |  |

</details>

### Responses Search

Search and filter responses records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await typeform.responses.search(
    query={"filter": {"eq": {"answers": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "responses",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"answers": []}}}
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
| `answers` | `array` | Response data for each question in the form |
| `calculated` | `object` | Calculated data related to the response |
| `form_id` | `string` | ID of the form |
| `hidden` | `object` | Hidden fields in the response |
| `landed_at` | `string` | Timestamp when the respondent landed on the form |
| `landing_id` | `string` | ID of the landing page |
| `metadata` | `object` | Metadata related to the response |
| `response_id` | `string` | ID of the response |
| `response_type` | `string` | Type of the response |
| `submitted_at` | `string` | Timestamp when the response was submitted |
| `token` | `string` | Token associated with the response |
| `variables` | `array` | Variables associated with the response |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].answers` | `array` | Response data for each question in the form |
| `data[].calculated` | `object` | Calculated data related to the response |
| `data[].form_id` | `string` | ID of the form |
| `data[].hidden` | `object` | Hidden fields in the response |
| `data[].landed_at` | `string` | Timestamp when the respondent landed on the form |
| `data[].landing_id` | `string` | ID of the landing page |
| `data[].metadata` | `object` | Metadata related to the response |
| `data[].response_id` | `string` | ID of the response |
| `data[].response_type` | `string` | Type of the response |
| `data[].submitted_at` | `string` | Timestamp when the response was submitted |
| `data[].token` | `string` | Token associated with the response |
| `data[].variables` | `array` | Variables associated with the response |

</details>

## Webhooks

### Webhooks List

Returns webhooks configured for a given form

#### Python SDK

```python
await typeform.webhooks.list(
    form_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "webhooks",
    "action": "list",
    "params": {
        "form_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `form_id` | `string` | Yes | Unique ID of the form |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `form_id` | `null \| string` |  |
| `tag` | `null \| string` |  |
| `url` | `null \| string` |  |
| `enabled` | `null \| boolean` |  |
| `verify_ssl` | `null \| boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Webhooks Search

Search and filter webhooks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await typeform.webhooks.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "webhooks",
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
| `created_at` | `string` | Timestamp when the webhook was created |
| `enabled` | `boolean` | Whether the webhook is currently enabled |
| `form_id` | `string` | ID of the form associated with the webhook |
| `id` | `string` | Unique identifier of the webhook |
| `tag` | `string` | Tag to categorize or label the webhook |
| `updated_at` | `string` | Timestamp when the webhook was last updated |
| `url` | `string` | URL where webhook data is sent |
| `verify_ssl` | `boolean` | Whether SSL verification is enforced |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | Timestamp when the webhook was created |
| `data[].enabled` | `boolean` | Whether the webhook is currently enabled |
| `data[].form_id` | `string` | ID of the form associated with the webhook |
| `data[].id` | `string` | Unique identifier of the webhook |
| `data[].tag` | `string` | Tag to categorize or label the webhook |
| `data[].updated_at` | `string` | Timestamp when the webhook was last updated |
| `data[].url` | `string` | URL where webhook data is sent |
| `data[].verify_ssl` | `boolean` | Whether SSL verification is enforced |

</details>

## Workspaces

### Workspaces List

Returns a paginated list of workspaces in the account

#### Python SDK

```python
await typeform.workspaces.list()
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number to retrieve |
| `page_size` | `integer` | No | Number of workspaces per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `account_id` | `null \| string` |  |
| `default` | `null \| boolean` |  |
| `shared` | `null \| boolean` |  |
| `forms` | `null \| object` |  |
| `self` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `null \| integer` |  |
| `page_count` | `null \| integer` |  |

</details>

### Workspaces Search

Search and filter workspaces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await typeform.workspaces.search(
    query={"filter": {"eq": {"account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"account_id": "<str>"}}}
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
| `account_id` | `string` | Account ID associated with the workspace |
| `default` | `boolean` | Whether this is the default workspace |
| `forms` | `object` | Information about forms in the workspace |
| `id` | `string` | Unique identifier of the workspace |
| `name` | `string` | Name of the workspace |
| `self` | `object` | Self-referential link |
| `shared` | `boolean` | Whether this workspace is shared |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account_id` | `string` | Account ID associated with the workspace |
| `data[].default` | `boolean` | Whether this is the default workspace |
| `data[].forms` | `object` | Information about forms in the workspace |
| `data[].id` | `string` | Unique identifier of the workspace |
| `data[].name` | `string` | Name of the workspace |
| `data[].self` | `object` | Self-referential link |
| `data[].shared` | `boolean` | Whether this workspace is shared |

</details>

## Images

### Images List

Returns a list of images in the account

#### Python SDK

```python
await typeform.images.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "images",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `file_name` | `null \| string` |  |
| `src` | `null \| string` |  |
| `width` | `null \| integer` |  |
| `height` | `null \| integer` |  |
| `media_type` | `null \| string` |  |
| `avg_color` | `null \| string` |  |
| `has_alpha` | `null \| boolean` |  |
| `upload_source` | `null \| string` |  |


</details>

### Images Search

Search and filter images records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await typeform.images.search(
    query={"filter": {"eq": {"avg_color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "images",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"avg_color": "<str>"}}}
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
| `avg_color` | `string` | Average color of the image |
| `file_name` | `string` | Name of the image file |
| `has_alpha` | `boolean` | Whether the image has an alpha channel |
| `height` | `integer` | Height of the image in pixels |
| `id` | `string` | Unique identifier of the image |
| `media_type` | `string` | MIME type of the image |
| `src` | `string` | URL to access the image |
| `width` | `integer` | Width of the image in pixels |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].avg_color` | `string` | Average color of the image |
| `data[].file_name` | `string` | Name of the image file |
| `data[].has_alpha` | `boolean` | Whether the image has an alpha channel |
| `data[].height` | `integer` | Height of the image in pixels |
| `data[].id` | `string` | Unique identifier of the image |
| `data[].media_type` | `string` | MIME type of the image |
| `data[].src` | `string` | URL to access the image |
| `data[].width` | `integer` | Width of the image in pixels |

</details>

## Themes

### Themes List

Returns a paginated list of themes in the account

#### Python SDK

```python
await typeform.themes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "themes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number to retrieve |
| `page_size` | `integer` | No | Number of themes per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `visibility` | `null \| string` |  |
| `font` | `null \| string` |  |
| `has_transparent_button` | `null \| boolean` |  |
| `rounded_corners` | `null \| string` |  |
| `colors` | `null \| object` |  |
| `background` | `null \| object` |  |
| `fields` | `null \| object` |  |
| `screens` | `null \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `null \| integer` |  |
| `page_count` | `null \| integer` |  |

</details>

### Themes Search

Search and filter themes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await typeform.themes.search(
    query={"filter": {"eq": {"background": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "themes",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"background": {}}}}
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
| `background` | `object` | Background settings for the theme |
| `colors` | `object` | Color settings |
| `created_at` | `string` | Timestamp when the theme was created |
| `fields` | `object` | Field display settings |
| `font` | `string` | Font used in the theme |
| `has_transparent_button` | `boolean` | Whether the theme has a transparent button |
| `id` | `string` | Unique identifier of the theme |
| `name` | `string` | Name of the theme |
| `rounded_corners` | `string` | Rounded corners setting |
| `screens` | `object` | Screen display settings |
| `updated_at` | `string` | Timestamp when the theme was last updated |
| `visibility` | `string` | Visibility setting of the theme |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].background` | `object` | Background settings for the theme |
| `data[].colors` | `object` | Color settings |
| `data[].created_at` | `string` | Timestamp when the theme was created |
| `data[].fields` | `object` | Field display settings |
| `data[].font` | `string` | Font used in the theme |
| `data[].has_transparent_button` | `boolean` | Whether the theme has a transparent button |
| `data[].id` | `string` | Unique identifier of the theme |
| `data[].name` | `string` | Name of the theme |
| `data[].rounded_corners` | `string` | Rounded corners setting |
| `data[].screens` | `object` | Screen display settings |
| `data[].updated_at` | `string` | Timestamp when the theme was last updated |
| `data[].visibility` | `string` | Visibility setting of the theme |

</details>

