# Granola full reference

This is the full reference documentation for the Granola agent connector.

## Supported entities and actions

The Granola connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Notes | [List](#notes-list), [Get](#notes-get), [Search](#notes-search) |

## Notes

### Notes List

Returns a paginated list of meeting notes

#### Python SDK

```python
await granola.notes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of notes to return per page |
| `cursor` | `string` | No | Pagination cursor for next page |
| `created_before` | `string` | No | Return notes created before this date (YYYY-MM-DD) |
| `created_after` | `string` | No | Return notes created after this date (YYYY-MM-DD) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `title` | `string \| null` |  |
| `owner` | `object \| any` |  |
| `created_at` | `string \| null` |  |
| `calendar_event` | `object \| any` |  |
| `attendees` | `array \| null` |  |
| `attendees[].name` | `string \| null` |  |
| `attendees[].email` | `string \| null` |  |
| `folder_membership` | `array \| null` |  |
| `folder_membership[].id` | `string` |  |
| `folder_membership[].object` | `string \| null` |  |
| `folder_membership[].name` | `string \| null` |  |
| `summary_text` | `string \| null` |  |
| `summary_markdown` | `string \| null` |  |
| `transcript` | `array \| null` |  |
| `transcript[].speaker` | `object \| any` |  |
| `transcript[].text` | `string \| null` |  |
| `transcript[].start_time` | `string \| null` |  |
| `transcript[].end_time` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `cursor` | `string \| null` |  |
| `has_more` | `boolean` |  |

</details>

### Notes Get

Get a single note by ID, including full details and optionally the transcript

#### Python SDK

```python
await granola.notes.get(
    note_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "get",
    "params": {
        "note_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `note_id` | `string` | Yes | The ID of the note |
| `include` | `"transcript"` | No | Include the note transcript in the response |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `object` | `string \| null` |  |
| `title` | `string \| null` |  |
| `owner` | `object \| any` |  |
| `created_at` | `string \| null` |  |
| `calendar_event` | `object \| any` |  |
| `attendees` | `array \| null` |  |
| `attendees[].name` | `string \| null` |  |
| `attendees[].email` | `string \| null` |  |
| `folder_membership` | `array \| null` |  |
| `folder_membership[].id` | `string` |  |
| `folder_membership[].object` | `string \| null` |  |
| `folder_membership[].name` | `string \| null` |  |
| `summary_text` | `string \| null` |  |
| `summary_markdown` | `string \| null` |  |
| `transcript` | `array \| null` |  |
| `transcript[].speaker` | `object \| any` |  |
| `transcript[].text` | `string \| null` |  |
| `transcript[].start_time` | `string \| null` |  |
| `transcript[].end_time` | `string \| null` |  |


</details>

### Notes Search

Search and filter notes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await granola.notes.search(
    query={"filter": {"eq": {"created_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
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
| `created_at` | `string` | The creation time of the note in ISO 8601 format. |
| `id` | `string` | The unique identifier of the note. |
| `object` | `string` | The object type, always "note". |
| `owner` | `object` | The owner of the note. |
| `title` | `string` | The title of the note. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `string` | The creation time of the note in ISO 8601 format. |
| `data[].id` | `string` | The unique identifier of the note. |
| `data[].object` | `string` | The object type, always "note". |
| `data[].owner` | `object` | The owner of the note. |
| `data[].title` | `string` | The title of the note. |

</details>

