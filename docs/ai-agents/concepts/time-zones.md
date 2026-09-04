---
plan: all
sidebar_position: 3
---

# Time zones

Airbyte Agents handles dates and times the same way across every interface: display in your local time, and store and transport in UTC. This page explains how that works and what to expect in each interface.

## The short version

- **Display**: The [web app](../interfaces/ui) formats every date and time in the local time zone set in your browser.
- **Storage**: The backend stores every timestamp in UTC.
- **Data in transit**: The [API](../interfaces/api), [SDK](../interfaces/sdk), and [MCP server](../interfaces/mcp) read and return timestamps in UTC, formatted as ISO 8601 strings.

## Display in the web app

Every timestamp the web app shows (run history, session tables, activity feeds) renders in the time zone the browser reports. If you travel, change your operating system's time zone, or open the app in a different browser profile, the same timestamp displays in the new local time. The underlying value doesn't change; only the formatting does.

This applies to both absolute times (for example, `Mar 18, 09:32`) and relative times (for example, `2 hours ago`).

## Storage and data in transit

All timestamps are UTC on the backend, and every interface that reads or writes timestamps uses UTC on the wire:

- **API**: Request and response bodies use ISO 8601 UTC strings (for example, `2026-03-18T13:32:00Z`).
- **SDK**: The Python SDK returns the same ISO 8601 UTC strings through its response models.
- **MCP server**: Tools that return timestamps return them in UTC. The `current_datetime` tool, which an agent calls to resolve relative dates like "today" or "last week," returns the current UTC time.

:::warning
If you pass a timestamp into a connector action (for example, as a date filter on a list query), use UTC. The agent doing the calling is responsible for any time zone conversion before it hands the value to the platform.
:::

## Time zones and MCP clients

The MCP server at [`mcp.airbyte.ai`](../interfaces/mcp) is accessed by external AI clients such as Claude, Cursor, and ChatGPT. It authenticates each user with OAuth but doesn't receive the client's local time zone. Two things follow from this:

- **Times on the wire are UTC.** The MCP tools accept and return UTC timestamps.
- **Time zone reasoning is the client agent's job.** When you ask your agent "what happened today?" or "show me deals closing this month," the agent needs to decide what "today" and "this month" mean. Most clients resolve relative dates using their host environment's time zone. Tell the agent the zone explicitly if you need precision.

## Related topics

- [Sessions](../admin/sessions): Review when chat sessions happened.
- [MCP server](../interfaces/mcp): Connect an external agent to Airbyte.
