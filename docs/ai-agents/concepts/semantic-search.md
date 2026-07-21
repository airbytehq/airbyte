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
        for hit in result.data:
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
        for hit in result.data:
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

## Related

- **[Context Store](./context-store).** How Airbyte indexes and serves your data.
- **[Agent connectors](../connectors).** Per-connector reference for the entities and fields that support semantic search.
- **[Execute operations](../interfaces/api/execute).** The execute request and response envelope shared by every action.
