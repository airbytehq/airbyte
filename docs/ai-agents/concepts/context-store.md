---
plan: all
sidebar_position: 2
---

# Context Store

The Context Store is a managed, searchable replica of select entities from all your connected data sources. Airbyte populates it from the connectors in your workspace and gives agents a fast, consistent way to search your business data without hitting the underlying APIs for every request.

Some third-party APIs have search endpoints, but many don't. Without the Context Store, prompts like these force your agent to list, page through, and filter records from the API in real time:

- `List all customers closing this month with deal sizes greater than $5000.`
- `Search all dresses and find the ones with a color option of red.`

Working this way causes a variety of problems:

- Unbounded growth of the context window
- Long-running queries
- Iterative collection of paginated lists of records
- API rate limiting

The result is a query that takes substantial time and resources to process, a degraded experience, and inflated costs.

The Context Store solves this problem by making key fields available to your agents in Airbyte-managed storage. Airbyte replicates a curated subset of the entities in your agent connectors into the store and keeps it up to date. Agents then answer these kinds of questions with fast, indexed searches instead of live API crawls.

## What's in the Context Store

Each connected source has its own isolated store. Airbyte curates the store for search, not archival.

- Airbyte selects a subset of fields and entities that are useful for search, not every record or field in the source.
- Each organization's data is only accessible to agents within that organization.
- Data in the store refreshes on a schedule that depends on your plan. See [Billing and pricing](../admin/billing) for details.

For the list of entities each connector contributes, see [Agent connectors](../connectors).

## Who manages the Context Store

The Context Store is enabled by default for every organization and operates at the organization level. Organization administrators can view Context Store status and monitor population progress from the Connectors page in the web app.

## Check Context Store status

You can check Context Store status in two places on the **Connectors** page: per connector and per entity.

### Per-connector status

Each connector in the Connectors list shows a status badge.

- **Ready.** The store is populated and fully available for search.
- **Preview.** The first population is still in progress, but some data is already searchable.
- **Building Preview.** The first population is in progress and no data is searchable yet.
- **Loading.** Airbyte is preparing the store for this connector.

Ready and Preview are both usable states for agents. Preview means newer records may still be arriving.

### Per-entity status

Click the status badge on a connector to open a detailed view. The view lists every entity Airbyte populates for the connector, along with:

- **Entity.** The entity name, for example `contacts`, `deals`, or `products`.
- **Status.** `Ready`, `Preview`, `Building Preview`, `Initializing`, or `Updating`.
- **Records.** The number of records currently searchable for that entity.
- **Last Synced** or **Last Updated.** The most recent time Airbyte refreshed that entity.

Use this view to confirm which entities are ready to query and which are still populating.

## How agents use the Context Store

When an agent processes a prompt, it chooses between two execution paths for each connector operation:

- **Context Store search.** The agent queries the pre-indexed replica in the Context Store. This path handles filtering, sorting, and aggregation without calling the third-party API, so it returns results faster and uses fewer tokens. Agents prefer this path when the entity is available in the Context Store.
- **Direct request.** The agent calls the third-party API in real time. This path always returns the most current data, and it's the only option for entities that aren't in the Context Store or for write operations like creating and updating records.

Agents choose between these paths automatically. You don't need to specify which path to use in your prompts. In chat, each tool call displays a badge that indicates whether it used the Context Store or a direct request.

## How search works

The Context Store supports structured search with filter operators, field selection, sorting, and cursor-based pagination. The agent translates user intent from natural language into a structured query, so you don't need to construct queries by hand.

If you build agents with the SDK or API, you can call `context_store_search` directly and pass structured filters. For details on the query model, see the individual [connector reference pages](../connectors), which document the available entities, filter fields, and search parameters for each connector.

## Semantic search

Structured search matches records by exact or fuzzy field values. Some connectors also support **semantic search**: a similarity search that finds relevant passages by meaning rather than by keyword. Instead of matching a filter, Airbyte embeds your natural-language query and returns the most similar chunks of text, ranked by relevance.

Semantic search is useful for long, unstructured text, such as call transcripts, issue descriptions, or the contents of a document, where the exact wording of a match isn't known in advance. For example, an agent can answer "find call passages where a customer raised pricing concerns" by searching the meaning of the transcript text, not a specific phrase.

