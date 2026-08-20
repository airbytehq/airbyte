# Greenhouse migration guide

## Version 1.0.0

Version 1.0.0 migrates the connector from Greenhouse Harvest v1 to Harvest v3 because Greenhouse is sunsetting Harvest v1 and v2 together on 2026-08-31. This is a breaking release: refresh the source schema and reset affected streams after upgrading.

### Authentication

Harvest v3 uses OAuth 2.0 Authorization Code authentication and refresh tokens instead of Harvest API keys. In Airbyte Cloud, enter the OAuth client ID and client secret and click **Authenticate** to complete the consent flow. In self-managed Airbyte, use the consent flow to mint a refresh token and provide it with the client ID and client secret. Reauthentication is required after upgrading to 1.0.0.

### Stream and schema changes

All 36 streams now use their Harvest v3 collection endpoints. The v3 response schemas remove several nested v1 objects and add v3 identifiers, timestamps, and relationship fields. Examples include:

- `applications` uses `created_at` instead of `applied_at` and exposes flat job, stage, recruiter, coordinator, and source identifiers.
- `candidates` no longer embeds applications and uses `private`, `preferred_name`, `last_activity_at`, and linked user identifiers.
- `applications_interviews` uses flat schedule, organizer, and interview identifiers.
- `jobs_openings`, `offers`, and `users` use v3 relationship identifiers instead of the v1 nested objects.
- `offices.location` is a string in v3 rather than the v1 object.

The complete field-level comparison is reflected in the connector's v3 schemas. Refresh the schema in every destination and reset streams whose records or fields are used downstream.

### Pagination and incremental state

Harvest v3 returns opaque cursor URLs in the `Link` response header. The connector sends `per_page=500`, incremental filters, parent filters, and static filters only on the first request; cursor follow-up requests use only the cursor URL. Existing application state is migrated from `applied_at` to `created_at`, including partitioned application child-stream state.

### Rate limits

The connector uses Greenhouse's v3 rate-limit headers and a fixed 30-second budget. Existing connections may take longer or process fewer concurrent requests while the connector stays within the documented account limit.

Greenhouse refresh tokens expire after 24 hours of non-use and rotate on every refresh, so set every Greenhouse connection to sync more often than once a day. A connection left paused, disabled, or failing for more than 24 hours requires re-running the consent flow from the source settings.
