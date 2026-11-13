---
products: cloud-no-flex
---

# Search your data

Search lets your AI agent query an index Airbyte builds from the data your connections sync. Use it to find records by keyword, meaning, or both without knowing the exact record ID or table. Airbyte stores the indexed data on its own infrastructure.

Search is a read-only part of the [context layer](readme.md). It works independently of [agent access](agent-access.md).

## Find relevant records

Use search when you need information from lots of synced text, such as support tickets, conversations, or notes, but don't know record IDs or the exact words people used. For example, an agent can find onboarding problems even when customers describe them as "getting started" or "setting up an account."

An index helps agents retrieve relevant records faster and with less context than paging through APIs. Results reflect indexed syncs or backfills, so they might not include the latest source changes.

Search supports three modes:

| Mode | When to use it |
| :--- | :--- |
| Keyword | Find specific words, names, or error messages. |
| Semantic | Find records by meaning, even when they use different words than your question. |
| Hybrid (default) | Combine keyword and semantic matches when your question includes both specific terms and broader concepts. |

## How indexing works

Both the source and destination must be agent connectors. Search uses the streams selected in a connection, not every stream available in the source.

After you [turn on search and select connections](manage-access.md#manage-search), Airbyte indexes data written by subsequent syncs. It organizes that data so your agent can find records by exact terms or meaning. Turning on search doesn't index data already in the destination.

## Backfill existing data

Start a backfill when you want agents to find data synced before you turned search on. A backfill reads that existing data from your connection's destination and adds it to the index. For example, backfill the last three months to include recent support history without indexing years of older tickets. Backfills support Snowflake and BigQuery destinations only. Snowflake requires username and password or key pair authentication. BigQuery requires a service account key.

1. Open **Context layer** > **Semantic search**.
2. Find the connection. Make sure **Semantic search** is on.
3. Set a **Backfill date** to limit how far back Airbyte reads. If you leave it empty, the UI uses a date one year ago.
4. Click **Start backfill**.

The start date applies to streams with a top-level timestamp or date cursor. Airbyte backfills rows whose cursor is at or after that date. Streams without such a cursor are backfilled in full.

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

[Connect your agent to the Airbyte MCP](../airbyte-mcp/install.md), then ask a question in plain language. You can ask about one source or search across the sources indexed through a destination. If a source syncs to several destinations, tell your agent which destination to use.

Results include matching records and context that helps your agent answer your question. For tool details, see [Search tools](../airbyte-mcp/tools.md#search).

### Check status and start a backfill

In Airbyte, open **Context layer** > **Semantic search** to check backfill progress or start a backfill. You can also ask your agent: "Check which streams are indexed for our Zendesk source and whether the backfill has finished" or "Backfill this connection's tickets from January 1, 2026, in UTC."

### Example prompts

- "Search our support tickets for conversations about customers struggling with onboarding. Use semantic search and return 10 results."
- "Find tickets mentioning error E104 using keyword search."
- "Search the sources indexed through our Snowflake destination for Acme renewal concerns. Use hybrid search."

## Troubleshoot empty results

If a search returns no results:

1. Check that **Semantic search** is on for your organization and connection.
2. Ask your agent to check indexing status. Confirm that the streams you need are indexed and that the backfill has completed.
3. If the data was synced before you turned on search, [start a backfill](#backfill-existing-data). Otherwise, allow your next sync and indexing work to finish.
4. Make sure you're asking about the right source, destination, and time period. Try a broader question, include more history, or ask for keyword or hybrid search.

## Limitations

- Search is available only in Airbyte Cloud, not self-managed Airbyte Core or Enterprise. It isn't available for connections running on customer-owned Enterprise Flex data planes. Keep search off for those connections: if search is on, their syncs fail before they start.
- Search is read-only and reflects indexed data, not live changes.
- Searches count toward the [shared context layer usage limit](readme.md#usage-limits).
- [Turning off search](manage-access.md#turn-off-search) deletes the affected index. Re-enabling it requires a new backfill for previously synced data.
