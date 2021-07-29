# Chargebee

## Overview

The Chargebee source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Chargebee source uses the [Chargebee Python Client Library](https://github.com/chargebee/chargebee-python/).

### Output schema

This connector outputs the following streams:

* [Subscriptions](https://apidocs.chargebee.com/docs/api/subscriptions?prod_cat_ver=2#list_subscriptions)
* [Customers](https://apidocs.chargebee.com/docs/api/customers?prod_cat_ver=2#list_customers)
* [Invoices](https://apidocs.chargebee.com/docs/api/invoices?prod_cat_ver=2#list_invoices)
* [Orders](https://apidocs.chargebee.com/docs/api/orders?prod_cat_ver=2#list_orders)
* [Plans](https://apidocs.chargebee.com/docs/api/plans?prod_cat_ver=1&lang=curl#list_plans)
* [Addons](https://apidocs.chargebee.com/docs/api/addons?prod_cat_ver=1&lang=curl#list_addons)

### Notes

Some streams may depend on Product Catalog version and be accessible only on sites with specific Product Catalog version. This means that we have following streams:

1. presented in both `Product Catalog 1.0` and `Product Catalog 2.0`:
    - Subscriptions
    - Customers
    - Invoices
    - Orders
    
2. presented only in `Product Catalog 1.0`:
    - Plans
    - Addons
    
3. presented only in `Product Catalog 2.0` will be added soon.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Chargebee connector should not run into [Chargebee API](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_rate_limits) limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Chargebee Account;
* `site_api_key` - Chargebee API Key wih the necessary permissions \(described below\);
* `site` - Chargebee site prefix for your instance;
* `start_date` - start date for incremental streams;
* `product_catalog` - Product Catalog version of your Chargebee site \(described below\).

### Setup guide

Log into Chargebee and then generate an [API Key](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2#api_authentication).
Then follow [these](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2) instructions, under `API Version` section, on how to find your Product Catalog version.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.2   | 2021-07-30 | [5067](https://github.com/airbytehq/airbyte/pull/5067) | Prepare connector for publishing |
| 0.1.1   | 2021-07-07 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add entrypoint and bump version for connector |
| 0.1.0   | 2021-06-30 | [3410](https://github.com/airbytehq/airbyte/pull/3410) | New Source: Chargebee |
