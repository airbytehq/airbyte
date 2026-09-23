# Monday Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 3.0.0

Monday.com is moving its OAuth flow to OAuth 2.1 and stops accepting legacy OAuth access tokens on **October 1, 2026**. See the [monday.com announcement](https://developer-community.monday.com/product-updates/oauth-2-1-is-now-open-for-all-monday-developers-5326) and the [monday.com migration guide](https://developer.monday.com/apps/docs/migrating-to-the-new-oauth-flow).

Version 3.0.0 authenticates through the new token endpoint (`https://auth.monday.com/oauth_ms/oauth/token`) with PKCE and keeps the access token fresh with rotating refresh tokens. The connector configuration now stores a `refresh_token` alongside the `access_token`, and the connector refreshes the access token automatically, persisting the newest refresh token after every refresh.

### Who is affected

Only sources that use the **OAuth2.0** authorization method. Sources that use a **Personal API Token** require no action.

### Migration steps

1. Upgrade the connector to version 3.0.0 **before October 1, 2026**.
2. Run the connection test or a sync. On its first run, the connector exchanges the existing legacy access token for a new access token and refresh token through Monday.com's [token migration endpoint](https://developer.monday.com/apps/docs/migrating-to-the-new-oauth-flow#6-migrate-legacy-api-tokens) and stores them in the source configuration. No re-authentication is needed when this succeeds.
3. If the run fails with an error asking you to re-authenticate, open the source in Airbyte and click **Authenticate your Monday account**. This issues a new access token and refresh token through the new endpoint. If the Airbyte app is not installed on your Monday.com account (for example because it was removed), Monday.com asks an account admin to install it before showing the consent screen, so have an admin run this step.

The automatic migration is best-effort and only works while the legacy access token is still valid, so upgrade and run the source before October 1, 2026. Monday.com describes the migration endpoint as temporary and rate limited; when it rejects the token (expired or revoked token, Airbyte app removed from the account, migration disabled) the source needs the manual re-authentication from step 3. Re-authenticating on a version earlier than 3.0.0 still uses the legacy flow and issues a token that stops working on October 1, 2026. On October 1, 2026 sources still on an earlier version are upgraded automatically, and OAuth2.0 configurations whose legacy token was not migrated stop syncing until re-authenticated.

## Upgrading to 2.0.0

Source Monday has deprecated API version 2023-07. We have upgraded the connector to the latest API version 2024-01. In this new version, the Id field has changed from an integer to a string in the streams Boards, Items, Tags, Teams, Updates, Users and Workspaces. Please reset affected streams.

## Connector upgrade guide

<MigrationGuide />