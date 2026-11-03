# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** - Calls and contacts read date windows with separate settings; calls split a window that still holds too many records, contacts fail with a config error, conversations restart from the last timestamp after 10,000 records.
2. **Cursor choices account for creation-date filters and edits** - Streams use different sync strategies because Aircall filters by creation date, while records may be edited later. Numbers and teams are full refresh only since 1.0.0. Conversations are incremental on `last_engagement_at`, which closes and assignments do not move; their engagements follow the parent's incremental read, three-day lookback included.
3. **Calls start within Aircall's six-month retention period** - A first sync or full refresh of calls starts 186 days back because older history is unavailable; incremental syncs start three days before the saved cursor.
4. **Rate limits are shared across the company** - All workers share one budget of 100 requests per minute, below Aircall's company-wide limit of 120.
5. **HTTP errors have distinct recovery behavior** - Credential errors and the contacts result limit need configuration changes; rate limits and server errors follow retry behavior.
6. **Pagination differs by endpoint** - Most v1 endpoints start with an omitted page parameter and continue at page 2; campaigns and campaign outcomes follow `meta.next_cursor`, and WhatsApp templates follow `pageInfo.nextToken` per number.
7. **Add-on endpoints are gated by a 403 with a specific body** - Requests to conversations, trackers and WhatsApp templates are ignored only on Aircall's gating text; a plain 403 still fails as a credential error.
8. **Primary keys follow Aircall's documented identifiers** - `webhooks` uses `webhook_id` rather than the legacy `id`, and `company` stays keyless because Aircall returns one company object with no identifier.
9. **Ids and epoch times stay `number`** - The reference calls them integers, but every value fits in `number` and changing a declared type is breaking, so 1.0.0 only changes the fields whose declared type misrepresented the value: objects stored as text, the integer `priority`, and ISO timestamps declared as plain strings.
10. **Two authentication modes; OAuth needs a Technology Partner app** - OAuth 2.0 is the default and sends the non-expiring access token as a bearer token; the API key pair is the second option, and configs saved before 1.1.0 migrate to it automatically. With OAuth, `webhooks` returns only the webhooks created with Airbyte's token.

## Authentication and the Aircall partner app

Aircall issues OAuth client credentials only to apps in its Technology Partner programme. Airbyte's partner app and the Cloud OAuth provisioning of its `client_id` and `client_secret` are tracked in [airbytehq/airbyte-internal-issues#18380](https://github.com/airbytehq/airbyte-internal-issues/issues/18380). Self-managed deployments need their own partner app for OAuth, or use the API key option.

| Mode                | `credentials.auth_type` | Request authentication                   |
| :------------------ | :---------------------- | :--------------------------------------- |
| OAuth 2.0 (default) | `oauth2.0`              | `Authorization: Bearer <access_token>`   |
| API Key             | `api_key`               | HTTP Basic with `api_id` and `api_token` |

Mock-server tests use the post-migration `credentials` shape. `unit_tests/test_authentication.py` covers both modes and the migration of top-level `api_id` and `api_token` configs.

## Testing

`unit_tests/` holds mock-server tests that need no Aircall account. The acceptance tests read the CI secret `SECRET_SOURCE-AIRCALL__CREDS`.
