# HubSpot

<HideInUI>

This page contains the setup guide and reference information for the [Pennylane](https://www.pennylane.com/) source connector.

</HideInUI>

## Prerequisites

- Pennylane Account

We recommend you setup a Sandbox (https://help.pennylane.com/fr/articles/18773-creer-un-environnement-de-test) to test the connector before using it in production.

## Setup guide

### Step 1: Set up Pennylane

1. Log in to your [Pennylane account](https://app.pennylane.com/auth/login).
2. In the sidebar, click **Company settings**.
3. Click **Connectivity** then go to the **Developers** tab.
4. Click **Generate an API token**.
5. Choose a **Token name**.
6. Select the data scopes that this token will give access to and make sure they match the endpoints you are targeting.
7. Select an expiration date and click **Generate token**.

For more information on Pennylane API tokens, see the [Pennylane documentation](https://help.pennylane.com/fr/articles/18770-utiliser-l-api-publique-pennylane#h_b5fb4b01ed).

### Step 2: Set up the Pennylane source connector in Airbyte

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or your Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Pennylane** from the list of available sources.
4. For **Source name**, enter a name to help you identify this source.
5. For **API Key**, enter the API token you created for the connection.
6. For **Start time**, use the provided datepicker or enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added after this datetime will be replicated.

## Supported sync modes

The Pennylane source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

- [Categories](https://pennylane.readme.io/reference/tags-get) \(Incremental\)
- [Category Groups](https://pennylane.readme.io/reference/tag-groups-get) \(Incremental\)
- [Customer Invoices](https://pennylane.readme.io/reference/customer_invoices-get-1) \(Incremental\)
- [Customers](https://pennylane.readme.io/reference/customers-get-1) \(Incremental\)
- [Plan Items](https://pennylane.readme.io/reference/plan_items-get-1)
- [Products](https://pennylane.readme.io/reference/products-get-1) \(Incremental\)
- [Supplier Invoices](https://pennylane.readme.io/reference/supplier_invoices-get) \(Incremental\)
- [Suppliers](https://pennylane.readme.io/reference/suppliers-get) \(Incremental\)

## Data type map

The [Pennylane API](https://paystack.com/docs/api) is compatible with the [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Performance considerations

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                        |
| :------ | :--------- | :----------- | :----------------------------- |
| 0.1.0   | 2024-08-04 |              | Add Pennylane source connector |

</details>
