# Zendesk Support Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 5.2.0

This is not a breaking change. No stream reset is required, and existing state is migrated automatically. This guide is provided because the behavioral change to the `tickets` stream may affect downstream pipelines that depend on deleted ticket data.

Version 5.2.0 switches the `tickets` stream from the Zendesk Incremental Export API to the [Export Search Results](https://developer.zendesk.com/api-reference/ticketing/ticket-management/search/#export-search-results) endpoint. This improves sync performance by enabling concurrent time-range partitioning.

### What changed

- The `tickets` stream no longer returns deleted tickets. Zendesk's Export Search Results endpoint excludes deleted tickets from the search index.
- A new `deleted_tickets` stream is available. This stream uses the [List Deleted Tickets](https://developer.zendesk.com/api-reference/ticketing/tickets/deleted_tickets/#list-deleted-tickets) endpoint and syncs in full refresh mode.
- The cursor field for the `tickets` stream changed from `generated_timestamp` to `updated_at`. Existing state is migrated automatically.

### Who is affected

Users who rely on the `tickets` stream to identify deleted tickets by filtering for `status`==`deleted` records. After upgrading, deleted tickets no longer appear in the `tickets` stream.

### Migration steps

1. Enable the `deleted_tickets` stream in your connection to continue syncing deleted ticket data.
2. Update any downstream pipelines that filter for `status`==`deleted` in the `tickets` stream to read from the `deleted_tickets` stream instead.
3. No stream reset is required. The connector automatically migrates existing state from the old cursor format to the new one.

:::note
The `deleted_tickets` stream requires the `view_deleted_tickets` permission in Zendesk. If your account lacks this permission, the stream is automatically skipped without failing the sync.
:::

## Upgrading to 5.0.0

This version adds OAuth2.0 with refresh token support. Users who authenticate via OAuth must re-authenticate to use the new flow with rotating refresh tokens.

### What changed

The OAuth authentication flow has been updated to support Zendesk's new grant-type tokens with rotating refresh tokens. The legacy OAuth2.0 option has been renamed to "OAuth2.0 (Legacy)" and a new "OAuth2.0 with Refresh Token" option has been added.

### Why this change is required

Zendesk announced support for OAuth refresh token grant type on April 30, 2025. According to [Zendesk's announcement](https://support.zendesk.com/hc/en-us/articles/9182123625370-Announcing-support-for-OAuth-refresh-token-grant-type-and-OAuth-access-and-refresh-token-expirations), all customers are required to adopt the OAuth refresh token flow by April 30, 2026. This connector update ensures compatibility with Zendesk's new authentication requirements.

### Migration steps

1. Go to your Zendesk Support connection settings in Airbyte
2. If you are using OAuth authentication, you will need to re-authenticate
3. Select "OAuth2.0 with Refresh Token" as the authentication method
4. Complete the OAuth flow to authorize the connector

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
