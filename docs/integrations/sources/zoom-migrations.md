import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Zoom Migration Guide

## Upgrading to 2.0.0

### WHAT

Version 2.0.0 adds primary keys, date-time formats, and Incremental sync support:

- The `meeting_polls` key is now `[meeting_id, id]`; `meeting_poll_results` is `[meeting_id, name]`; `meeting_registration_questions` is `[meeting_id]`; and `report_meeting_participants` is `[meeting_id, user_id]`.
- The `webinar_panelists`, `webinar_registrants`, and `webinar_polls` keys are `[webinar_id, id]`; `webinar_poll_results` and `webinar_qna_results` are `[webinar_id, name]`; `webinar_registration_questions` is `[webinar_id]`; `report_webinars` is `[uuid]`; and `report_webinar_participants` is `[webinar_uuid, user_id]`.
- ISO-8601 timestamp fields now use the `date-time` schema format in `users`, `meetings`, `meeting_registrants`, `meeting_poll_results`, `webinars`, `webinar_registrants`, `webinar_absentees`, `webinar_poll_results`, `report_meetings`, `report_meeting_participants`, `report_webinars`, and `report_webinar_participants`.
- `meetings`, `report_meetings`, `report_meeting_participants`, `webinars`, `report_webinars`, and `report_webinar_participants` now support Incremental sync. The optional `start_date` applies to these streams as well as `report_user_meetings` and `report_daily`.

Registration-question streams emit one record per meeting or webinar, with questions nested in arrays. Their keys therefore use the parent ID rather than a nested `field_name`.

### WHY

Composite keys distinguish records that repeat across meetings or webinars, and typed timestamps make their date-time semantics explicit. Incremental sync uses meeting or webinar creation dates with a 30-day lookback to avoid repeatedly reading older parent records.

### WHO

Refresh the source schema and refresh/reset any affected stream whose primary key, field format, or sync mode changes. If you sync any of the streams listed above, back up its destination data before refreshing.

### STEPS

1. Back up the destination tables for affected streams.
2. Upgrade the Zoom source to 2.0.0 and refresh the source schema.
3. Refresh/reset each affected stream. A refresh only re-reads records from the configured `start_date`; without one, the incremental streams start from `2010-01-01T00:00:00Z`.
4. Save the connection and allow the refreshed sync to complete.

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
