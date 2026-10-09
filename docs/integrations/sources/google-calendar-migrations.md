import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Google Calendar Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 reads `events` from every calendar in the account when **Calendar Id** is empty, adds the `acl` and `freebusy` streams, and changes the `events`, `calendars` and `colors` streams.

:::danger Risk of permanent data loss
Clearing the `events` stream deletes its destination rows and re-reads only what Google still returns. Events last modified before your Start Date are not re-read, events deleted in Google Calendar come back with at most their ID and a `cancelled` status (or not at all), and with an Append sync mode every earlier copy of each event is lost. Back up the `events` table before you clear it if you need that history.
:::

### `events`

Because one `events` stream can now hold events from several calendars, these things change for it:

- **Primary key.** The primary key changes from `id` to `[calendar_id, id]`. Google keeps event ids unique per calendar only, and a meeting has the same id on the organiser's calendar and on each invitee's calendar. With `id` alone, *Append + Deduped* would keep one of those rows and drop the others.
- **`calendar_id` values.** `calendar_id` now holds the calendar's real ID. Connections configured with the alias `primary` get the account's email address instead of the word `primary`, so the column joins to `calendarlist.id`.
- **Date and timestamp types.** `created`, `updated`, and the `dateTime` fields of `start`, `end` and `originalStartTime` are typed as timestamps. `start.date`, `end.date` and the new `originalStartTime.date` are typed as dates.
- **State format.** The saved `events` cursor moves to a format that covers all calendars. Version 1.0.0 does not read a cursor saved by 0.1.0, so the first incremental sync after the upgrade re-reads every event since the Start Date, or every event if Start Date is empty.

Connections that set **Calendar Id** keep syncing that one calendar. To sync every calendar instead, empty the field before you clear `events`, so the clear re-reads every calendar. If you empty it later, clear `events` again: otherwise an incremental sync reads only events changed after the switch from the other calendars.

With **Calendar Id** empty, `events` reads only the calendars the account can read events from, and `acl` only the calendars it owns. Calendars shared with the account as free/busy only are read by `freebusy` alone.

### `calendars`

`calendars` used to return the same calendar-list entries as `calendarlist`. It now returns the calendar resource of each calendar in the calendar list that the account can read: `id`, `summary`, `description`, `location`, `timeZone` and `conferenceProperties`. The per-user fields of a list entry (`accessRole`, colors, reminders, `primary`, `selected`) stay in `calendarlist`.

### `colors`

The primary key changes from `[calendar, event]`, two objects keyed by color ID, to `kind`. The stream returns one record. Its `updated` field is typed as a timestamp.

### Update downstream queries

- Queries that filter `events.calendar_id = 'primary'` stop matching. Filter on the account's email address instead.
- Once `events` reads more than one calendar, `events.id` is no longer unique. Joins, uniqueness tests and deduplication logic must use `(calendar_id, id)`.
- Queries that read `accessRole`, colors or reminders from `calendars` must read them from `calendarlist`.

### `acl` scope

The new `acl` stream needs the `calendar.acls.readonly` scope, unless your refresh token already has `calendar.acls` or `calendar`. Generate a new refresh token for your OAuth client that includes the scope and paste it into **Refresh token**, or leave `acl` deselected. If your connection adds new streams automatically, deselect `acl` until the token has the scope; otherwise every sync fails.

### Refresh schemas and clear data

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This clears the data in your destination for the affected streams. After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

<MigrationGuide />
