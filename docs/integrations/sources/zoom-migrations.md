import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Zoom Migration Guide

## Upgrading to 2.0.0

:::danger Risk of permanent data loss
Clearing a Full Refresh | Append stream permanently deletes destination history that Zoom can no longer serve, including reports older than roughly six months and meetings older than one year. Back up the affected tables before clearing.
:::

### WHAT

- Primary keys are added or changed for `meeting_polls` (`[meeting_id, id]`), `meeting_registration_questions` (`[meeting_id]`), `report_meetings` (`[uuid]`), and `report_meeting_participants` (`[meeting_uuid, user_id]`). Webinar keys are `webinar_panelists`, `webinar_registrants`, and `webinar_polls` (`[webinar_id, id]`); `webinar_registration_questions` (`[webinar_id]`); `report_webinars` (`[uuid]`); and `report_webinar_participants` (`[webinar_uuid, user_id]`). `meeting_poll_results`, `webinar_poll_results`, and `webinar_qna_results` have no primary key because a result name is not unique.
- `webinar_id` is an integer in `webinar_panelists`, `webinar_registrants`, `webinar_polls`, `webinar_registration_questions`, `webinar_poll_results`, and `webinar_qna_results`. The two result streams add the field, and `webinar_tracking_sources.webinar_id` changes from a string to an integer.
- Timestamp fields now use the `date-time` schema format: `users.created_at`, `users.user_created_at`, and `users.last_login_time`; `meetings` and `webinars` `created_at`, `start_time`, `occurrences[].start_time`, and `recurrence.end_date_time`; `meeting_registrants.create_time`, `webinar_registrants.create_time`, and `webinar_absentees.create_time`; `start_time` and `end_time` in the meeting and webinar report streams; and `join_time` and `leave_time` in the meeting and webinar report participant streams.
- The `users` stream adds `login_types`. The `report_meeting_participants` stream adds `meeting_uuid` and `meeting_end_time`; `meeting_id` remains the numeric meeting ID. Registration-question streams emit one record per meeting or webinar with questions nested in arrays, so their keys use the parent ID rather than a nested `field_name`.
- Incremental sync is supported for `meetings`, `report_meetings`, `report_meeting_participants`, `webinars`, and `report_user_meetings`. `report_webinars`, `report_webinar_participants`, and `report_daily` use Full Refresh.
- Incremental `meetings` and `webinars` use `created_at` with a 30-day lookback. Edits to meetings or webinars created before that window are not picked up by incremental sync; a Full Refresh picks them up.
- `meetings` and `webinars` include only records created on or after `start_date`, including in Full Refresh. Leave `start_date` empty to sync everything Zoom still serves. `report_user_meetings`, `report_daily`, `report_meetings`, and `report_meeting_participants` start at `start_date` and are limited to Zoom's roughly six months of report retention; `report_daily` starts at the beginning of that month. `report_webinars` and `report_webinar_participants` are not filtered by `start_date`.

The poll-results `question_details[].date_time` fields remain unformatted because live Zoom values use `YYYY-MM-DD HH:MM:SS`, not ISO 8601. Update SQL, dbt models, and dashboards that treat the retyped timestamp columns or `webinar_id` as strings.

### Report meeting streams

`report_meetings` and `report_meeting_participants` now use Zoom's past-meetings report, which can return rows for eligible meeting sessions, including separate rows for sessions of recurring meetings. Zoom's past-meetings report omits sessions with fewer than two participants, so those sessions produce no report rows. Zoom retains these reports for roughly six months, and `start_date` further limits the requested report window.

These streams require the classic `report:read:admin` scope or the granular `report:read:user:admin` scope. Zoom apps set up before source-zoom 1.5.0 may not have the required scope; without it, sync fails with a configuration error naming the missing scope. After adding the scope, users with OAuth credentials must re-authenticate the source.

### WHY

Composite keys distinguish records that repeat across meetings or webinars, and typed timestamps make their date-time semantics explicit. Meeting report streams use session end times so a report is fetched when the session ends, even when the meeting was created much earlier.

### WHO

Users syncing `users`, `meetings`, `meeting_registrants`, `meeting_polls`, `meeting_registration_questions`, `webinars`, `webinar_panelists`, `webinar_registrants`, `webinar_absentees`, `webinar_polls`, `webinar_poll_results`, `webinar_registration_questions`, `webinar_qna_results`, `webinar_tracking_sources`, `report_meetings`, `report_meeting_participants`, `report_webinars`, or `report_webinar_participants` are affected.

Users syncing only `chat_channels`, `meeting_poll_results`, `report_user_meetings`, `report_daily`, or `zoom_events` are not affected by this upgrade.

### STEPS

1. Add the report scope if needed. Upgrade the Zoom source to 2.0.0 and refresh the source schema.
2. For **Full Refresh | Overwrite** streams, no other action is needed; the next sync rebuilds the stream with the new schema.
3. For **Full Refresh | Append** streams, back up the destination first. Refresh the schema while retaining existing records, or leave the existing records in place and accept that old rows keep their previous types.

:::note
If you set `start_date` in source-zoom 1.5.0 for `report_user_meetings` or `report_daily`, `meetings` and `webinars` now include only records created on or after that date, including during Full Refresh. Clear `start_date` to keep everything Zoom still serves.
:::

## Upgrading to 1.1.0

### Authentication

As of September 8, 2023, Zoom has [deprecated JWT](https://developers.zoom.us/docs/internal-apps/jwt-faq/) authentication and now supports Oauth instead.

### Creating a server-to-server OAuth app

To successfully migrate, please use [Zoom's migration guide](https://developers.zoom.us/docs/internal-apps/jwt-app-migration/) to create a new server-to-server OAuth app and generate the necessary credentials.

When creating the app, ensure you grant it access to the following scopes:

- user:read:admin
- meeting:read:admin
- webinar:read:admin
- chat_channel:read:admin
- report:read:admin

To successfully authenticate your connection in Airbyte, you will need to input the following OAuth credentials:

- client_id
- client_secret
- account_id
- authorization_endpoint

### Schema changes

The type of the 'meeting_id' field in Meeting Registration Questions stream has been changed from "string" to "integer". Users with existing connections that are syncing data from this stream should refresh their schemas and reset their data.

#### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

4. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear)

## Connector upgrade guide

<MigrationGuide />
