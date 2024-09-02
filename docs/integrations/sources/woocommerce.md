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

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the WooCommerce connector and select **WooCommerce** from the Source
   type dropdown.
4. Fill in `Customer key` and `Customer Secret` with data from Step 1 of this guide.
5. Fill in `Shop Name`. For `https://EXAMPLE.com`, the shop name is 'EXAMPLE.com'.
6. Choose start date you want to start sync from.
7. (Optional) Fill in Conversion Window.
<!-- env:oss -->

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

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)
<!-- /env:oss -->

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

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about WooCommerce connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The WooCommerce API allows to
set [custom rate limits](https://developer.woocommerce.com/2022/11/22/store-api-now-supports-rate-limiting/) to protect
your store. If you set a custom rate limit,
specify it in seconds in the `maxSecondsBetweenMessages` field in the `metadata.yaml` file. This value should be the
maximum number of seconds between API calls.
</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                |
|:--------| :--------- |:---------------------------------------------------------|:-----------------------------------------------------------------------|
| 0.4.6 | 2024-08-31 | [44957](https://github.com/airbytehq/airbyte/pull/44957) | Update dependencies |
| 0.4.5 | 2024-08-24 | [44627](https://github.com/airbytehq/airbyte/pull/44627) | Update dependencies |
| 0.4.4 | 2024-08-19 | [44388](https://github.com/airbytehq/airbyte/pull/44388) | Update the CDK version to support RFR for Low-Code substreams |
| 0.4.3 | 2024-08-17 | [44228](https://github.com/airbytehq/airbyte/pull/44228) | Update dependencies |
| 0.4.2 | 2024-08-12 | [43786](https://github.com/airbytehq/airbyte/pull/43786) | Update dependencies |
| 0.4.1 | 2024-08-10 | [43487](https://github.com/airbytehq/airbyte/pull/43487) | Update dependencies |
| 0.4.0 | 2024-08-06 | [43323](https://github.com/airbytehq/airbyte/pull/43323) | Update CDK to v4, Python 3.10 |
| 0.3.1 | 2024-08-03 | [43054](https://github.com/airbytehq/airbyte/pull/43054) | Update dependencies |
| 0.3.0 | 2024-07-26 | [42551](https://github.com/airbytehq/airbyte/pull/42551) | Make builder compatible |
| 0.2.13 | 2024-07-27 | [42637](https://github.com/airbytehq/airbyte/pull/42637) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42157](https://github.com/airbytehq/airbyte/pull/42157) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41731](https://github.com/airbytehq/airbyte/pull/41731) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41581](https://github.com/airbytehq/airbyte/pull/41581) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41161](https://github.com/airbytehq/airbyte/pull/41161) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40814](https://github.com/airbytehq/airbyte/pull/40814) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40375](https://github.com/airbytehq/airbyte/pull/40375) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40094](https://github.com/airbytehq/airbyte/pull/40094) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39270](https://github.com/airbytehq/airbyte/pull/39270) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-05-21 | [38544](https://github.com/airbytehq/airbyte/pull/38544) | [autopull] base image + poetry + up_to_date |
| 0.2.3 | 2023-06-02 | [26955](https://github.com/airbytehq/airbyte/pull/26955) | Added `block_context` and `author` properties to the `Products` stream |
| 0.2.2 | 2023-03-03 | [23599](https://github.com/airbytehq/airbyte/pull/23599) | Fix pagination and removed lookback window |
| 0.2.1 | 2023-02-10 | [22821](https://github.com/airbytehq/airbyte/pull/22821) | Specified date formatting in specification |
| 0.2.0 | 2022-11-30 | [19903](https://github.com/airbytehq/airbyte/pull/19903) | Migrate to low-code; Certification to Beta |
| 0.1.1 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.0 | 2021-09-09 | [5955](https://github.com/airbytehq/airbyte/pull/5955) | Initial Release. Source WooCommerce |

</details>
