# Zendesk Support Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 6.0.0

Zendesk is ending third-party access to its [Incremental Export APIs](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/). Per Zendesk's [announcement](https://support.zendesk.com/hc/en-us/articles/11275429993498) and [developer guide](https://developer.zendesk.com/documentation/marketplace/building-a-marketplace-app/incremental-third-party/), integrations such as Airbyte stop receiving data from these endpoints between **2026-12-02** and **2027-01-19**, after which Zendesk answers their requests with `403 Forbidden`. Versions before 6.0.0 read `tickets`, `users`, `organizations`, `articles`, `ticket_comments`, `ticket_events` and `ticket_metric_events` from those endpoints, so they fail on these streams once Zendesk enforces the change on your account. Upgrade before 2026-12-02. If you need more time, a Zendesk administrator can request a one-time 60-day extension for Airbyte in Zendesk Admin Center under **Apps and integrations > APIs > API Configuration**, available from November 2026.

No reset is required and the saved state is migrated automatically. Existing rows in your destination are not changed. Read the rest of this section to learn which records and fields change.

### What changed

| Stream | Before 6.0.0 | 6.0.0 |
| :--- | :--- | :--- |
| `tickets` | Incremental Ticket Export, cursor `generated_timestamp` | [List Tickets](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#list-tickets) sorted by `updated_at`, cursor `updated_at` |
| `users` | Incremental User Export | [List Users](https://developer.zendesk.com/api-reference/ticketing/users/users/#list-users) sorted by `updated_at` |
| `user_identities` | Identities of each exported user | Identities of each listed user, read with the user |
| `organizations` | Incremental Organization Export | [List Organizations](https://developer.zendesk.com/api-reference/ticketing/organizations/organizations/#list-organizations) sorted by `updated_at` |
| `articles` | Incremental Article Export | [List Articles](https://developer.zendesk.com/api-reference/help_center/help-center-api/articles/#list-articles) sorted by `updated_at` |
| `ticket_comments` | Comment events from the Incremental Ticket Event Export | Comment events from [List Audits for a Ticket](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/#list-audits-for-a-ticket), one request per ticket the `tickets` stream returns |
| `ticket_events` | Incremental Ticket Event Export | Audits from List Audits for a Ticket, one request per ticket |
| `ticket_metric_events` | Incremental Ticket Metric Events Export | [List Ticket Metric Events for a Ticket](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/), one request per ticket |
| `ticket_metrics`, `side_conversations`, `ticket_audits_per_ticket` | One request per ticket from the Incremental Ticket Export | Unchanged requests, one per ticket the new `tickets` stream returns |

The cursor fields of `users`, `user_identities`, `organizations`, `articles`, `ticket_comments`, `ticket_events` and `ticket_metric_events` do not change. The `tickets` cursor changes from `generated_timestamp` to `updated_at`. The connector converts the saved `generated_timestamp` value into an `updated_at` value one hour earlier, and the per-ticket streams carry the same converted value for their parent, so the first sync after upgrading continues where the previous one stopped. `generated_timestamp` stays in the `tickets` records.

### Records that are no longer replicated

The list endpoints return less than the export endpoints did. The following records stop appearing in new syncs; rows already in your destination stay as they are.

- **Archived tickets.** Zendesk [archives](https://support.zendesk.com/hc/en-us/articles/4408887617050-About-ticket-archiving) closed tickets after about 120 days and leaves them out of the ticket list. `tickets` no longer returns them, and `ticket_comments`, `ticket_events`, `ticket_metric_events`, `ticket_metrics`, `side_conversations` and `ticket_audits_per_ticket` no longer visit them, including after a bulk update that changes an archived ticket. The opt-in `tickets_search` stream reads Zendesk's search index, which includes archived tickets. See [Tickets stream: change tracking](zendesk-support.md#tickets-stream-change-tracking) for its limitations.
- **Deleted tickets.** Versions 5.5.0 to 5.7.0 included deleted tickets in `tickets` with `status` `deleted`. The ticket list does not return deleted tickets. Enable the `deleted_tickets` stream to keep replicating them.
- **Deleted users and organizations.** The user and organization lists do not return deleted records, so `users` no longer returns permanently deleted users (the `permanently_deleted` field is no longer populated) and `organizations` no longer returns deleted organizations (`deleted_at` is no longer populated).
- **Ticket metric events without a ticket.** The export occasionally returned metric events whose `ticket_id` was null. These are not reachable ticket by ticket.
- **Ticket metric events recorded without a ticket update.** `ticket_metric_events` reads a ticket's metric events when the ticket is created or updated. Zendesk records some metric events on its own clock, for example SLA `breach` events and `pausable_update_time` or `periodic_update_time` events. If such an event doesn't change the ticket's `updated_at`, it's read on the next sync in which the ticket changes for another reason, instead of by the event's own time as the export did.
- **Updates that change only `generated_timestamp`.** The ticket list is sorted and filtered by `updated_at`, which Zendesk bumps only for changes that generate a ticket event. An automation-, macro- or system-driven update that changes only `generated_timestamp` is not picked up by incremental syncs of `tickets` and the per-ticket streams. Version 5.5.0 moved `tickets` to `generated_timestamp` to catch these updates; the endpoint that made that possible is the one Zendesk is retiring.

### Field changes in `ticket_events`

`ticket_events` records now come from ticket audits. Each record keeps the fields it had (`id`, `ticket_id`, `timestamp`, `created_at`, `updater_id`, `via`, `system`, `child_events`, `event_type`) and gains `metadata`, the audit's metadata object. Three of the existing fields change their values:

- `via` holds the channel name from the Ticket Audits API instead of the label the export used. Update filters on this field with this mapping:

  | Before 6.0.0 | 6.0.0 |
  | :--- | :--- |
  | `Web form` | `web` |
  | `Closed Ticket` | `web` |
  | `Web service` | `api` |
  | `Mail` | `email` |
  | `Chat` | `chat` |
  | `Chat Transcript` | `chat_transcript` |
  | `Voicemail` | `voice` |
  | `Rule` | `rule` |
  | `Sample Ticket` | `sample_ticket` |

- `child_events` holds the audit's `events` array in the shape of the [Ticket Audits API](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/#audit-events): each child event has a `type` (for example `Create`, `Change`, `Comment`) and a `field_name` with a `value`, where the export used `event_type` and one key per changed field. Audits also include `Notification` and `AgentMacroReference` child events that the export left out.
- `updater_id` holds the audit's `author_id`, which is `-1` for changes Zendesk made itself (for example notifications sent by triggers). The export attributed some of these audits to the user whose action triggered them.

`ticket_comments` records keep their shape, including `via_reference_id`, which stays null as before.

### Sync cost of the per-ticket streams

`ticket_comments`, `ticket_events` and `ticket_metric_events` now make one request for every ticket created or updated since the previous sync, as `ticket_metrics` and `side_conversations` already did, against your plan's account-wide rate limit. On accounts with heavy ticket traffic these syncs take longer than before and share the limit with your other Zendesk integrations. A ticket that changes re-emits all of its comments, audits and metric events; sync these streams with a deduplicated sync mode to keep one row per `id`.

The `tickets` stream itself reads 100 tickets per request at up to 100 requests per minute. A new connection, or a cleared `tickets` stream, on a large account reads its whole history at that pace before incremental syncs become short again.

### Migration steps

1. Upgrade the connector before 2026-12-02. The first sync continues from the migrated state; no reset is required.
2. If you rely on deleted tickets from the `tickets` stream, enable the `deleted_tickets` stream. If you rely on archived tickets, enable `tickets_search`.
3. Update downstream queries, models and dashboards that read `ticket_events.via`, `ticket_events.child_events` or `ticket_events.updater_id` using the mappings above, and ones that read `users.permanently_deleted` or `organizations.deleted_at`.
4. If `ticket_comments`, `ticket_events` or `ticket_metric_events` are synced without deduplication, switch them to a deduplicated sync mode or deduplicate on `id` downstream.

## Upgrading to 5.5.0

This is not a breaking change. No stream reset is required, and existing state is migrated automatically. This guide is provided because the behavioral change to the `tickets` stream affects which records are synced.

Version 5.5.0 reverts the `tickets` stream to Zendesk's [Incremental Ticket Export](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based) endpoint and changes its cursor field back from `updated_at` to `generated_timestamp`.

### Why

The 5.2.0 switch to the [Export Search Results](https://developer.zendesk.com/api-reference/ticketing/ticket-management/search/#export-search-results) endpoint filtered and checkpointed the `tickets` stream on `updated_at`. Per Zendesk's [incremental export docs](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based), `updated_at` is only bumped when an update generates a ticket event, whereas `generated_timestamp` is bumped for **every** ticket change including system updates. Automation-, macro-, and system-driven ticket updates (e.g. auto-solve batches) generate no ticket event, so they left `updated_at` unchanged and were silently dropped from incremental syncs.

This also affected full/historical reads. The Export Search Results endpoint is served from Zendesk's search index, which [Zendesk documents as non-real-time](https://developer.zendesk.com/api-reference/ticketing/ticket-management/search/) ("It can take up to a few minutes for new tickets, users, and other resources to be indexed for search") and recommends against for data export. In practice, tickets whose most recent change generated no ticket event were not re-indexed, so `search/export` returned **stale field values** (e.g. `status = new` for tickets that were actually solved) — even on a from-scratch backfill. `generated_timestamp` on the Incremental Ticket Export endpoint avoids both problems: it reads the live ticket record and advances on every change.

### What changed

- The `tickets` stream again uses `generated_timestamp` and re-includes deleted tickets (as it did before 5.2.0). It reads the live ticket record, so statuses are accurate (no search-index staleness).
- A one-time state migration runs automatically on upgrade. It converts existing `updated_at`-based state back to `generated_timestamp` and clamps the cursor to **2026-03-01T00:00:00Z** (just before 5.2.0 shipped), so the first sync after upgrading re-reads every ticket changed during the regression window and rewrites their current values. No manual stream reset is required.
- `ticket_metrics` and `side_conversations` depend on the `tickets` stream and are re-synced accordingly.
- The fast Export Search Results behavior is preserved as a new **opt-in `tickets_search` stream**. It has a configurable `Tickets Search Lookback Window (days)` setting. ⚠️ `tickets_search` can miss automation/macro/system-driven updates in incremental mode (same limitation as 5.2.0–5.4.x `tickets`); use the default `tickets` stream when completeness matters. Because Export Search excludes deleted tickets, pair `tickets_search` with the `deleted_tickets` stream.

### Who is affected

All users of the `tickets`, `ticket_metrics`, and `side_conversations` streams.

The state migration also rewrites the `tickets` parent state carried inside `ticket_metrics` and `side_conversations`, so all three streams backfill on the first sync after upgrading. That sync is substantially heavier than a normal incremental run: `tickets` re-reads from the Incremental Ticket Export endpoint, which Zendesk rate limits to 10 requests per minute regardless of plan tier, and `ticket_metrics` and `side_conversations` each make one additional API request per re-read ticket. Expect it to run considerably longer than usual; later syncs return to normal volume. Progress is checkpointed, so an interrupted first sync continues from the last committed cursor rather than restarting the backfill.

### Migration steps

1. Upgrade the connector. The first sync automatically backfills records changed since 2026-03-01 via the state migration — no reset required. Allow extra time for it (see [Who is affected](#who-is-affected)).
2. If you specifically want the faster (but potentially lossy) sync behavior, enable the new `tickets_search` stream and keep `deleted_tickets` enabled alongside it.

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

## Upgrading to 4.0.0

The pagination strategy has been changed from `Offset` to `Cursor-Based`. It is necessary to reset the stream.

## Upgrading to 3.0.0

`cursor_field` for `TicketsMetric` stream is changed to `generated_timestamp`. It is necessary to refresh the data and schema for the affected stream.

### Schema Changes - Added Field

| Stream Name     | Added Fields          |
| --------------- | --------------------- |
| `TicketMetrics` | `generated_timestamp` |

## Upgrading to 2.0.0

Stream `Deleted Tickets` is removed. You may need to refresh the connection schema (skipping the data clearing), and running a sync. Alternatively, you can clear your data.

## Upgrading to 1.0.0

`cursor_field` for `Tickets` stream is changed to `generated_timestamp`.
For a smooth migration, you should refresh your stream. Alternatively, you can clear your data.

## Connector upgrade guide

<MigrationGuide />
