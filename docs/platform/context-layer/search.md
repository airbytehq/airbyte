---
products: cloud
---

# Search your data

Search lets your AI agent query an index Airbyte builds from the data your connections sync. Use it to find records by keyword, meaning, or both without knowing the exact record ID or table. Airbyte stores the indexed data on its own infrastructure.

Search is part of the [context layer](readme.md) and is available only in Airbyte Cloud. Searches are read-only: they don't change records in your sources or destinations.

## Choose search or direct reads

[Direct reads](readme.md#what-are-direct-reads) query a source's API or run SQL on a destination when your agent needs data. Search queries an index instead. Its freshness depends on your syncs and indexing progress, so it might not include the latest changes in your source.

Use search to find relevant tickets, conversations, or other records when you don't know their IDs. Use direct reads to retrieve a known record's current state or query your warehouse with SQL.

Search supports three modes:

| Mode | When to use it |
| :--- | :--- |
| Keyword | Find specific words, names, or error messages. |
| Semantic | Find records by meaning, even when they use different words than your question. |
| Hybrid (default) | Combine keyword and semantic matches when your question includes both specific terms and broader concepts. |

## Turn on search

Agent connectors support agent access for direct reads and search. To index a connection's synced data for search, both the source and destination must be agent connectors. Search uses the streams selected in the connection, not every stream available in the source.

1. As an organization administrator, open **Context layer** and turn on **Semantic search** in the settings.
2. Review and accept the new terms of service for storing indexed data on Airbyte infrastructure.
3. Open the **Semantic search** page and turn on **Semantic search** for each connection you want to index. You need workspace edit permission to change this setting.

After your organization enables search, new eligible connections have **Semantic search** on by default. You can change this option when you create a connection or in its settings.

Airbyte indexes data written by syncs that run after you turn on search for the connection. Turning on search doesn't index data already in the destination. To include that data, start a backfill.

## Backfill existing data

A search backfill reads data already in your connection's destination and adds it to the index. Backfills support Snowflake and BigQuery destinations only. Snowflake requires username and password or key pair authentication. BigQuery requires a service account key.

1. Open **Context layer** > **Semantic search**.
2. Find the connection. Make sure **Semantic search** is on.
3. Set a **Backfill date** to limit how far back Airbyte reads. If you leave it empty, the UI uses a date one year ago.
4. Click **Start backfill**.

The start date applies to streams with a top-level timestamp or date cursor. Airbyte backfills rows whose cursor is at or after that date. Streams without such a cursor are backfilled in full. To backfill the full history through the MCP, omit `backfill_start_time`.

Backfills are free in Airbyte, but they use compute in your destination, which your destination provider may charge for. Choose a start date that includes only the history you need to reduce destination costs.

The **Backfill status** column shows:

| Status | Meaning |
| :--- | :--- |
| Backfill off | No backfill is active. |
| Running | A backfill is in progress. A percentage appears when progress is available. |
| Complete | The backfill finished. |
| Failed | The backfill failed. Click **Start backfill** to try again. |
| Unknown | Airbyte couldn't fetch the status and keeps trying in the background. |

## Search with the Airbyte MCP

[Connect your agent to the Airbyte MCP](../airbyte-mcp/install.md), then ask a question in plain language. Your agent uses `execute_external_search_query` to search a source or destination by its connector ID.

A source search searches that source's indexed data. A destination search searches across its indexed sources. You can guide your agent with these parameters:

| Parameter | What it controls |
| :--- | :--- |
| `prompt` | The words or question to search for. |
| `search_type` | The mode: `keyword`, `semantic`, or `hybrid`. Defaults to `hybrid`. |
| `limit` | The maximum number of results, from 1 to 100. Defaults to 10. |
| `streams` | The streams to search. Omit it to search every indexed stream, or pass an empty list to search none. Each entry includes `stream_name` and can include `namespace` to distinguish streams with the same name. |
| `streams[].source_id` | The source that owns a stream. Required for each stream in a destination search. Optional in a source search, where it must match the source you're searching. |
| `streams[].fields` | The fields to return in each result's `entity_data`. This is an output projection, not a match filter: other indexed fields can still match and appear in the context. Omit it for the full indexed payload, or use an empty list for no payload fields. |
| `lookback_seconds` | Restrict results to records whose cursor falls within this many seconds. |
| `min_similarity` | The minimum semantic similarity for a match. Applies to semantic and hybrid searches only. |
| `max_similarity_diff` | The maximum similarity gap from the best semantic match in an index. Applies to semantic and hybrid searches only. |
| `max_context_chars` | Limit the text context returned for each result. A shortened keyword context stays centered on the match. |
| `destination_id` | Choose which destination's index to use for a source search. Required when the source syncs to multiple enabled destinations. |

Results include the source, stream, record ID, indexed record data, score, and matching context. Search results aren't a substitute for a complete record: use a direct read if you need its full current contents.

### Check status and request a backfill

Your agent can use `get_cloud_search_status` on a source or destination to check which streams are indexed and track backfill progress. For a source with multiple destinations, it also identifies the destinations you can search through.

To backfill through the MCP, use `request_cloud_search_index_backfill` with the connection ID. Optionally, provide `streams` to backfill specific selected streams and `backfill_start_time` to limit the history. Omit `streams` to backfill every stream selected in the connection. This tool requests indexing work; it doesn't change records in your destination, but the backfill uses destination compute.

### Example prompts

- "Search our support tickets for conversations about customers struggling with onboarding. Use semantic search and return 10 results."
- "Find tickets mentioning error E104 using keyword search."
- "Search the sources indexed through our Snowflake destination for Acme renewal concerns. Use hybrid search."
- "Check which streams are indexed for our Zendesk source and whether the backfill has finished."
- "Backfill the tickets stream for this connection from January 1, 2026, in UTC."

## Troubleshoot empty results

If a search returns no results:

1. Check that **Semantic search** is on for your organization and connection.
2. Ask your agent to call `get_cloud_search_status`. Confirm that the streams you need are indexed and that the backfill has completed.
3. If the data was synced before you turned on search, [start a backfill](#backfill-existing-data). Otherwise, allow your next sync and indexing work to finish.
4. Check your stream selectors, destination, lookback, and similarity settings. Try a broader prompt or another search mode.

## Turn off search

Turn off **Semantic search** for a connection to stop indexing it, or turn off the organization setting to stop search for the organization. Turning off search deletes the affected index. If you turn it on again, you need a new backfill to search previously synced data, which uses destination compute again.

## Usage limits

Searches and direct reads share the same limit of 100,000 requests per organization per month at no cost. See [Context layer usage limits](readme.md#usage-limits).
