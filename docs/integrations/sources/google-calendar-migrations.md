# Google Calendar Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 reads `events` from every calendar in the account when **Calendar Id** is empty, and adds the `acl` and `freebusy` streams. Because one `events` stream can now hold events from several calendars, three things change for it:

- **Primary key.** The primary key changes from `id` to `[calendar_id, id]`. Google keeps event ids unique per calendar only, and a meeting has the same id on the organiser's calendar and on each invitee's calendar. With `id` alone, *Append + Deduped* would keep one of those rows and drop the others.
- **`calendar_id` values.** `calendar_id` now holds the calendar's real ID. Connections configured with the alias `primary` get the account's email address instead of the word `primary`, so the column joins to `calendarlist.id`.
- **State format.** The saved `events` cursor moves to a format that covers all calendars. A cursor saved by an earlier version is not carried over, and the first sync after the upgrade re-reads the calendar.

Connections that set **Calendar Id** keep syncing that one calendar. To sync every calendar, clear the field after upgrading.

The `acl` stream needs the `calendar.acls.readonly` OAuth scope. Re-authorize the connector to grant it, or leave `acl` deselected.

### Steps

1. Upgrade the connector to 1.0.0.
2. Refresh the source schema so the new primary key and streams are picked up, and save the connection.
3. Clear the `events` stream. Clearing removes the stream's data from the destination and re-syncs it, so rows written under the old primary key and the old `calendar_id` values are replaced.

For background on these operations, see [Schema changes](/platform/using-airbyte/schema-change-management) and [Clearing your data](/platform/operator-guides/clear).
