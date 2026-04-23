---
sidebar_position: 3
---

# Time zones

Airbyte Agents handles dates and times the same way across every interface: display in your local time, store and transport in UTC, and schedule Automations in a time zone you choose. This page explains how that works and what to expect in each interface.

## The short version

- **Display**: The [web app](../interfaces/ui) formats every date and time in the local time zone set in your browser.
- **Storage**: The backend stores every timestamp in UTC.
- **Data in transit**: The [API](../interfaces/api), [SDK](../interfaces/sdk), and [MCP server](../interfaces/mcp) read and return timestamps in UTC, formatted as ISO 8601 strings.
- **Automation schedules**: You pick a time zone per Automation. Airbyte stores it as an [IANA time zone identifier](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (for example, `America/New_York` or `Asia/Kolkata`).

## Display in the web app

Every timestamp the web app shows—run history, session tables, activity feeds, Automation schedules—renders in the time zone the browser reports. If you travel, change your operating system's time zone, or open the app in a different browser profile, the same timestamp displays in the new local time. The underlying value doesn't change; only the formatting does.

This applies to both absolute times (for example, `Mar 18, 09:32`) and relative times (for example, `2 hours ago`).

## Storage and data in transit

All timestamps are UTC on the backend, and every interface that reads or writes timestamps uses UTC on the wire:

- **API**: Request and response bodies use ISO 8601 UTC strings (for example, `2026-03-18T13:32:00Z`).
- **SDK**: The Python SDK returns the same UTC ISO 8601 strings through its response models.
- **MCP server**: Tools that return timestamps return them in UTC. The `current_datetime` tool, which an agent calls to resolve relative dates like "today" or "last week," returns the current UTC time.

If you pass a timestamp into a connector action—for example, as a date filter on a list query—use UTC. The agent doing the calling is responsible for any time zone conversion before it hands the value to the platform.

## Scheduling Automations

Every scheduled [Automation](../interfaces/ui/automations) has its own time zone, stored as an IANA identifier alongside its cron expression. When the schedule fires, Airbyte evaluates the cron in that time zone, so `0 9 * * MON-FRI` means 9 AM local time for the chosen zone, whether that's `America/Los_Angeles` or `Asia/Tokyo`.

The default time zone depends on how you create the Automation:

- **From the web app**: The [Automation Builder](../interfaces/ui/automations#the-automation-builder) defaults to your browser's local time zone. Pick a different zone from the dropdown if you want the schedule to fire somewhere else.
- **From the Automation Builder chat agent**: The agent uses this precedence when it creates or updates a schedule:
  1. An explicit time zone you state in the prompt (for example, "at 9 AM Tokyo time").
  2. Your browser's local time zone, which the web app sends with every message.
  3. UTC, if neither is available.

  The agent only ever passes IANA identifiers. If you say "EST" or "Eastern Time," it translates to `America/New_York` before calling the tool.

### Interpreting times in an Automation's prompt

A scheduled Automation can run for a long time without you watching it. If your prompt includes relative words like "today," "this week," or "last month," the agent resolves them to a concrete date and time when the run starts. It does this by calling `current_datetime` (UTC) and then reasoning about the window. Be explicit about the zone if the result depends on it (for example, "today in US Pacific time").

## Time zones and MCP clients

The MCP server at [`mcp.airbyte.ai`](../interfaces/mcp) is accessed by external AI clients such as Claude, Cursor, and ChatGPT. It authenticates each user with OAuth but doesn't receive the client's local time zone. Two things follow from this:

- **Times on the wire are UTC.** The MCP tools accept and return UTC timestamps.
- **Time zone reasoning is the client agent's job.** When you ask your agent "what happened today?" or "show me deals closing this month," the agent needs to decide what "today" and "this month" mean. Most clients resolve relative dates using their host environment's time zone. Tell the agent the zone explicitly if you need precision.

The MCP server doesn't currently expose tools for creating, updating, or running Automations. However, if you used it with an agent that supports automations, it runs according to the settings that agent is designed to use.

## Related topics

- [Automations](../interfaces/ui/automations) — Pick a schedule and time zone.
- [Sessions](../admin/sessions) — Review when Automation runs and chat sessions happened.
- [MCP server](../interfaces/mcp) — Connect an external agent to Airbyte.
