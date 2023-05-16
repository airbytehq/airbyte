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

## Getting Started

Here are the steps needed to set up Commercetools in Airbyte:

1. Log in to your Commercetools account.
2. Select **API clients** from the main menu to create a new API client.
3. Give your API client a name and description, e.g., `Airbyte_read_only`.
4. Generate a password for the client. Save the password as it will not be displayed again.
5. Select the **Scopes** tab.
6. Select **Manage Scopes**.
7. Locate the `OAuth2 Scopes` section. Ensure that the following scopes are enabled:
   * `view_customers`
   * `view_orders`
   * `view_products`
   * `view_discounts`
   * `view_payments`
8. Select the **Create API client** button at the bottom of the page.
9. After creating the API client, get the project key, client ID, and client secret.
10. In Airbyte UI, enter the `project_key`, `client_id`, and `client_secret`.
11. Select the correct `region` of your Commercetools account.
12. Enter the `start_date` to replicate data. The format should be `YYYY-MM-DD`.
13. Select the `host` where your shop is hosted. See: [https://docs.commercetools.com/api/authorization](https://docs.commercetools.com/api/authorization).
14. Test the connection. If it is successful, select **Save & Continue** followed by **Test**. If the test is successful, select **Submit**.

You are now ready to replicate data from Commercetools to Airbyte!

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0  | 2021-08-19 | [5957](https://github.com/airbytehq/airbyte/pull/5957) | Initial Release. Source Commercetools |