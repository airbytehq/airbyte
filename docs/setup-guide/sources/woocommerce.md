# WooCommerce

This page contains the setup guide and reference information for WooCommerce.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

## Setup guide

1. Navigate to your store's WordPress admin interface, go to WooCommerce \> Settings \> Advanced \> REST API.

2. Click on "Add Key" to generate an API Key.

3. Choose the level of access for this REST API key, which can be Read access, Write access or Read/Write access. Daspire only needs read-level access.

  > **Note:** The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.

4. The two keys, Consumer Key and Consumer Secret are what you'll use respectively as api\_key and api\_secret for the integration.

5. You're ready to set up WooCommerce in Daspire!

## Sync overview

The WooCommerce source supports both **Full Refresh** and **Incremental** syncs. You can choose to copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Daspire can sync data for the [WooCommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/).

## Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-customers)
* [Orders](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-orders)
* [Coupons](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-coupons)

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |