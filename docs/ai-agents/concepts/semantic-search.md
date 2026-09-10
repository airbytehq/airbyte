---
plan: all
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Semantic search

Structured [Context Store](./context-store) search matches records by exact or fuzzy field values. Semantic search is a different mode: a similarity search that finds relevant passages by *meaning* rather than by keyword. Instead of matching a filter, Airbyte embeds your natural-language prompt as a vector, compares it against the stored text, and returns the most similar passages, ranked by relevance.

Semantic search suits long, unstructured text, such as call transcripts, issue descriptions, or the contents of a document, where you don't know the exact wording of a match in advance. For example, an agent can answer "find call passages where a customer raised pricing concerns" by searching the meaning of the transcript text, not a specific phrase.

:::note Alpha
Semantic search is an alpha capability. The request and response shapes described here can change, and it's available for a limited set of connectors and fields today. See [Supported connectors and fields](#supported-connectors-and-fields).
:::

## How it works

Airbyte indexes each supported text field ahead of time:

1. **Extract and split.** Airbyte takes the source text (a record field or the extracted contents of a file) and splits it into passages, such as speaker turns, paragraphs, or document chunks.
2. **Embed.** Each passage is converted into a numeric vector (an embedding) that captures its meaning, and stored in the Context Store.
3. **Rank at query time.** When you search, Airbyte embeds your `prompt` the same way and returns the passages whose vectors are most similar, each with a relevance `score` and the surrounding `context` text.

Because similarity determines the order, results come back ranked from most to least relevant. You don't sort them yourself.

## Record text vs. file content

Semantic search comes in two flavors, depending on the connector. Both use the same request shape, so agents call them the same way. What differs is what a passage represents.

- **Data connectors (record text).** Connectors such as Gong and Linear embed a text field of a structured record: a transcript, an issue description, a comment body. Each hit is a passage of that field, attributed to the record it came from.
- **File connectors (file content).** Connectors such as Google Drive embed the extracted text of the files they sync. Each hit is a passage of a document's content, attributed to its source file, such as name, path, and MIME type.

## Supported connectors and fields

Semantic search is available on a growing set of connectors and fields, so this page doesn't maintain a fixed list. To check whether a connector supports it, open its [connector documentation](../connectors): an entity supports semantic search when a **Semantic Search** action appears in its list of actions. This action shows up in the entity table on the connector's overview page and in its full reference, which documents the exact field, request, and response.

The examples on this page use Gong (a data connector) and Google Drive (a file connector).

## How you invoke it

- **Web app.** In the agent chat, ask in natural language. The agent uses semantic search automatically when it's available for the data you're asking about.
- **Agent MCP.** Same as the web app. Semantic search isn't a separate MCP tool. Your agent calls the connector's `context_store_search` action with a `semantic` object when your prompt calls for meaning-based retrieval.
- **CLI, API, and SDK.** You build the request yourself by passing a `semantic` object to the `context_store_search` action. The two sections below show complete examples for each.

## Request shape

Whether the connector is a data connector or a file connector, a semantic search is a `context_store_search` call whose `params` carry a `semantic` object instead of a structured `query`.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `semantic.field` | `string` | Yes | The indexed field to search, as listed on the connector's reference page. |
| `semantic.prompt` | `string` | Yes | The natural-language query. Airbyte embeds it and compares it against the field's stored passages. |
| `semantic.filter` | `object` | No | A filter applied alongside the similarity match, using the same operators and dot notation as `query.filter`. |
| `semantic.min_similarity` | `number` | No | Minimum similarity score a hit must reach, from -1.0 to 1.0. Defaults to 0.25. Set it to -1.0 to return every hit regardless of score. |
| `semantic.context_size` | `integer` | No | Characters of surrounding context to return per hit, centered on the match and capped at the field's configured window. Omit it to return the full window. |
| `semantic.dedup` | `string` | No | `max` (the default) returns the single best-scoring passage per source record or file. `none` returns multiple passages from the same source, still ranked by similarity and capped by `limit`. |
| `fields` | `array` | No | Field paths to include in each hit's `entity`, using dot notation for nested fields. |
| `limit` | `integer` | No | Maximum number of hits to return. Defaults to 10, with a maximum of 100. |

Keep these rules in mind:

- **`semantic` and `query` are mutually exclusive.** Pass one or the other, never both in the same request.
- **`sort` isn't supported.** Results are always ranked by similarity. To narrow them, use `semantic.filter`.

## Response shape

A semantic search returns a `data` array of hits and a `meta` object. Each hit separates the source from the match:

- `data[].entity` holds the source record's or source file's own fields.
- `data[].metadata` holds everything that describes the match: the similarity `score`, the matched `context` text, and any per-passage attribution or [enrichment](../connectors) fields the connector adds. Enrichment outputs are returned only and can't be filtered.

```json title="Search result"
{
  "data": [
    {
      "entity": { "...": "source record or file fields" },
      "metadata": {
        "score": 0.82,
        "context": "...the matched passage of text..."
      }
    }
  ],
  "meta": {
    "has_more": false,
    "cursor": null,
    "took_ms": 42
  }
}
```

The CLI and API wrap this object in the standard [execute envelope](../interfaces/api/execute#response-format): the `{data, meta}` result lands in the response's `result` field.

## Search data connectors

Data connectors search a text field of a structured record. The example below searches Gong call transcripts for passages about pricing concerns. Each hit is attributed to its call, and Gong enriches hits with the speaker's name, title, and affiliation under `metadata`.

<Tabs groupId="interface">
<TabItem value="cli" label="CLI" default>

```bash title="Request"
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "Gong",
  "entity": "call_transcripts",
  "action": "context_store_search",
  "params": {
    "semantic": {
      "field": "transcript",
      "prompt": "customer raised concerns about pricing"
    },
    "limit": 10
  }
}'
```

</TabItem>
<TabItem value="api" label="API">

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "call_transcripts",
    "action": "context_store_search",
    "params": {
      "semantic": {
        "field": "transcript",
        "prompt": "customer raised concerns about pricing"
      },
      "limit": 10
    }
  }'
```

</TabItem>
<TabItem value="sdk" label="SDK">

Pass the `semantic` object through the generic `execute` method. The typed `call_transcripts.context_store_search` helper accepts only a structured `query`, not a `semantic` object.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import connect

async def main():
    gong = connect("gong")
    try:
        result = await gong.execute(
            "call_transcripts",
            "context_store_search",
            {
                "semantic": {
                    "field": "transcript",
                    "prompt": "customer raised concerns about pricing",
                },
                "limit": 10,
            },
        )
        for hit in result.data["data"]:
            print(hit["metadata"]["score"], hit["metadata"]["context"])
    finally:
        await gong.close()

asyncio.run(main())
```

</TabItem>
<TabItem value="mcp" label="Agent MCP">

Ask your agent in natural language, for example *"find Gong calls where a customer raised pricing concerns."* The agent calls `context_store_search` with a `semantic` object automatically when it fits your prompt. There's no separate semantic-search tool.

</TabItem>
<TabItem value="webapp" label="Web app">

In the agent chat, ask in natural language. The agent uses semantic search automatically when it's available for the data you're asking about.

</TabItem>
</Tabs>

A hit looks like this. The call's own fields are under `entity`; the score, matched context, and speaker enrichment are under `metadata`.

```json title="Search result"
{
  "data": [
    {
      "entity": {
        "callId": "7830000000000000000",
        "started": "2024-05-14T17:00:00Z"
      },
      "metadata": {
        "score": 0.79,
        "context": "...honestly that number is more than we budgeted for a team our size...",
        "speakerName": "Jordan Lee",
        "speakerTitle": "VP Finance",
        "speakerAffiliation": "external"
      }
    }
  ],
  "meta": { "has_more": false, "cursor": null, "took_ms": 51 }
}
```

## Search file connectors

File connectors search the extracted text content of the files they sync. The example below searches a Google Drive connector for passages about renewal terms. Each hit is a passage of a document's content, attributed to its source file.

