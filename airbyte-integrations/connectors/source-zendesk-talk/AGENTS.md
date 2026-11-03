> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-zendesk-talk: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Zendesk Talk's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Zendesk Talk cannot.

## 2. No Call History Streams (Zendesk Withdrew the Incremental Exports)

Until 2.x the connector had two incremental streams, `calls` (`/stats/incremental/calls`) and `call_legs` (`/stats/incremental/legs`), the only Talk endpoints that return call history. Zendesk is [ending access to its Incremental APIs for third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498-Announcing-end-of-availability-of-Incremental-APIs-for-third-party-developers) (rollout 2026-12-02, completion 2027-01-19), lists [no alternative endpoint](https://developer.zendesk.com/documentation/marketplace/building-a-marketplace-app/incremental-third-party/) for these two paths, and confirmed to Airbyte that none exists. Version 3.0.0 removed both streams. Every remaining stream is a full-refresh read of a stats snapshot or a configuration list, and `start_date` in the spec no longer filters anything; it is kept so existing configs stay valid.

**Why this matters:** do not re-add a stream on `/stats/incremental/*` or on any other path Zendesk lists as an Incremental API: requests from Airbyte's OAuth client get HTTP 403 once enforcement reaches the account, and `check` (which reads `account_overview`) keeps passing, so the failure only shows up in syncs. The `unit_tests/test_manifest.py` guard fails if such a path comes back.

## Incremental Stream Considerations

No remaining stream has an API-side date filter. The streams are stats/overview endpoints and config lookups (addresses, greetings, IVR menus, etc.) that return aggregate data or small config sets without date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| account_overview | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; singleton aggregate |
| addresses | small | top-level parent | none | none | deferred_no_api_support | Config-style; phone addresses |
| agents_activity | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; snapshot data |
| agents_overview | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; aggregate snapshot |
| current_queue_activity | small | top-level parent | none | none | deferred_no_api_support | Real-time stats endpoint; snapshot data |
| greeting_categories | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| greetings | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| ivr_menus | small | top-level parent | none | none | deferred_no_api_support | Config-style; IVR menu items |
| ivr_routes | small | top-level parent | none | none | deferred_no_api_support | Config-style; IVR routing rules |
| ivrs | small | top-level parent | none | none | deferred_no_api_support | Config-style; IVR trees |
| phone_numbers | small | top-level parent | none | none | deferred_no_api_support | Config-style; provisioned numbers |

### Future incremental stream candidates

- **No API date filter (11 streams):** `account_overview`, `addresses`, `agents_activity`, `agents_overview`, `current_queue_activity`, `greeting_categories`, `greetings`, `ivr_menus`, `ivr_routes`, `ivrs`, `phone_numbers` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
