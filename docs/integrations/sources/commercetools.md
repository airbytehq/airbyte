# CommerceTools

## Sync overview

The CommerceTools source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [CommerceTools API](https://docs.commercetools.com/api/).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://docs.commercetools.com/api/projects/customers)
* [Orders](https://docs.commercetools.com/api/projects/orders)
* [Payments](https://docs.commercetools.com/api/projects/payments)
* [DiscountCodes](https://docs.commercetools.com/api/projects/discountCodes)
* [Products](https://docs.commercetools.com/api/projects/products)


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

CommerceTools has some [rate limit restrictions](https://docs.commercetools.com/api/limits).

## Getting started

1. Log into your CommerceTools admin page
2. Create an API Client
3. Select the resources you want to allow access to. Airbyte only needs read-level access.
    * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
4  Set up the integration on Airbyte using the region of your store and, the client_id and client_secret generated for the API client
5. You're ready to set up CommerceTools in Airbyte!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0  | 2021-09-01 | [5521](https://github.com/airbytehq/airbyte/pull/5521) | Initial Release. Source CommerceTools |
