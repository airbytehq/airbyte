# Monday Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 3.0.0

Monday.com is moving its OAuth flow to OAuth 2.1 and stops accepting legacy OAuth access tokens on **October 1, 2026**. See the [monday.com announcement](https://developer-community.monday.com/product-updates/oauth-2-1-is-now-open-for-all-monday-developers-5326) and the [monday.com migration guide](https://developer.monday.com/apps/docs/migrating-to-the-new-oauth-flow).

Version 3.0.0 authenticates through the new token endpoint (`https://auth.monday.com/oauth_ms/oauth/token`) with PKCE and keeps the access token fresh with rotating refresh tokens. The connector configuration now stores a `refresh_token` alongside the `access_token`, and the connector refreshes the access token automatically, persisting the newest refresh token after every refresh.

### Who is affected

Only sources that use the **OAuth2.0** authorization method. Sources that use a **Personal API Token** require no action.

### Migration steps

1. Upgrade the connector to version 3.0.0.
2. Open the affected Monday source in Airbyte and click **Authenticate your Monday account** to re-authenticate. This issues a new access token and refresh token through the new endpoint.
3. Save the source and verify the connection succeeds.

Complete these steps before October 1, 2026. After that date monday.com rejects the legacy access tokens, and syncs of sources that were not re-authenticated fail with an authentication error until they are.

## Upgrading to 2.0.0

Source Monday has deprecated API version 2023-07. We have upgraded the connector to the latest API version 2024-01. In this new version, the Id field has changed from an integer to a string in the streams Boards, Items, Tags, Teams, Updates, Users and Workspaces. Please reset affected streams.

## Connector upgrade guide

<MigrationGuide />