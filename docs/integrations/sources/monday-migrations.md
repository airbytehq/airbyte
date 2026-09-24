# Monday Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.6.0

Monday.com is moving its OAuth flow to OAuth 2.1 and stops accepting legacy OAuth access tokens on **October 1, 2026**. See the [monday.com announcement](https://developer-community.monday.com/product-updates/oauth-2-1-is-now-open-for-all-monday-developers-5326) and the [monday.com migration guide](https://developer.monday.com/apps/docs/migrating-to-the-new-oauth-flow).

Version 2.6.0 authenticates through the new token endpoint (`https://auth.monday.com/oauth_ms/oauth/token`) with PKCE and keeps the access token fresh with rotating refresh tokens. The connector configuration stores a `refresh_token` alongside the `access_token`, and the connector refreshes the access token automatically, persisting the newest refresh token after every refresh. This is not a breaking change: existing configurations stay valid and are migrated automatically on the first run.

### Who is affected

Only sources that use the **OAuth2.0** authorization method. Sources that use a **Personal API Token** require no action.

### What happens on upgrade

1. On Airbyte Cloud the upgrade is applied automatically through a progressive rollout. On self-managed Airbyte, upgrade the connector to 2.6.0 **before October 1, 2026**.
2. On the first run on 2.6.0 (connection test or sync), the connector exchanges the existing legacy access token for a new access token and refresh token through Monday.com's [token migration endpoint](https://developer.monday.com/apps/docs/migrating-to-the-new-oauth-flow#6-migrate-legacy-api-tokens) and stores them in the source configuration. No re-authentication is needed when this succeeds.
3. If a run fails with an error asking you to re-authenticate, open the source in Airbyte and click **Authenticate your Monday account**. If the Airbyte app is not installed on your Monday.com account (for example because it was removed), Monday.com asks an account admin to install it before showing the consent screen, so have an account admin install the app first. If the admin completes the authorization, the source syncs with the admin's permissions.

The automatic migration only works while the legacy access token is still valid, so make sure the source runs once on 2.6.0 before October 1, 2026. Monday.com describes the migration endpoint as temporary and rate limited; when it rejects the token (expired or revoked token, Airbyte app removed from the account, migration disabled, or a personal API token stored in the OAuth2.0 settings) the source needs the manual re-authentication from step 3. Re-authenticating on a version earlier than 2.6.0 uses the legacy flow: it fails once the Airbyte app is switched to Monday.com's new OAuth flow, and any token it issues stops working on October 1, 2026. From that date, OAuth2.0 sources whose legacy token was not migrated stop syncing until they are re-authenticated.

## Upgrading to 2.0.0

Source Monday has deprecated API version 2023-07. We have upgraded the connector to the latest API version 2024-01. In this new version, the Id field has changed from an integer to a string in the streams Boards, Items, Tags, Teams, Updates, Users and Workspaces. Please reset affected streams.

## Connector upgrade guide

<MigrationGuide />