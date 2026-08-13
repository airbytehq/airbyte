# Granola full reference

This is the full reference documentation for the Granola agent connector.

## Supported entities and actions

The Granola connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Notes | [List](#notes-list), [Get](#notes-get), [Context Store Search](#notes-context-store-search), [Semantic Search](#notes-semantic-search) |

## Notes

### Notes List

Returns a paginated list of meeting notes

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "granola",
  "entity": "notes",
  "action": "list"
}'
```

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
| `updated_at` | `string \| null` |  |
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

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "granola",
  "entity": "notes",
  "action": "get",
  "params": {
    "note_id": "<str>"
  }
}'
```

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
| `updated_at` | `string \| null` |  |
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

### Notes Context Store Search

Search and filter notes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "granola",
  "entity": "notes",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await granola.notes.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "context_store_search",
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
| `id` | `string` | The unique identifier of the note. |
| `object` | `string` | The object type, always "note". |
| `title` | `string` | The title of the note. |
| `owner` | `object` | The owner of the note. |
| `created_at` | `string` | The creation time of the note in ISO 8601 format. |
| `updated_at` | `string` | The last update time of the note in ISO 8601 format. |
| `summary_text` | `string` | Plain text summary of the note. |
| `summary_markdown` | `string` | Markdown formatted summary of the note. |
| `attendees` | `array` | The attendees of the meeting. |
| `calendar_event` | `object` | Associated calendar event details. |
| `folder_membership` | `array` | The folder membership of the note. |
| `transcript` | `array` | Transcript of the meeting. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | The unique identifier of the note. |
| `data[].object` | `string` | The object type, always "note". |
| `data[].title` | `string` | The title of the note. |
| `data[].owner` | `object` | The owner of the note. |
| `data[].created_at` | `string` | The creation time of the note in ISO 8601 format. |
| `data[].updated_at` | `string` | The last update time of the note in ISO 8601 format. |
| `data[].summary_text` | `string` | Plain text summary of the note. |
| `data[].summary_markdown` | `string` | Markdown formatted summary of the note. |
| `data[].attendees` | `array` | The attendees of the meeting. |
| `data[].calendar_event` | `object` | Associated calendar event details. |
| `data[].folder_membership` | `array` | The folder membership of the note. |
| `data[].transcript` | `array` | Transcript of the meeting. |

</details>

### Notes Semantic Search

Search notes records by meaning rather than by exact or fuzzy field values. Semantic search embeds a natural-language `prompt` and returns the most similar passages, ranked by relevance. Pass a `semantic` object to `context_store_search` instead of `query`. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "granola",
  "entity": "notes",
  "action": "context_store_search",
  "params": {
    "semantic": {"field": "summary_markdown", "prompt": "<your natural-language query>"}
  }
}'
```

#### Python SDK

Semantic search is passed through the generic `execute` method — the typed `notes.context_store_search` helper only accepts `query`.

```python
await granola.execute(
    "notes",
    "context_store_search",
    {"semantic": {"field": "summary_markdown", "prompt": "<your natural-language query>"}},
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "notes",
    "action": "context_store_search",
    "params": {
        "semantic": {"field": "summary_markdown", "prompt": "<your natural-language query>"}
    }
}'
```

#### Semantic Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `semantic.field` | `string` | Yes | Field to search semantically. Mutually exclusive with `query`. |
| `semantic.prompt` | `string` | Yes | Natural-language query that is embedded and compared against stored passages. |
| `semantic.filter` | `object` | No | Filter conditions (same shape/operators as `query.filter`). `sort` is not supported — results are ranked by similarity. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, up to the field's configured window. Omit to return the full configured window. |
| `semantic.dedup` | `string` | No | `max` (default) returns the single best-scoring passage per record; `none` returns multiple passages per record, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in results (dot notation for nested fields). Applied to each hit's `entity`. |
| `limit` | `integer` | No | Maximum results to return (default 10, maximum 100). |

#### Semantically Searchable Fields

| Field Name | Max Context (chars) | Description |
|------------|---------------------|-------------|
| `summary_markdown` | 2048 | Markdown formatted summary of the note. |
| `transcript` | 2048 | Transcript of the meeting. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching passages |
| `data[].entity` | `object` | The matched source record |
| `data[].entity.id` | `string` | Source record field |
| `data[].entity.updated_at` | `string` | Source record field |
| `data[].entity.title` | `string` | Source record field |
| `data[].metadata` | `object` | Match metadata |
| `data[].metadata.score` | `number` | Similarity score |
| `data[].metadata.context` | `string` | The matched passage text |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

