# Microsoft Dataverse Migration Guide

## Upgrading to 1.0.0

This release corrects the schema type for Dataverse fields configured with `DateTimeBehavior=DateOnly`. Previously, all DateTime fields were mapped to `format: "date-time"` (timestamp with timezone), which caused DateOnly values like `"2024-03-15"` to fail RFC 3339 datetime validation, resulting in `DESTINATION_SERIALIZATION_ERROR` and nulled data.

Starting with version 1.0.0, DateOnly fields are correctly mapped to `format: "date"`. This is a schema type change that requires affected streams to be reset.

### Affected streams

Any stream containing one or more Dataverse columns with `DateTimeBehavior` set to `DateOnly` is affected. Common examples include custom date fields added to entities. Standard timestamp fields such as `createdon` and `modifiedon` use `UserLocal` behavior and are not affected.

### Downstream impact

If you have SQL queries, views, or dashboards that reference affected DateOnly columns as timestamps, you may need to update them to handle `date` values instead of `timestamp with time zone` values after the reset.

### Steps to upgrade

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.
   :::note
   Any detected schema changes will be listed for your review.
   :::
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked.
4. Select **Save connection**.
   :::note
   This will reset the data in your destination and initiate a fresh sync.
   :::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).