Semantic search is an evolving capability and is available for a limited set of connectors and fields today. Agents choose it automatically when a prompt calls for meaning-based retrieval over a supported field. As with structured search, you don't need to specify the search mode in your prompts.

### Record text vs. file content

Semantic search comes in two flavors, depending on the connector:

- **Record text.** Data connectors (such as Gong and Linear) embed a text field of a structured record — a transcript, an issue description, a comment body. Each hit is a passage of that field, attributed to the record it came from.
- **File content.** File connectors (such as Google Drive) embed the extracted text of the files they sync. Each hit is a passage of a document's content, attributed to its source file (name, path, and other file metadata).

Both flavors use the same request shape — a `semantic` object passed to `context_store_search` — so agents call them the same way. The difference is what a passage represents: a field of a record, or a span of a file's contents.

### Connectors and fields that support semantic search

| Connector | Entity | Field | Searches |
| --------- | ------ | ----- | -------- |
| Gong | Call transcripts | Transcript text | Record text |
| Linear | Issues | Description | Record text |
| Linear | Comments | Body | Record text |
| Google Drive | Files | Content | File content |

Airbyte continues to add semantic search to more connectors and fields.

### Calling semantic search with the SDK or API

If you build agents with the SDK or API, you can request semantic search directly by passing a `semantic` object to `context_store_search`. In the SDK, use the generic `connector.execute(entity, "context_store_search", params)` method — the typed per-entity `context_store_search` helper accepts only a structured `query`, not a `semantic` object.

```json
{
  "entity": "call_transcripts",
  "action": "context_store_search",
  "params": {
    "semantic": {
      "field": "transcript",
      "prompt": "customer raised pricing concerns",
      "context_size": 2048,
      "dedup": "max"
    },
    "limit": 20
  }
}
```

Each hit is returned as an `{entity, metadata}` object, where `metadata` includes the similarity `score`, the matched `context` text, and connector-specific attribution fields.

Keep these rules in mind when constructing a request:

- **`semantic` and `query` are mutually exclusive.** Pass one or the other, never both in the same request.
- **Results are ranked by similarity, so `sort` isn't supported.** To filter results, put the filter inside `semantic.filter` using the same operators as `query.filter`.
- **`dedup` controls per-record deduplication.** `max` (the default) returns only the single best-scoring passage per source record. `none` returns multiple passages from the same record, still ranked by similarity and capped by `limit`.
- **`context_size` controls how many characters of surrounding context are returned per hit,** up to the field's configured window. Omit it to return the full configured window.

For the entities and fields available on each connector, see the individual [connector reference pages](../connectors).

## Initial index

When the Context Store populates data for a connector, Airbyte runs an initial index. Indexing time depends on the amount of data and third-party API rate limits, and can range from minutes to days.

During the initial index, Airbyte makes data available to agents progressively. You don't have to wait for the index to finish before agents can search. An entity in **Preview** status already has partial data that agents can query. As indexing continues, more records become searchable until the entity reaches **Ready** status.

The per-entity detail view on the Connectors page shows record counts and timestamps so you can track indexing progress.

## When to use the Context Store

The Context Store is always on and requires no configuration. It benefits most workflows by default:

- Agents can search across large amounts of connector data with predictable latency.
- Prompts like "find all X where Y" run as a single search instead of a live API crawl.
- Search behavior is consistent across connectors, including connectors whose APIs don't offer their own search endpoint.

## Limitations

- **Data freshness.** The Context Store is not real-time. Airbyte refreshes data on a schedule that depends on your plan, ranging from hourly to daily. See [Billing and pricing](../admin/billing) for refresh cadence by plan.
- **Curated subset of data.** Not every field or entity from a source is included. Airbyte indexes only the fields and entities that are most useful for search. You can see which entities populate the Context Store when selecting entities in the authentication widget.
- **Initial indexing delay.** The first time Airbyte populates a connector, the [initial index](#initial-index) can take minutes to days depending on data volume and API rate limits.
- **Read-only.** The Context Store supports search operations only. Write operations like creating, updating, or deleting records always go through a direct API request.
