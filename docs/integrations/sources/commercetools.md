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

## Setup Guide

This guide will walk you through the process of configuring the commercetools Source connector in Airbyte.

### Prerequisites

Before you begin setting up the commercetools Source connector, you need to have access to the commercetools platform. If you don't have access yet, you can sign up for an account at the [commercetools website](https://commercetools.com/).

### Step 1: Create an API Client

To create an API client, follow these steps:

1. Log in to the [commercetools Admin Center](https://mc.commercetools.com/login).
2. Select your project.
3. Go to the "Settings" (gear icon) in the left sidebar.
4. Navigate to "Developer Settings" > "API Clients".
5. Click on "Create New API Client".
6. Fill in the "Display name" and "Description" fields according to your preferences.
7. Choose the appropriate "Scopes" for the API client. Airbyte only needs read-level access.
    * Note: The UI will show all possible data sources and will display errors when syncing if it doesn't have permissions to access a resource.

### Step 2: Retrieve API Client Credentials

After creating the API client in commercetools, you will see the generated `client_id` and `client_secret`. You will need these credentials, along with the `project_key` of the store for the integration.

Make sure to copy the `client_id` and `client_secret` as they will not be visible again.

### Step 3: Configure the commercetools Source Connector in Airbyte

To configure the commercetools Source connector, you need to provide the following information:

- **Region**: The region of the platform (e.g., `us-central1`, `australia-southeast1`). For more details on how to choose the region, refer to the [commercetools API documentation](https://docs.commercetools.com/api/authorization#region).
- **Host**: The cloud provider your shop is hosted on (`gcp`, `aws`). See the [commercetools API authorization documentation](https://docs.commercetools.com/api/authorization) for more information.
- **Start_date**: The date from which you would like to replicate data. Format: `YYYY-MM-DD` (e.g., `2021-01-01`).
- **Project_key**: The `project_key` of the store. It can be found in the commercetools Admin Center under the "Settings" (gear icon) in the left sidebar.
- **Client_id**: The generated `client_id` from Step 2.
- **Client_secret**: The generated `client_secret` from Step 2.



## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0  | 2021-08-19 | [5957](https://github.com/airbytehq/airbyte/pull/5957) | Initial Release. Source Commercetools |
