# Commercetools

## Sync overview

The Commercetools source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Commercetools API](https://docs.commercetools.com/api/).

### Output schema

This Source is capable of syncing the following core Streams:
- Customers
- Orders
- Products
- DiscountCodes
- Payments

### Data type mapping

| Integration Type | Airbyte Type | Notes                    |
|------------------|--------------|-------------------------|
| `string`         | `string`     |                         |
| `number`         | `number`     |                         |
| `array`          | `array`      |                         |
| `object`         | `object`     |                         |

## Getting started

Here are the steps to set up Commercetools as an Airbyte Source Connector.

1. Log in to the [Commercetools Merchant Center](https://login.commercetools.com/signin).

2. Click on the **API Clients** link on the sidebar navigation menu.

3. Click the **Create new client** button.

4. Enter a friendly **Client Name**.

5. Make sure the **Grant Type** is set to **Confidential**.

6. In the **Scopes** section, select the needed permissions. For Airbyte, only the **View Data** permission is needed.

7. Click **Create API Client**.

8. You will see a page with your client's **Client ID** and **Client Secret**. Copy these values, as you will need them later.

9. In the Airbyte UI, in the Commercetools configuration screen, enter the following values:

     - **Region**: The region of the platform. Examples: `"us-central1"`, `"australia-southeast1"`.
     - **Host**: The cloud provider your shop is hosted. Choose from `"gcp"`, `"aws"`.
     - **Start Date**: The date you would like to replicate data. Format: `YYYY-MM-DD`.
     - **Project Key**: The project key.

10. In the `credentials` field enter a JSON object with the following structure:

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

11. Save the configuration.

You are now ready to set up Commercetools in Airbyte!