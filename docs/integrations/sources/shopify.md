# Shopify

## Sync overview

The Shopify source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Shopify API](https://help.shopify.com/en/api/reference).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This Source is capable of syncing the following core Streams:

* [Abandoned Checkouts](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
* [Collects](https://help.shopify.com/en/api/reference/products/collect)
* [Custom Collections](https://help.shopify.com/en/api/reference/products/customcollection)
* [Customers](https://help.shopify.com/en/api/reference/customers)
* [Draft Orders](https://help.shopify.com/en/api/reference/orders/draftorder)
* [Discount Codes](https://shopify.dev/docs/admin-api/rest/reference/discounts/discountcode)
* [Metafields](https://help.shopify.com/en/api/reference/metafield)
* [Orders](https://help.shopify.com/en/api/reference/orders)
* [Products](https://help.shopify.com/en/api/reference/products)
* [Transactions](https://help.shopify.com/en/api/reference/orders/transaction)
* [Pages](https://help.shopify.com/en/api/reference/online-store/page)
* [Price Rules](https://help.shopify.com/en/api/reference/discounts/pricerule)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits).
Typically, there should not be issues with throttling or exceeding the rate limits but in some edge cases, user can receive the warning message as follows:
```
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```
This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error.
With given error message the sync operation is still goes on, but will require more time to finish.

## Getting started

1. Go to `https://YOURSTORE.myshopify.com/admin/apps/private`
2. Enable private development if it isn't enabled.
3. Create a private application.
4. Select the resources you want to allow access to. Airbyte only needs read-level access. 
   * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource. 
5. The password under the `Admin API` section is what you'll use as the `api_password` for the integration.
6. You're ready to set up Shopify in Airbyte!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.16  | 2021-09-09 | [5965](https://github.com/airbytehq/airbyte/pull/5945) | Fixed the connector's performance for `Incremental refresh` |
| 0.1.15  | 2021-09-02 | [5853](https://github.com/airbytehq/airbyte/pull/5853) | Fixed `amount` type in `order_refund` schema |
| 0.1.14  | 2021-09-02 | [5801](https://github.com/airbytehq/airbyte/pull/5801) | Fixed `line_items/discount allocations` & `duties` parts of `orders` schema |
| 0.1.13  | 2021-08-17 | [5470](https://github.com/airbytehq/airbyte/pull/5470) | Fixed rate limits throttling |
| 0.1.12  | 2021-08-09 | [5276](https://github.com/airbytehq/airbyte/pull/5276) | Add status property to product schema |
| 0.1.11  | 2021-07-23 | [4943](https://github.com/airbytehq/airbyte/pull/4943) | Fix products schema up to API 2021-07 |
| 0.1.10  | 2021-07-19 | [4830](https://github.com/airbytehq/airbyte/pull/4830) | Fix for streams json schemas, upgrade to API version 2021-07 |
| 0.1.9   | 2021-07-04 | [4472](https://github.com/airbytehq/airbyte/pull/4472) | Incremental sync is now using updated_at instead of since_id by default |
| 0.1.8   | 2021-06-29 | [4121](https://github.com/airbytehq/airbyte/pull/4121) | Add draft orders stream |
| 0.1.7   | 2021-06-26 | [4290](https://github.com/airbytehq/airbyte/pull/4290) | Fixed the bug when limiting output records to 1 caused infinity loop |
| 0.1.6   | 2021-06-24 | [4009](https://github.com/airbytehq/airbyte/pull/4009) | Add pages, price rules and discount codes streams |
| 0.1.5   | 2021-06-10 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.4   | 2021-06-09 | [3926](https://github.com/airbytehq/airbyte/pull/3926) | New attributes to Orders schema |
| 0.1.3   | 2021-06-08 | [3787](https://github.com/airbytehq/airbyte/pull/3787) | Add Native Shopify Source Connector |
