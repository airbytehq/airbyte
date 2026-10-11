# Strava Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 0.4.0

### What changed and why

Airbyte now stores the latest OAuth refresh token, a secret access token, and its expiry in the source configuration. Previously, rotated refresh tokens were discarded and the absolute `expires_at` timestamp was interpreted as a duration. The new optional, hidden `access_token` and `token_expiry_date` fields are managed automatically; do not populate them manually.

The connection check now validates access to both athlete stats and activities. Previously, setup could succeed without the activity permission needed to sync activities.

### Who is affected

All Strava sources use the updated credential configuration. Sources whose tokens lack `activity:read_all` will now fail setup instead of failing later during a sync. Existing valid credentials remain usable. Stream schemas and incremental state are unchanged; no stream reset is required.

Upgrade by October 21, 2026. Remaining sources will be automatically upgraded after that deadline.

### Upgrade steps

1. Upgrade the connector to version 0.4.0.
2. Ensure the Strava developer application is active. If Strava reports `Application` / `Status` / `Inactive`, restore its access before retrying.
3. If the athlete has not granted `activity:read_all`, reauthorize the application with that scope and update the source credentials. Refreshing a token cannot add permissions.
4. Use the latest refresh token if tokens have been exchanged outside Airbyte. Older tokens may have been invalidated by rotation.
5. Run the source connection check, then resume syncing. Airbyte manages subsequent token refreshes automatically.

## Connector upgrade guide

<MigrationGuide />
