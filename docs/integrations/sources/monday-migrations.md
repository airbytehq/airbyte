# Monday Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 3.0.0

Monday.com is deprecating its legacy OAuth token endpoint (`https://auth.monday.com/oauth2/token`) and invalidating OAuth tokens issued through it. The connector now exchanges and refreshes tokens through the new endpoint (`https://auth.monday.com/oauth_ms/oauth/token`), which issues short-lived access tokens together with refresh tokens. The connector configuration now stores a `refresh_token` and `token_expiry_date` alongside the `access_token`, and the connector automatically refreshes the access token when it expires (persisting the newest refresh token on every refresh).

### Who is affected

Only sources using the **OAuth2.0** authorization method are affected. Sources using a **Personal API Token** require no action.

### Migration steps

1. Upgrade the connector to version 3.0.0.
2. Open the affected Monday source in Airbyte, and re-authenticate via **Authenticate your Monday account**. This obtains a new access token and refresh token from the new endpoint. Previously issued tokens are invalidated upstream by Monday.com, so re-authentication is required regardless of when you upgrade.
3. Save the source and verify the connection succeeds.

## Upgrading to 2.0.0

Source Monday has deprecated API version 2023-07. We have upgraded the connector to the latest API version 2024-01. In this new version, the Id field has changed from an integer to a string in the streams Boards, Items, Tags, Teams, Updates, Users and Workspaces. Please reset affected streams.

## Connector upgrade guide

<MigrationGuide />