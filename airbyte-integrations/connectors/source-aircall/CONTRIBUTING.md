# Contributing to source-aircall

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **The 10,000-result cap requires date windows** - Calls and contacts read date windows with separate settings; calls split a window that still holds too many records, contacts fail with a config error, conversations restart from the last timestamp after 10,000 records.
2. **Cursor choices account for creation-date filters and edits** - Streams use different sync strategies because Aircall filters by creation date, while records may be edited later. Numbers and teams are full refresh only since 1.0.0. Contacts do not sort by `updated_at` because only the creation-date windows keep a read under the 10,000-result cap; campaigns, campaign outcomes, trackers, webhooks, WhatsApp and SMS templates and user numbers stay full refresh because their endpoints have no update filter and the lists are small. Conversations are incremental on `last_engagement_at`, which closes and assignments do not move; their engagements follow the parent's incremental read, three-day lookback included.
3. **Calls start a year back to cover Aircall's call history** - A first sync or full refresh starts 365 days back, covering the six months Aircall keeps; incremental syncs start three days before the saved cursor.
4. **Rate limits are shared across the company** - All workers share one budget of 100 requests per minute, below Aircall's company-wide limit of 120.
5. **HTTP errors have distinct recovery behavior** - Credential errors and the contacts result limit need configuration changes; rate limits and server errors follow retry behavior. Any other status falls back to the CDK default mapping (for example 404 and 405 fail as system errors, 408 and unmapped codes are retried).
6. **Pagination differs by endpoint** - Most v1 endpoints start with an omitted page parameter and continue at page 2; campaigns and campaign outcomes follow `meta.next_cursor`, and WhatsApp templates follow `pageInfo.nextToken` per number.
7. **Add-on endpoints are gated by a 403 with a specific body** - Requests to conversations, trackers and WhatsApp templates are ignored only on Aircall's gating text; a plain 403 still fails as a credential error, except on the conversation intelligence streams (see 10).
8. **Primary keys follow Aircall's documented identifiers** - `webhooks` uses `webhook_id` rather than the legacy `id`, and `company` stays keyless because Aircall returns one company object with no identifier.
9. **Ids and epoch times stay `number`** - The reference calls them integers, but every value fits in `number` and changing a declared type is breaking, so 1.0.0 only changes the fields whose declared type misrepresented the value: objects stored as text, the integer `priority`, and ISO timestamps declared as plain strings. `campaigns.calling_hours` slot `from_time` and `to_time` stay plain strings because Aircall sends 24-hour `HH:MM` without seconds, which no Airbyte time type accepts.
10. **Conversation intelligence is opt-in and costs one request per call** - The six AI streams exist only when `include_conversation_intelligence` is on. A 403 fails as a configuration error that names the AI Assist package and says to deselect the stream or turn the option off and refresh the schema (playbook results name AI Assist Pro), unless it is the gateway body of an invalid API key or OAuth token; a 404 with Aircall's `NotFound` body (no result for that call) is skipped, and any other 404 fails.
11. **Conversation intelligence fans out over the calls read** - Each AI stream follows the calls stream's incremental window and makes one request per call, keyed by `call_started_at`, so every selected stream adds about one request per call re-read on every sync, and all of them share one rate-limit budget.
12. **Two authentication modes; OAuth needs a Technology Partner app** - OAuth 2.0 is the default and sends the non-expiring access token as a bearer token; the API key pair is the second option, and configs saved before 1.2.0 migrate to it automatically. With OAuth, `webhooks` returns only the webhooks created with Airbyte's token.

## Authentication and the Aircall partner app

Aircall issues OAuth client credentials only to apps in its Technology Partner programme. Airbyte's partner app and the Cloud OAuth provisioning of its `client_id` and `client_secret` are tracked in [airbytehq/airbyte-internal-issues#18380](https://github.com/airbytehq/airbyte-internal-issues/issues/18380). Self-managed deployments need their own partner app for OAuth, or use the API key option.

| Mode                | `credentials.auth_type` | Request authentication                   |
| :------------------ | :---------------------- | :--------------------------------------- |
| OAuth 2.0 (default) | `oauth2.0`              | `Authorization: Bearer <access_token>`   |
| API Key             | `api_key`               | HTTP Basic with `api_id` and `api_token` |

Mock-server tests use the post-migration `credentials` shape. `unit_tests/test_authentication.py` covers both modes and the migration of top-level `api_id` and `api_token` configs.

## Testing

`unit_tests/` holds mock-server tests that need no Aircall account. The acceptance tests read the CI secret `SECRET_SOURCE-AIRCALL__CREDS`.
