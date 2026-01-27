# Zendesk Support Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 5.0.0

This version adds OAuth2.0 with refresh token support. Users who authenticate via OAuth must re-authenticate to use the new flow with rotating refresh tokens.

### What changed

Zendesk announced support for OAuth refresh token grant type starting April 30, 2025, with a requirement for all customers to adopt this flow by April 30, 2026. The connector has been updated to support this new authentication flow.

The OAuth authentication flow now uses rotating refresh tokens. When the connector refreshes an access token, Zendesk returns a new refresh token and invalidates the previous one. This provides enhanced security but requires the connector to properly handle token rotation.

The legacy OAuth2.0 option has been renamed to "OAuth2.0 (Legacy)" and a new "OAuth2.0 with Refresh Token" option has been added.

### Who is affected

This change affects users who authenticate via OAuth. Users who authenticate with API tokens are not affected.

### Migration steps

1. Go to your Zendesk Support connection settings in Airbyte.
2. If you are using OAuth authentication, you will need to re-authenticate.
3. Select "OAuth2.0 with Refresh Token" as the authentication method.
4. Complete the OAuth flow to authorize the connector.

For more information about Zendesk's OAuth changes, see [Zendesk's OAuth refresh token announcement](https://support.zendesk.com/hc/en-us/articles/9182123625370).

### Connector upgrade guide

<MigrationGuide />

## Upgrading to 4.0.0

The pagination strategy has been changed from `Offset` to `Cursor-Based`. It is necessary to reset the stream.

### Connector upgrade guide

<MigrationGuide />

## Upgrading to 3.0.0

`cursor_field` for `TicketsMetric` stream is changed to `generated_timestamp`. It is necessary to refresh the data and schema for the affected stream.

### Schema Changes - Added Field

| Stream Name        | Added Fields            |
| -------------------|------------------------ |
| `TicketMetrics`    | `generated_timestamp`   |

## Upgrading to 2.0.0

Stream `Deleted Tickets` is removed. You may need to refresh the connection schema (skipping the data clearing), and running a sync. Alternatively, you can clear your data.

## Upgrading to 1.0.0

`cursor_field` for `Tickets` stream is changed to `generated_timestamp`.
For a smooth migration, you should refresh your stream. Alternatively, you can clear your data.
