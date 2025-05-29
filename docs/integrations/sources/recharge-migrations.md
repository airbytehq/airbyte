# Recharge Migration Guide

## Upgrading to 2.0.0

This is a breaking change for **Shop** stream, which used `[shop, store]` fields as a primary key.
This version introduces changing of primary key from `[shop, store]`(type: object, object) to primary key `id`(type: integer), as it makes stream compatible with destinations that do not support complex primary keys(e.g. BigQuery).

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version. The **Shop** stream can be manually reset in the following way:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Click **Refresh source schema**, then **Ok**.
4. Select **Save changes** at the bottom of the page.
5. Select the **Status** tab and click three dots on the right side of **Shop**.
6. Press the **Clear data** button.
7. Return to the **Schema** tab.
8. Check all your streams.
9. Select **Sync now** to sync your data

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).