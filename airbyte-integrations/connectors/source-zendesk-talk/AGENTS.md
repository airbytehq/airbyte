> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-zendesk-talk: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Zendesk Talk's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Zendesk Talk cannot.

## Incremental Stream Considerations

The Zendesk Talk API supports incremental exports for high-volume call-related endpoints. The connector already uses `DatetimeBasedCursor` for `call_legs` and `calls` streams. The remaining FR parent streams are stats/overview endpoints and config lookups (addresses, greetings, IVR menus, etc.) that return aggregate data or small config sets without date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| account_overview | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; singleton aggregate |
| addresses | small | top-level parent | none | none | deferred_no_api_support | Config-style; phone addresses |
| agents_activity | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; snapshot data |
| agents_overview | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; aggregate snapshot |
| call_legs | medium | top-level parent | updated_at | updated_at | incremental |  |
| calls | medium | top-level parent | updated_at | updated_at | incremental |  |
| current_queue_activity | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; snapshot data |
| greeting_categories | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| greetings | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| ivr_menus | small | top-level parent | none | none | deferred_no_api_support | Config-style; IVR menu items |
| ivr_routes | small | top-level parent | none | none | deferred_no_api_support | Config-style; IVR routing rules |
| ivrs | small | top-level parent | none | none | deferred_no_api_support | Config-style; IVR trees |
| phone_numbers | small | top-level parent | none | none | deferred_no_api_support | Config-style; provisioned numbers |

### Future incremental stream candidates

- **No API date filter (11 streams):** `account_overview`, `addresses`, `agents_activity`, `agents_overview`, `current_queue_activity`, `greeting_categories`, `greetings`, `ivr_menus`, `ivr_routes`, `ivrs`, `phone_numbers` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
