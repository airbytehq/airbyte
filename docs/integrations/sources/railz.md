# Railz

This source can sync data for the [Railz API](https://docs.railz.ai/).
This page guides you through the process of setting up the Railz source connector.

## Prerequisites

- A Railz account with permission to access data from accounts you want to sync.
- Railz Client ID and Secret key

## Setup guide

### Step 1: Set up Railz

Generate API key [on the dashboard](https://dashboard.railz.ai/developers/api-keys) and take it's client_id and secret_key.

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account;
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**;
3. On the source setup page, select **Railz** from the Source type dropdown and enter a name for this connector;
4. Enter `Client ID (client_id)`;
5. Enter `Secret key (secret_key)`;
6. Enter `Start date` (optional);
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page;
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**;
3. On the source setup page, select **Railz** from the Source type dropdown and enter a name for this connector;
4. Enter `Client ID (client_id)`;
5. Enter `Secret key (secret_key)`;
6. Enter `Start date`;
7. click `Set up source`.
<!-- /env:oss -->

## Supported sync modes

The Railz supports full refresh and incremental sync.

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

## Supported Streams

Several output streams are available from this source:

- [Businesses](https://docs.railz.ai/reference/get-businesses)
- [Connections](https://docs.railz.ai/reference/getconnections)
- [Customers](https://docs.railz.ai/reference/getcustomers)
- [Accounts](https://docs.railz.ai/reference/getaccounts)
- [Inventory](https://docs.railz.ai/reference/getinventory)
- [Tax Rates](https://docs.railz.ai/reference/gettaxrates)
- [Tracking Categories](https://docs.railz.ai/reference/get-trackingcategories)
- [Vendors](https://docs.railz.ai/reference/getvendors)
- [Bank Accounts](https://docs.railz.ai/reference/get-bankaccounts)
- [Accounting Transactions](https://docs.railz.ai/reference/get-accountingtransactions) \(Incremental sync\)
- [Bank Transfers](https://docs.railz.ai/reference/get-banktransfers) \(Incremental sync\)
- [Bills](https://docs.railz.ai/reference/getbills) \(Incremental sync\)
- [Bills Credit Notes](https://docs.railz.ai/reference/bill-creditnotes) \(Incremental sync\)
- [Bills Payments](https://docs.railz.ai/reference/getbillspayments) \(Incremental sync\)
- [Deposits](https://docs.railz.ai/reference/get-deposits) \(Incremental sync\)
- [Estimates](https://docs.railz.ai/reference/get-estimates) \(Incremental sync\)
- [Invoices](https://docs.railz.ai/reference/getinvoices) \(Incremental sync\)
- [Invoices Credit Notes](https://docs.railz.ai/reference/get-invoice-creditnotes) \(Incremental sync\)
- [Invoices Payments](https://docs.railz.ai/reference/getinvoicespayments) \(Incremental sync\)
- [Journal Entries](https://docs.railz.ai/reference/get-journalentries) \(Incremental sync\)
- [Purchase Orders](https://docs.railz.ai/reference/get-purchaseorder) \(Incremental sync\)
- [Refunds](https://docs.railz.ai/reference/get-refund) \(Incremental sync\)
- [Commerce Disputes](https://docs.railz.ai/reference/dispute) \(Incremental sync\)
- [Commerce Orders](https://docs.railz.ai/reference/order) \(Incremental sync\)
- [Commerce Products](https://docs.railz.ai/reference/product) \(Incremental sync\)
- [Commerce Transactions](https://docs.railz.ai/reference/transactions) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Performance considerations

The Railz connector should gracefully handle Railz API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject           |
| :------ | :--------- | :------------------------------------------------------- | :---------------- |
| 0.1.17 | 2024-10-12 | [46786](https://github.com/airbytehq/airbyte/pull/46786) | Update dependencies |
| 0.1.16 | 2024-10-05 | [46462](https://github.com/airbytehq/airbyte/pull/46462) | Update dependencies |
| 0.1.15 | 2024-09-28 | [46182](https://github.com/airbytehq/airbyte/pull/46182) | Update dependencies |
| 0.1.14 | 2024-09-21 | [45811](https://github.com/airbytehq/airbyte/pull/45811) | Update dependencies |
| 0.1.13 | 2024-09-14 | [45576](https://github.com/airbytehq/airbyte/pull/45576) | Update dependencies |
| 0.1.12 | 2024-09-07 | [45317](https://github.com/airbytehq/airbyte/pull/45317) | Update dependencies |
| 0.1.11 | 2024-08-31 | [45036](https://github.com/airbytehq/airbyte/pull/45036) | Update dependencies |
| 0.1.10 | 2024-08-24 | [44649](https://github.com/airbytehq/airbyte/pull/44649) | Update dependencies |
| 0.1.9 | 2024-08-17 | [44206](https://github.com/airbytehq/airbyte/pull/44206) | Update dependencies |
| 0.1.8 | 2024-08-12 | [43801](https://github.com/airbytehq/airbyte/pull/43801) | Update dependencies |
| 0.1.7 | 2024-08-10 | [43541](https://github.com/airbytehq/airbyte/pull/43541) | Update dependencies |
| 0.1.6 | 2024-08-03 | [43288](https://github.com/airbytehq/airbyte/pull/43288) | Update dependencies |
| 0.1.5 | 2024-07-27 | [42674](https://github.com/airbytehq/airbyte/pull/42674) | Update dependencies |
| 0.1.4 | 2024-07-20 | [40029](https://github.com/airbytehq/airbyte/pull/40029) | Update dependencies |
| 0.1.3 | 2024-07-19 | [42125](https://github.com/airbytehq/airbyte/pull/42125) | Fix Python MRO bug |
| 0.1.2 | 2024-05-21 | [38545](https://github.com/airbytehq/airbyte/pull/38545) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-02-16 | [20960](https://github.com/airbytehq/airbyte/pull/20960) | New Source: Railz |

</details>
