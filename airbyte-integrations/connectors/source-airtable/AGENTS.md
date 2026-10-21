> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-airtable: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Airtable's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Airtable cannot.

## 2. Short-Lived Access Tokens (60-Minute Expiry)

In addition to the single-use refresh tokens above, Airtable access tokens expire **60 minutes after they are issued** ([Airtable token expiry docs](https://airtable.com/developers/web/api/oauth-reference#token-expiry-refresh-tokens)). This means tokens are refreshed frequently, and the single-use rotation in section 1 happens on every refresh.

**Why this matters:** During long syncs or extended local testing sessions, expect a token refresh (and refresh-token rotation) roughly every hour. This makes the persistence concern in section 1 more likely to surface than for connectors whose access tokens live for days.

## 3. Incremental Sync via filterByFormula

Dynamic table streams use the synthetic `_airtable_extracted_at` cursor, stamped with the end time of the sync window because Airtable records do not include a last-modified timestamp. Incremental requests compare `LAST_MODIFIED_TIME()` with the cursor, falling back to `CREATED_TIME()` when Airtable leaves last-modified blank for never-edited records. The filter is omitted for full refreshes and the first incremental sync. This approach does not capture changes only to computed fields (formula, rollup, lookup, or count) or deleted records.
