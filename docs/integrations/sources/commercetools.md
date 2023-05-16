# Commercetools

## Sync overview

The Commercetools source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Commercetools API](https://docs.commercetools.com/api/).

### Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://docs.commercetools.com/api/projects/customers)
* [Orders](https://docs.commercetools.com/api/projects/orders)
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

1. Log in to your Commercetools account or create a new one [here](https://commercetools.com/signup).
2. Create an [API client](https://docs.commercetools.com/api/authorization/creating-and-managing-clients) in your Commercetools account by following the instructions provided.
3. Choose the desired scopes for the API client, keeping in mind that Airbyte only needs read-level access.
    * Note: The user interface will show all possible data sources, and will show errors when syncing if the API client doesn't have permission to access a resource.
4. Navigate to the [Dashboard](https://docs.commercetools.com/dashboard/?language=en) section of your Commercetools account.
5. Under the Project Settings section, locate and copy the `projectKey` for the store you wish to replicate data from.
6. Navigate back to Airbyte.
7. In the Commercetools configuration page, under "Connection Configuration," fill out the following fields:
    * `region`: The region of the platform, which can be found in the Commercetools [documentation](https://docs.commercetools.com/api/authorization#regions).
    * `host`: The cloud provider your shop is hosted on. Choose either `gcp` or `aws`, as per your setup.
    * `start_date`: The date from which you would like to replicate data. Use the format YYYY-MM-DD.
    * `project_key`: The `projectKey` you copied earlier.
    * `client_id`: The `client_id` of the API client you created in step 2.
    * `client_secret`: The `client_secret` of the API client you created in step 2.
8. Click "Test Connection" to check that the connection has been successfully established.
9. If the connection test is successful, click "Create" to create the Commercetools source connector.
10. You're now ready to use the Commercetools source in Airbyte!

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0  | 2021-08-19 | [5957](https://github.com/airbytehq/airbyte/pull/5957) | Initial Release. Source Commercetools |