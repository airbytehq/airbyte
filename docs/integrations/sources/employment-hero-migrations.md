import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Employment Hero Migration Guide

## Upgrading to 0.1.0

### What changed

Version 0.1.0 replaces the single `API Key` field with the Employment Hero OAuth 2.0 refresh-token flow. The source configuration now takes:

| Field | Description |
| --- | --- |
| `client_id` | Client ID of your OAuth 2.0 application in the Employment Hero Developer Portal |
| `client_secret` | Client Secret of that application |
| `refresh_token` | Refresh token returned by the OAuth 2.0 authorization code (PKCE) flow |

Before every sync the connector exchanges the refresh token for a new access token at `https://oauth.employmenthero.com/oauth2/token`, so syncs no longer depend on a manually copied, short-lived token. Streams, schemas, primary keys and the `organization_configids` / `employees_configids` inputs are unchanged.

### Why

Employment Hero does not issue long-lived API keys. The `API Key` field accepted an OAuth *access token*, which [Employment Hero expires after 15 minutes](https://developer.employmenthero.com/api-references/authentication). As a result every connection failed with `Stream organisations is not available: Unauthorized` as soon as the pasted token expired, and the connector had no way to renew it. There is no automatic config migration because the expired access token cannot be converted into OAuth credentials.

### Who is affected

All users of this source. Every existing connection is already failing on the `check` step with an `Unauthorized` error, so there is no working configuration to preserve.

### Steps to migrate

1. Upgrade the source connector to 0.1.0.
2. In the Employment Hero Developer Portal, open (or create) your OAuth 2.0 application and copy its **Client ID** and **Client Secret**.
3. Run the OAuth 2.0 authorization code flow **with PKCE** (required by Employment Hero since 2026-09-30) and copy the `refresh_token` from the token response. The [Employment Hero source docs](https://docs.airbyte.com/integrations/sources/employment-hero#authentication-setup) describe how to do this with Postman.
4. Edit the Employment Hero source in Airbyte, fill in **Client ID**, **Client Secret** and **Refresh Token**, and click **Test and save**.
5. Run a sync. No schema refresh or stream reset is required: the streams and schemas are unchanged.

## Connector upgrade guide

<MigrationGuide />
