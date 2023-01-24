# WooCommerce

This page contains the setup guide and reference information for the WooCommerce source connector.

## Prerequisites

To set up the WooCommerce source connector with Airbyte, you must be using:

- WooCommerce 3.5+
- WordPress 4.4+
- Pretty permalinks in `Settings > Permalinks` so that the custom endpoints are supported.
  e.g. `/%year%/%monthnum%/%day%/%postname%/`

You will need to generate new API key with read permissions and use `Customer key` and `Customer Secret`.

## Setup guide

### Step 1: Set up WooCommerce

1. Generate new [Rest API key](https://woocommerce.github.io/woocommerce-rest-api-docs/#rest-api-keys)
2. Obtain `Customer key` and `Customer Secret`.

### Step 2: Set up the WooCommerce connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the WooCommerce connector and select **WooCommerce** from the Source
   type dropdown.
4. Fill in `Customer key` and `Customer Secret` with data from Step 1 of this guide.
5. Fill in `Shop Name`. For `https://EXAMPLE.com`, the shop name is 'EXAMPLE.com'.
6. Choose start date you want to start sync from.
7. (Optional) Fill in Conversion Window.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. On the Set up the source page, enter the name for the WooCommerce connector and select **WooCommerce** from the Source
   type dropdown.
4. Fill in `Customer key` and `Customer Secret` with data from Step 1 of this guide.
5. Fill in `Shop Name`. For `https://EXAMPLE.com`, the shop name is 'EXAMPLE.com'.
6. Choose start date you want to start sync from.
7. (Optional) Fill in Conversion Window.

## Supported sync modes

The WooCommerce source connector supports the
following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

- [Coupons](https://woocommerce.github.io/woocommerce-rest-api-docs/#coupons) \(Incremental\)
- [Customers](https://woocommerce.github.io/woocommerce-rest-api-docs/#customers) \(Incremental\)
- [orders](https://woocommerce.github.io/woocommerce-rest-api-docs/#orders) \(Incremental\)
- [Order notes](https://woocommerce.github.io/woocommerce-rest-api-docs/#order-notes)
- [Payment gateways](https://woocommerce.github.io/woocommerce-rest-api-docs/#payment-gateways)
- [Product attribute terms](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-attribute-terms)
- [Product attributes](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-attributes)
- [Product categories](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-categories)
- [Product reviews](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-reviews) \(Incremental\)
- [Product shipping classes](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-shipping-classes)
- [Product tags](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-tags)
- [Product variations](https://woocommerce.github.io/woocommerce-rest-api-docs/#product-variations)
- [Products](https://woocommerce.github.io/woocommerce-rest-api-docs/#products) \(Incremental\)
- [Refunds](https://woocommerce.github.io/woocommerce-rest-api-docs/#refunds)
- [Shipping methods](https://woocommerce.github.io/woocommerce-rest-api-docs/#shipping-methods)
- [Shipping zone locations](https://woocommerce.github.io/woocommerce-rest-api-docs/#shipping-zone-locations)
- [Shipping zone methods](https://woocommerce.github.io/woocommerce-rest-api-docs/#shipping-zone-methods)
- [Shipping zones](https://woocommerce.github.io/woocommerce-rest-api-docs/#shipping-zones)
- [System status tools](https://woocommerce.github.io/woocommerce-rest-api-docs/#system-status-tools)
- [Tax classes](https://woocommerce.github.io/woocommerce-rest-api-docs/#tax-classes)
- [Tax rates](https://woocommerce.github.io/woocommerce-rest-api-docs/#tax-rates)

## Connector-specific features & highlights

Useful links:

- [WooCommerce Rest API Docs](https://woocommerce.github.io/woocommerce-rest-api-docs/#introduction)

## Data type map

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |
| `boolean`        | `boolean`    |       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                    |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------- |
| 0.2.0   | 2022-11-30 | [19903](https://github.com/airbytehq/airbyte/pull/19903) | Migrate to low-code; Certification to Beta |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies            |
| 0.1.0   | 2021-09-09 | [5955](https://github.com/airbytehq/airbyte/pull/5955)   | Initial Release. Source WooCommerce        |