<Tabs groupId="interface">
<TabItem value="cli" label="CLI" default>

```bash title="Request"
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "Google Drive",
  "entity": "files",
  "action": "context_store_search",
  "params": {
    "semantic": {
      "field": "content",
      "prompt": "auto-renewal terms in our vendor agreements"
    },
    "limit": 10
  }
}'
```

</TabItem>
<TabItem value="api" label="API">

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "entity": "files",
    "action": "context_store_search",
    "params": {
      "semantic": {
        "field": "content",
        "prompt": "auto-renewal terms in our vendor agreements"
      },
      "limit": 10
    }
  }'
```

</TabItem>
<TabItem value="sdk" label="SDK">

Pass the `semantic` object through the generic `execute` method. The typed `files.context_store_search` helper accepts only a structured `query`, not a `semantic` object.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import connect

async def main():
    google_drive = connect("google-drive")
    try:
        result = await google_drive.execute(
            "files",
            "context_store_search",
            {
                "semantic": {
                    "field": "content",
                    "prompt": "auto-renewal terms in our vendor agreements",
                },
                "limit": 10,
            },
        )
        for hit in result.data["data"]:
            print(hit["entity"]["file_name"], hit["metadata"]["score"])
    finally:
        await google_drive.close()

asyncio.run(main())
```

</TabItem>
<TabItem value="mcp" label="Agent MCP">

Ask your agent in natural language, for example *"search Google Drive for the auto-renewal terms in the vendor agreements."* The agent calls `context_store_search` with a `semantic` object automatically when it fits your prompt. There's no separate semantic-search tool.

</TabItem>
<TabItem value="webapp" label="Web app">

In the agent chat, ask in natural language. The agent uses semantic search automatically when it's available for the data you're asking about.

</TabItem>
</Tabs>

A hit looks like this. The source file's attribution fields are under `entity`; the score and matched passage are under `metadata`.

```json title="Search result"
{
  "data": [
    {
      "entity": {
        "id": "1AbC...",
        "file_name": "2024-vendor-agreement.pdf",
        "file_path": "/Contracts/2024-vendor-agreement.pdf",
        "mime_type": "application/pdf",
        "updated_at": "2024-06-02T09:12:00Z"
      },
      "metadata": {
        "score": 0.84,
        "context": "...this agreement continues for successive one-year periods unless either party gives written notice 30 days beforehand..."
      }
    }
  ],
  "meta": { "has_more": false, "cursor": null, "took_ms": 63 }
}
```

## Search across your whole workspace

The connector-local searches above target one connector, entity, and field. Workspace-wide semantic search takes a prompt and a workspace, searches every connector in that workspace whose Context Store data supports semantic search, ranks all hits together by similarity, and returns one merged list. It searches only the workspace you name, not every workspace in your organization.

Use workspace-wide semantic search for discovery when you don't know which connector holds the answer, such as "where did anyone mention the ACME renewal?" Use connector-local search when you already know the connector, entity, and field and want filters, field selection, or pagination.

### Availability

- Available today through the **REST API** endpoint below and in the **web app agent chat**. The agent searches your whole workspace when your question isn't scoped to one connector.
- Not available in the **CLI**, the **Python SDK**, or the **Agent MCP**. For those interfaces, call `context_store_search` per connector as shown above.
- Workspace-wide semantic search is alpha. The request and response shapes can change.

### Request

```text
POST https://api.airbyte.ai/api/v1/integrations/connectors/search
```

This endpoint requires an [application token](../interfaces/api/authentication). Scoped tokens are rejected with `401`.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `workspace_id` | `string (uuid)` | Required (one of) | The workspace to search, resolved within your organization. Pass either this or `workspace_name`, not both. |
| `workspace_name` | `string` | Required (one of) | The workspace name, as an alternative to `workspace_id`. |
| `prompt` | `string` | Yes | The natural-language query. It can't be empty. |
| `limit` | `integer` | No | Maximum merged hits to return. Defaults to 10, with a maximum of 100. |
| `min_similarity` | `number` | No | Minimum similarity score a hit must reach, from `-1.0` to `1.0`. Defaults to `0.25`. Set it to `-1.0` to turn off the cutoff. |
| `include_entity_data` | `boolean` | No | When `true`, each hit carries the source record's own fields as `entity_data`. Defaults to `false`. |
| `select_fields` | `array` | No | A list of allowed dot-notation field paths to include in `entity_data`. Passing it opts into `entity_data` and takes precedence over `include_entity_data`. |

Unknown fields are rejected.

```bash title="Request"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/search' \
  --header 'Authorization: Bearer <your_application_token>' \
  --header 'Content-Type: application/json' \
  --data '{
    "workspace_name": "default",
    "prompt": "customers unhappy about pricing",
    "limit": 10
  }'
```

### Response

This endpoint returns a flat `{data, meta}` body. Unlike connector `execute` calls, it is not wrapped in the [execute envelope](../interfaces/api/execute#response-format), and it does not use cursor pagination.

```json title="Search result"
{
  "data": [
    {
      "connector_instance_id": "9f1c2e7a-4b3d-4a10-8f21-5c6d7e8a9b01",
      "connector_instance_name": "Gong",
      "connector_type": "gong",
      "entity": "call_transcripts",
      "field": "transcript",
      "record_key": {
        "name": "call_id",
        "value": "7830000000000000000"
      },
      "score": 0.91,
      "context": "...the renewal price is higher than we expected...",
      "metadata": {
        "speaker_name": "Jordan Lee",
        "speaker_role": "VP Finance"
      },
      "entity_data": null
    },
    {
      "connector_instance_id": "3a7b5c11-9d02-4e64-b8f3-1c2d3e4f5a67",
      "connector_instance_name": "Linear",
      "connector_type": "linear",
      "entity": "issues",
      "field": "description",
      "record_key": {
        "name": "issue_id",
        "value": "ENG-142"
      },
      "score": 0.84,
      "context": "...the customer is unhappy with the new pricing...",
      "metadata": {
        "team": "Engineering",
        "status": "In Progress"
      },
      "entity_data": null
    }
  ],
  "meta": {
    "elapsed_ms": 248,
    "searched_connectors": 2,
    "searched_targets": 2,
    "partial": false,
    "failures": []
  }
}
```

Each hit can include these fields:

- `connector_instance_id` identifies the connector instance.
- `connector_instance_name` is the name you gave the connector in Airbyte.
- `connector_type` is the connector's technical type, such as `gong`.
- `entity` is the source entity, such as `call_transcripts` or `issues`.
- `field` is the semantically indexed source field.
- `record_key` is an object with `name` and `value` that identifies the source record.
- `score` is the similarity score. Hits are returned in descending score order.
- `context` is the passage that matched the prompt.
- `metadata` contains per-passage attribution and enrichment.
- `entity_data` contains the source record's fields, or `null` unless you ask for them with `include_entity_data` or `select_fields`.

The `meta` object contains:

- `elapsed_ms`, the search time in milliseconds.
- `searched_connectors`, the number of connector instances searched.
- `searched_targets`, the number of searchable connector targets.
- `partial`, whether some connectors failed or timed out.
- `failures`, an array of failures. Each failure includes `connector_instance_id`, `connector_instance_name`, and a `reason`.

### Partial results and errors

- Connectors whose Context Store data isn't ready or that have no semantically indexed fields are skipped. An empty `data` with `searched_connectors: 0` means nothing in the workspace was searchable yet.
- When some connectors fail or time out, `meta.partial` is `true` and each skipped connector appears in `meta.failures` with a reason. The hits that succeeded are still returned and ranked.
- `404` means the workspace wasn't found.
- `409` means the workspace's searchable connectors don't share one embedding model, so their scores aren't comparable. Search those connectors individually instead.
- `503` means the search couldn't complete for any connector.

## Related

- **[Context Store](./context-store).** How Airbyte indexes and serves your data.
- **[Agent connectors](../connectors).** Per-connector reference for the entities and fields that support semantic search.
- **[Execute operations](../interfaces/api/execute).** The execute request and response envelope shared by every action.
