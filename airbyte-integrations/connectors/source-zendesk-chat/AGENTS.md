> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-zendesk-chat

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Zendesk Chat (Zopim) API supports incremental exports for high-volume endpoints (chats, agents, bans, agent_timeline) via the Incremental API. The connector already uses these for incremental streams. The remaining FR parent streams are config-style lookups (accounts, departments, goals, roles, routing_settings, shortcuts, skills, triggers) that do not support date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Singleton account config |
| agent_timeline | medium | top-level parent | start_time | start_time | incremental |  |
| agents | medium | top-level parent | id | id | incremental |  |
| bans | medium | top-level parent | id | id | incremental |  |
| chats | medium | top-level parent | update_timestamp | update_timestamp | incremental |  |
| departments | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| goals | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| roles | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| routing_settings | small | top-level parent | none | none | deferred_no_api_support | Singleton config endpoint |
| shortcuts | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| skills | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| triggers | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |

### Future incremental stream candidates

- **No API date filter (8 streams):** `accounts`, `departments`, `goals`, `roles`, `routing_settings`, `shortcuts`, `skills`, `triggers` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
