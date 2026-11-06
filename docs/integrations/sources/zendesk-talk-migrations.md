# Zendesk Talk Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 3.0.0

:::danger Risk of permanent data loss
Turn off the `calls` and `call_legs` streams in every connection that syncs them before you upgrade. If a sync runs on version 3.0.0 while the two streams are still selected, the destination can replace their tables with empty ones in overwrite modes, and Zendesk can't provide that call history again.
:::

Version 3.0.0 removes the `calls` and `call_legs` streams. No other stream changes.

### What changed

Zendesk is [ending access to its Incremental APIs for third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498-Announcing-end-of-availability-of-Incremental-APIs-for-third-party-developers), including the Talk incremental call export (`/stats/incremental/calls`) and call-leg export (`/stats/incremental/legs`) that the `calls` and `call_legs` streams read from. Zendesk [names no alternative endpoint](https://developer.zendesk.com/documentation/marketplace/building-a-marketplace-app/incremental-third-party/) for either path and confirmed to Airbyte that there is none. Enforcement starts on December 2, 2026 and completes on January 19, 2027, with a pause from December 17, 2026 to January 4, 2027. Once Zendesk blocks the integration's requests, syncs on version 2.x that include the two streams fail, while the connection test keeps passing because it reads a different endpoint. Zendesk also deactivates all API tokens on April 30, 2027, so version 2.x has no supported way to sync them.

The `start_date` field stays in the connector configuration, now optional, so existing sources keep validating, but no remaining stream uses it.

### Who is affected

Sources with at least one connection, including paused connections, that selects `calls` or `call_legs`. Airbyte keeps such a source on version 2.x until you upgrade it, and on Airbyte Cloud disables every connection on that source after December 2, 2026 until the upgrade. On Airbyte Cloud, sources whose connections never select the two streams are upgraded automatically and need no action. The other streams (`account_overview`, `addresses`, `agents_activity`, `agents_overview`, `current_queue_activity`, `greeting_categories`, `greetings`, `ivr_menus`, `ivr_routes`, `ivrs`, `phone_numbers`) are unchanged.

### Upgrade steps

1. In every connection on the source that selects `calls` or `call_legs`, including paused connections, turn the two streams off in the stream selection and save. Do this before upgrading: a sync on version 3.0.0 that still lists the two streams can replace their destination tables with empty ones in overwrite modes, and Zendesk can't provide that call history again.
2. Upgrade the Zendesk Talk source to version 3.0.0 (see [Update the connector version](#update-the-connector-version) at the end of this page; the clear step described there doesn't apply to this upgrade). On self-managed Airbyte, first update the connector definition to 3.0.0 (see [Self-managed plans: update the local connector image](#self-managed-plans-update-the-local-connector-image)).
3. Refresh the source schema for each connection and save, so the two streams leave the catalog.
4. If Airbyte disabled a connection on this source, turn it back on.
5. Keep syncing. No stream needs to be cleared or re-synced: the remaining streams are unchanged, and the call history already written by `calls` and `call_legs` stays in your destination tables. Don't clear or delete those tables unless you no longer need the history.

On Airbyte Cloud, every connection on a source kept on 2.x by this change is disabled after December 2, 2026 until the source is upgraded. On self-managed Airbyte the upgrade is opt-in, but version 2.x has no supported way to keep syncing the two streams. Zendesk's announcement also offers a 60-day extension that a Zendesk admin can request in Admin Center under **Apps & integrations > APIs > API Configuration**; it doesn't help in Airbyte, because version 3.0.0 no longer has the streams and Cloud disables the 2.x connections after December 2, 2026, so don't rely on it.

### Update downstream queries

Models, dashboards and exports that read the `calls` or `call_legs` tables keep working on the data already synced, but the tables stop receiving new rows. Point anything that needs ongoing call history at another data source, such as Zendesk's own Talk reporting.

## Upgrading to 2.0.0

This version adds OAuth2.0 with refresh token support. Users who authenticate via OAuth must re-authenticate to use the new flow with rotating refresh tokens.

### What changed

The OAuth authentication flow has been updated to support Zendesk's new grant-type tokens with rotating refresh tokens. The legacy OAuth2.0 option has been renamed to "OAuth2.0 (Legacy)" and a new "OAuth2.0" option with refresh token support has been added.

### Migration steps

1. Go to your Zendesk Talk connection settings in Airbyte
2. If you are using OAuth authentication, you will need to re-authenticate
3. Select "OAuth2.0" as the authentication method
4. Complete the OAuth flow to authorize the connector

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source zendesk-talk from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. This change will affect the `calls` and `call_legs` streams.

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

## Connector upgrade guide

<MigrationGuide />
