> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-zendesk-chat

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Zendesk Chat (Zopim) API offers incremental exports for high-volume endpoints (chats, agents, bans, agent_timeline) via the Incremental API, but Zendesk stops serving that API to third-party integrations such as Airbyte between 2026-12-02 and 2027-01-19 (see "Unique behaviors" below). The `chats` stream therefore reads through Search Chats plus List Chats since 2.0.0; `agent_timeline` still reads the incremental export because it has no replacement endpoint. The remaining FR parent streams are config-style lookups (accounts, departments, goals, roles, routing_settings, shortcuts, skills, triggers) that do not support date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Singleton account config |
| agent_timeline | medium | top-level parent | start_time | start_time | incremental |  |
| agents | medium | top-level parent | id | id | incremental |  |
| bans | medium | top-level parent | id | id | incremental |  |
| chats | medium | child of internal `chats_search` parent | timestamp | search windows on update_timestamp | incremental | Search Chats + List Chats since 2.0.0; state migrated from `update_timestamp` |
| departments | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| goals | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| roles | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| routing_settings | small | top-level parent | none | none | deferred_no_api_support | Singleton config endpoint |
| shortcuts | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| skills | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| triggers | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |

### Future incremental stream candidates

- **No API date filter (8 streams):** `accounts`, `departments`, `goals`, `roles`, `routing_settings`, `shortcuts`, `skills`, `triggers` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.

## Unique behaviors

### 1. `chats` is a search-then-fetch substream, not a single endpoint read

Zendesk [stops serving the Incremental Exports API to third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498) between 2026-12-02 and 2027-01-19 (blocked requests return HTTP 403), and the only replacement for `incremental/chats` is the regular Chats API. Since 2.0.0 the `chats` stream is a substream of the internal `chats_search` parent (defined in `definitions.streams`, deliberately not listed under `streams`, so it never appears in the catalog). The parent calls [Search Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#search-chats) with `q=update_timestamp:[start TO end]` in one-day windows from the cursor (minus a one-day lookback) to now, paginating with the `page` number taken from `next_url` (40 results per page). The child groups the ids found with a `GroupingPartitionRouter` (50 ids per group, the documented maximum of the `ids` parameter) and calls [List Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#list-chats) with `ids=`, whose response is a `docs` map keyed by chat id, hence the `["docs", "*"]` extractor path. Groups span search windows, so a group can contain ids from several days. An id that List Chats no longer has (a chat deleted between the search and the fetch) comes back as `"<id>": null` with HTTP 200; the child's `record_filter` drops those nulls, which would otherwise fail schema normalization and the sync.

Both cursors are `timestamp` (the chat start time), while the search filter is `update_timestamp`: the search window therefore catches chats that were updated after they first synced, and the state (the maximum `timestamp` seen) never moves past a chat that still has to be read. `update_timestamp` itself is not in the List Chats payload, so it cannot be the cursor; `deleted`, `update_timestamp` and `engagements` only exist in the incremental export and were dropped from the schema. The `ChatsStateMigration` component converts the pre-2.0.0 state (`{"update_timestamp": <epoch seconds or ISO>}`) into the global-cursor shape with a matching `parent_state` for `chats_search`, so upgrades resume without a re-read from `start_date`.

Search Chats returns at most 10,000 results per query (page 251 is a 400), so the parent's error handler resolves a first page whose `count` is 10,000 or more to `SPLIT_REQUEST_WINDOW` (`>=` because Zendesk does not document whether `count` is capped) and the retriever's `request_window_splitting` halves the window, down to about 84 seconds after the CDK's ten split levels, before failing; the window size is a manifest constant. `update_timestamp` is not in Zendesk's list of documented searchable fields; it filters correctly today (verified live: server-side, inclusive bounds at one-second precision), but an unknown field returns HTTP 200 with `count: 0`, so if Zendesk ever drops it the stream silently syncs nothing while the sync stays green. The per-sync request budget is one search per day in the window plus one per additional page of 40 results, plus one List Chats request per 50 ids; an idle account still pays one search per day since its last chat because the state follows record values rather than window ends.

**Why this matters:** Changing the search field, the cursor field, the window size or the group size changes which chats are re-read and how many requests a sync makes. Filtering the child by its cursor (`is_client_side_incremental`) would drop updated chats whose `timestamp` is older than the state. Removing the state migration or renaming `chats_search` breaks the resume for every connection upgraded from 1.x. Do not switch the parent to `timestamp` windows without a lookback that covers late updates, and do not raise the window above a day without checking the 10,000-result cap.

### 2. `agent_timeline` still reads an incremental export and maps 403 to a configuration error

`agent_timeline` has no replacement endpoint in the Chats API, so it keeps calling `incremental/agent_timeline`. Zendesk did not list agent timelines in the shutdown announcement, so whether that export keeps working after 2026-12-02 is unknown. The stream uses a dedicated error handler (`definitions.incremental_export_error_handler`) that turns an HTTP 403 into a `config_error` naming the stream and pointing to the 60-day partner extension in Zendesk Admin Center; the export is also limited to the Owner and Administrator roles, so the message mentions the role as the other cause. The 403 mapping must stay limited to `incremental/` paths because other endpoints return 403 for ordinary permission problems.

**Why this matters:** Reusing the shared `error_handler` for this stream would surface the shutdown as a generic failure, and applying the incremental-export handler to other streams would mislabel permission errors. If Zendesk later confirms a replacement for agent timelines, move the stream off the export and delete the dedicated handler.
