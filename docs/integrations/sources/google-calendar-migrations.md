import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Google Calendar Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing the `events` stream deletes its destination rows and re-syncs them. If you set a Start Date, events last modified before that date are not re-synced — export them first if you need them.
:::

Version 1.0.0 reads `events` from every calendar in the account when **Calendar Id** is empty, and adds the `acl` and `freebusy` streams. Because one `events` stream can now hold events from several calendars, three things change for it:

- **Primary key.** The primary key changes from `id` to `[calendar_id, id]`. Google keeps event ids unique per calendar only, and a meeting has the same id on the organiser's calendar and on each invitee's calendar. With `id` alone, *Append + Deduped* would keep one of those rows and drop the others.
- **`calendar_id` values.** `calendar_id` now holds the calendar's real ID. Connections configured with the alias `primary` get the account's email address instead of the word `primary`, so the column joins to `calendarlist.id`.
- **State format.** The saved `events` cursor moves to a format that covers all calendars. A cursor saved by an earlier version is not carried over, and the first sync after the upgrade re-reads the calendar.

Connections that set **Calendar Id** keep syncing that one calendar. To sync every calendar, clear the field after upgrading.

The `acl` stream needs the `calendar.acls.readonly` OAuth scope. Re-authorize the connector to grant it, or leave `acl` deselected.

After upgrading, refresh the source schema and clear the `events` stream so rows under the old primary key and `calendar_id` values are replaced.

## Connector upgrade guide

<MigrationGuide />
