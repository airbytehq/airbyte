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

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **`chats` is a search-then-fetch substream, not a single endpoint read** -- Zendesk ends incremental exports for third-party integrations starting 2026-12-02 (rolled out through 2027-01-19, extendable by 60 days), so the stream now searches chats by last-update time one day at a time (splitting a day that hits Zendesk's 10,000-result search cap) and then fetches them in full 50 ids per request, dropping ids that no longer exist; the cursor changed to `timestamp` and old state is migrated automatically.
2. **`agent_timeline` still reads an incremental export and maps 403 to a configuration error** -- the stream has no replacement endpoint, so a 403 from Zendesk becomes a configuration error that points users to the 60-day partner extension.
