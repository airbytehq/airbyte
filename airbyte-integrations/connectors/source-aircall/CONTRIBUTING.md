# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** — Calls and contacts use configurable date windows to stay under Aircall's per-request result limit.
2. **Cursor choices account for creation-date filters and edits** — Streams use different sync strategies because Aircall filters by creation date, while records may be edited later.
3. **Calls start within Aircall's six-month retention period** — Calls always start 186 days before the sync because older call history is unavailable.
4. **Rate limits are shared across the company** — All workers share Aircall's company-wide limit of 120 requests per minute.
5. **HTTP errors have distinct recovery behavior** — Credential and result-limit errors need configuration changes; rate limits and server errors follow retry behavior.
6. **V1 page numbering starts at one** — V1 pagination starts with an omitted page parameter and continues at page 2.
7. **Two authentication modes; OAuth needs Airbyte's partner app** — OAuth 2.0 is the default and sends the non-expiring access token as a bearer token; the API key pair is the second option, and older top-level API key configs migrate automatically.

## Testing

The GSM test key is revoked. Connector behavior is covered by mock-server tests in `unit_tests/`; do not make live Aircall API calls.

## Authentication and the Aircall partner app

Aircall issues OAuth client credentials only to apps in its Technology Partner programme. Airbyte owns the partner app; the APIs team (`team/apis`) owns its registration ([airbytehq/airbyte-internal-issues#18380](https://github.com/airbytehq/airbyte-internal-issues/issues/18380)) and the Cloud OAuth provisioning of its `client_id` and `client_secret`. Until Aircall approves the app, OAuth cannot be tested live, and Cloud users authenticate with the API key option.

| Mode | `credentials.auth_type` | Request authentication |
| :--- | :--- | :--- |
| OAuth 2.0 (default) | `oauth2.0` | `Authorization: Bearer <access_token>` |
| API Key | `api_key` | HTTP Basic with `api_id` and `api_token` |

Mock-server tests use the post-migration `credentials` shape. `unit_tests/test_authentication.py` covers both modes and the migration of top-level `api_id`/`api_token` configs.
