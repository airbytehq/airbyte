# Commercetools

## Sync overview

The Commercetools source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Commercetools API](https://docs.commercetools.com/api/).

### Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://docs.commercetools.com/api/projects/customers)
* [Orders](https:///docs.commercetools.com/api/projects/orders)
* [Products](https://docs.commercetools.com/api/projects/products)
* [DiscountCodes](https://docs.commercetools.com/api/projects/discountCodes)
* [Payments](https://docs.commercetools.com/api/projects/payments)

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

Commercetools has some [rate limit restrictions](https://docs.commercetools.com/api/limits).

## Getting started

To set up the Commercetools source connector, follow these steps:

1. In the Commercetools admin interface, go to the [Developer Settings](https://docs.commercetools.com/docs/developer-settings) section.
2. Click on "API Clients" and then click on the "New API Client" button to create an API Client.
3. Provide a name for your API Client and choose the desired scopes. Airbyte requires read-level access.
   * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
4. Once the API Client is created, you will receive the `client_id`, `client_secret`, and `projectKey` which are required for the integration.
5. In the Airbyte configuration form for the Commercetools source connector, enter the following information:
   * `region`: The region of the platform (e.g. "us-central1" or "australia-southeast1").
   * `host`: The cloud provider your shop is hosted on. See the [Commercetools API documentation](https://docs.commercetools.com/api/authorization) for more details.
   * `start_date`: The date you would like to replicate data starting from. The format should be "YYYY-MM-DD" (e.g. "2021-01-01").
   * `project_key`: Enter the `projectKey` you obtained in Step 4.
   * `client_id`: Enter the `client_id` you obtained in Step 4.
   * `client_secret`: Enter the `client_secret` you obtained in Step 4.
6. You're now ready to set up the Commercetools source connector in Airbyte!

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-08-19 | [5957](https://github.com/airbytehq/airbyte/pull/5957) | Initial Release. Source Commercetools |