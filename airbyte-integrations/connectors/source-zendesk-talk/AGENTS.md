> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-zendesk-talk: Unique Behaviors

## 1. Single-Use Rotating Refresh Tokens

Zendesk Talk's OAuth implementation issues single-use refresh tokens. Every time an access token is refreshed, the old refresh token is invalidated and a new one is returned. The connector uses `refresh_token_updater` to persist the new refresh token back to the connection configuration after each token exchange.

**Why this matters:** If a token refresh succeeds but the new refresh token fails to persist (e.g., due to a crash or network issue between the exchange and the config update), the connection becomes permanently broken and requires re-authentication. Standard OAuth connectors can retry with the same refresh token, but Zendesk Talk cannot.

## 2. Zendesk Marketplace Headers Are Sent in Airbyte Cloud, and on the Authorization Code Exchange in Every Edition

Zendesk asks Marketplace integrations to send `X-Zendesk-Marketplace-Name`, `X-Zendesk-Marketplace-Organization-Id` and `X-Zendesk-Marketplace-App-Id` on [every request made from outside the Zendesk Apps framework](https://developer.zendesk.com/documentation/marketplace/building-a-marketplace-app/request-header-requirements-for-marketplace-apps/). In Airbyte Cloud the connector sends them on every data request and on the OAuth token refresh, for every authentication option. Self-managed deployments send none on the connector's own requests: they run with the customer's own OAuth client or API token. The platform's OAuth authorization code exchange does carry them in every edition, because the platform makes it from the spec (item 3).

How it is built, and why:

1. **The headers are declared once on the authenticator.** `marketplace_headers` on the `CustomAuthenticator` of `definitions.base_requester` holds the three headers. The IDs are quoted, because `requests` rejects a header value that is not a string.
2. **`ZendeskTalkAuthenticator` adds them in Airbyte Cloud only.** When `AIRBYTE_EDITION` is `CLOUD`, `send_headers_on_every_request` in `components.py` wraps `get_auth_header` and, on the OAuth authenticator, `get_refresh_request_headers` of the selected instance. A manifest cannot read the edition, which is why this is not plain `request_headers`.
3. **The authorization code exchange is made by the platform from the spec, so it sends the headers in every edition.** `advanced_auth.oauth_config_specification.oauth_connector_input_specification.access_token_headers` lists the three headers. A non-empty `access_token_headers` replaces the platform's default headers instead of adding to them, so it also repeats `Content-Type: application/x-www-form-urlencoded` and `Accept: application/json`. The spec is the same in every edition, so a self-managed deployment that authenticates from the setup form with its own OAuth client sends them on this one request too. `test_authorization_code_exchange_sends_the_headers_in_every_edition` pins the whole mapping.

**Why this matters:** every stream takes its requester from `#/definitions/base_requester`. A stream that sets its own `authenticator` next to the `$ref`, or a custom component that makes its own HTTP call, silently sends no Marketplace headers; `test_cloud_sends_the_headers_on_check_and_on_every_stream` fails in the first case. The IDs appear in `marketplace_headers` and in `access_token_headers`, both pinned by `unit_tests/test_marketplace_headers.py`; change them together.

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
