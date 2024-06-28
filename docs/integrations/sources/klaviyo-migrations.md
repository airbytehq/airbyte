# Klaviyo Migration Guide

## Upgrading to 3.0.0
Stream `event_detailed` is now request only event API instead if requesting each event with id. 

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before 
resuming your data syncs with the new version. The **Event Detailed** stream can be manually reset in the following way:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Click **Refresh source schema**, then **Ok**.
4. Select **Save changes** at the bottom of the page.
5. Select the **Status** tab and click three dots on the right side of **Workflows**.
6. Press the **Clear data** button.
7. Return to the **Schema** tab.
8. Check all your streams.
9. Select **Sync now** to sync your data

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 2.0.0

Streams `campaigns`, `email_templates`, `events`, `flows`, `global_exclusions`, `lists`, and `metrics` are now pulling
data using latest API which has a different schema. Users will need to refresh the source schemas and reset these
streams after upgrading. See the chart below for the API version change.

| Stream            | Current API version | New API version |
|-------------------|---------------------|-----------------|
| campaigns         | v1                  | 2023-06-15      |
| email_templates   | v1                  | 2023-10-15      |
| events            | v1                  | 2023-10-15      |
| flows             | v1                  | 2023-10-15      |
| global_exclusions | v1                  | 2023-10-15      |
| lists             | v1                  | 2023-10-15      |
| metrics           | v1                  | 2023-10-15      |
| profiles          | 2023-02-22          | 2023-02-22      |

## Upgrading to 1.0.0

`event_properties/items/quantity` for `Events` stream is changed from `integer` to `number`.
For a smooth migration, data reset and schema refresh are needed.
