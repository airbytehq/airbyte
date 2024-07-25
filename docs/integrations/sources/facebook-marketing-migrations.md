# Facebook Marketing Migration Guide

## Upgrading to 3.1.0

The `AdsInsights` Reports now don't have the possibility to fetch the next root level properties (fields):
- cost_per_conversion_lead
- conversion_lead_rate

### Refresh affected AdsInsights Report:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab. 
    1. Select **Refresh source schema**. 
    2. Select **OK** 
    3. Select **Save changes** at the bottom of the page.
   :::note
   Any detected schema changes will be listed for your review.
   :::

### Custom streams

Custom streams will not be able to rely on `cost_per_conversion_lead` and `conversion_lead_rate` as `fields` anymore. Those streams will need to updated considering the fact that the information is not available in Facebook Marketing.

## Upgrading to 3.0.0

Custom Insights Reports now have updated schema for following breakdowns:

- body_asset
- call_to_action_asset
- description_asset
- image_asset
- link_url_asset
- title_asset
- video_asset

| Field                  | Old Type | New Type | Example                                                                                                                           |
| :--------------------- | :------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `body_asset`           | string   | object   | `{"text": "Body Text", "id": "12653412653"}`                                                                                      |
| `call_to_action_asset` | string   | object   | `{"name": "Action Name", "id": "12653412653"}`                                                                                    |
| `description_asset`    | string   | object   | `{"text": "Description", "id": "12653412653"}`                                                                                    |
| `image_asset`          | string   | object   | `{"hash": "hash_value", "url": "http://url","id": "12653412653" }`                                                                |
| `link_url_asset`       | string   | object   | `{"website_url": "http://url","id": "12653412653" }`                                                                              |
| `title_asset`          | string   | object   | `{"text": "Text", "id": "12653412653" }`                                                                                          |
| `video_asset`          | string   | object   | `{"video_id": "2412334234", "url": "http://url", "thumbnail_url: "http://url", "video_name": "Video Name", "id": "12653412653" }` |

### Refresh affected Custom Insights Report above and clear data if it uses breakdowns

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab. 
    1. Select **Refresh source schema**. 
    2. Select **OK** 
    3. Select **Save changes** at the bottom of the page.
   :::note
   Any detected schema changes will be listed for your review.
   :::

3. Navigate to a connection's **Settings** tab and click **Clear data** to clear all streams. This action will clear data for all streams in the connection. To clear data for a single stream navigate to the **Status** tab,  click the **three grey dots** next to the affected stream, and select **Clear data**. Do this for all affected streams in the connection.

For more information on clearing your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 2.0.0

Streams Ads-Insights-\* streams now have updated schemas.

:::danger
Please note that data older than 37 months will become unavailable due to Facebook limitations.
It is recommended to create a backup at the destination before proceeding with migration.
:::

### Update Custom Insights Reports (this step can be skipped if you did not define any)

1. Select **Sources** in the main navbar.
   1. Select the Facebook Marketing Connector.
2. Select the **Retest saved source**.
3. Remove unsupported fields from the list in Custom Insights section.
4. Select **Test and Save**.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page. 1. Ensure the **Reset affected streams** option is checked.
   :::note
   Depending on destination type you may not be prompted to reset your data.
   :::
4. Select **Save connection**.
   :::note
   This will reset the data in your destination and initiate a fresh sync.
   :::

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).
