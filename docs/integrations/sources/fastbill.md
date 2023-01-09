# Fastbill 

This page contains the setup guide and reference information for the [Fastbill](https://www.fastbill.com/) source connector.

You can find more information about the Fastbill REST API [here](https://apidocs.fastbill.com/).

## Prerequisites

You can find your Project ID and find or create an API key within [Fastbill](https://my.fastbill.com/index.php?s=D7GCLx0WuylFq3nl4gAvRQMwS8RDyb3sCe_bEoXoU_w).

## Setup guide

## Step 1: Set up the Fastbill connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Fastbill connector and select **Fastbill** from the Source type dropdown.
4. Enter your `username` - Fastbill username/email.
5. Enter your `api_key` - Fastbill API key with read permissions.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
3. Enter your `project_id` - Fastbill Project ID.
4. Enter your `api_key` - Fastbill API key with read permissions.
5. Click **Set up source**.

## Supported sync modes

The Fastbill source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

## Supported Streams

* [Customers](https://apidocs.fastbill.com/fastbill/de/customer.html#customer.get)
* [Invoices](https://apidocs.fastbill.com/fastbill/de/invoice.html#invoice.get)
* [Products](https://apidocs.fastbill.com/fastbill/de/recurring.html#recurring.get)
* [Recurring_invoices](https://apidocs.fastbill.com/fastbill/de/recurring.html#recurring.get)
* [Revenues](https://apidocs.fastbill.com/fastbill/de/revenue.html#revenue.get)

## Data type map

| Integration Type    | Airbyte Type |
| :------------------ | :----------- |
| `string`            | `string`     |
| `integer`, `number` | `number`     |
| `array`             | `array`      |
| `object`            | `object`     |

## Changelog

| Version | Date        | Pull Request                                             | Subject                                           |
|:--------|:------------|:---------------------------------------------------------|:--------------------------------------------------|
| 0.1.0   | 2022-10-TBA | [18522](https://github.com/airbytehq/airbyte/pull/18593)   | New Source: Fastbill                                |