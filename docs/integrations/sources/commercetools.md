# Commercetools

## Sync overview

The Commercetools source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Commercetools API](https://docs.commercetools.com/api/).

### Output schema

This Source is capable of syncing the following core Streams:

- [Customers](https://docs.commercetools.com/api/projects/customers)
- [Orders](https://docs.commercetools.com/api/projects/orders)
- [Products](https://docs.commercetools.com/api/projects/products)
- [DiscountCodes](https://docs.commercetools.com/api/projects/discountCodes)
- [Payments](https://docs.commercetools.com/api/projects/payments)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

### Performance considerations

Commercetools has some [rate limit restrictions](https://docs.commercetools.com/api/limits).

## Getting started

1. Create an API Client in the admin interface
2. Decide scopes for the API client. Airbyte only needs read-level access.
   - Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
3. The `projectKey` of the store, the generated `client_id` and `client_secret` are required for the integration
4. You're ready to set up Commercetools in Airbyte!

## Changelog

| Version | Date       | Pull Request                                             | Subject                               |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------ |
| 0.2.0   | 2023-08-24 | [29384](https://github.com/airbytehq/airbyte/pull/29384) | Migrate to low code                   |
| 0.1.1   | 2023-08-23 | [5957](https://github.com/airbytehq/airbyte/pull/5957)   | Fix schemas                           |
| 0.1.0   | 2021-08-19 | [5957](https://github.com/airbytehq/airbyte/pull/5957)   | Initial Release. Source Commercetools |
