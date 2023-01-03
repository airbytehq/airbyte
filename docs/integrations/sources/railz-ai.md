# Recharge

This source can sync data for the [Recharge API](https://docs.railz.ai/).
This page guides you through the process of setting up the Recharge source connector.

## Prerequisites

- A Railz.ai account with permission to access data from accounts you want to sync.
- Railz.ai Client ID and Secret key

## Setup guide

### Step 1: Set up Railz.ai

Generate API key [on the dashboard](https://dashboard.railz.ai/developers/api-keys) and take it's client_id and secret_key.

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account;
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**;
3. On the source setup page, select **Railz.ai** from the Source type dropdown and enter a name for this connector;
4. Enter `Client ID (client_id)`;
5. Enter `Secret key (secret_key)`;
6. Enter `Start date` (optional);
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page;
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**;
3. On the source setup page, select **Railz.ai** from the Source type dropdown and enter a name for this connector;
4. Enter `Client ID (client_id)`;
5. Enter `Secret key (secret_key)`;
6. Enter `Start date` (optional);
7. click `Set up source`.
<!-- /env:oss -->

## Supported sync modes

The Recharge supports full refresh and incremental sync.

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

## Supported Streams

Several output streams are available from this source:

- [Businesses](https://docs.railz.ai/reference/get-businesses)
- [Connections](https://docs.railz.ai/reference/getconnections)
- [Accounting Transactions](https://docs.railz.ai/reference/get-accountingtransactions) \(Incremental sync\)
- [Ap Aging Month (Aging Reports / Aged Payable)](https://docs.railz.ai/reference/get-apaging) \(Incremental sync\)
- [Ap Aging Quarter (Aging Reports / Aged Payable)](https://docs.railz.ai/reference/get-apaging) \(Incremental sync\)
- [Ap Aging Year (Aging Reports / Aged Payable)](https://docs.railz.ai/reference/get-apaging) \(Incremental sync\)
- [Ar Aging Month (Aging Reports / Aged Receivable)](https://docs.railz.ai/reference/get-araging) \(Incremental sync\)
- [Ar Aging Quarter (Aging Reports / Aged Receivable)](https://docs.railz.ai/reference/get-araging) \(Incremental sync\)
- [Ar Aging Year (Aging Reports / Aged Receivable)](https://docs.railz.ai/reference/get-araging) \(Incremental sync\)
- [Bank Transfers](https://docs.railz.ai/reference/get-banktransfers) \(Incremental sync\)
- [Bills](https://docs.railz.ai/reference/getbills) \(Incremental sync\)
- [Bill Credit Notes](https://docs.railz.ai/reference/bill-creditnotes) \(Incremental sync\)
- [Bill Payments](https://docs.railz.ai/reference/getbillspayments) \(Incremental sync\)
- [Accounts](https://docs.railz.ai/reference/getaccounts)
- [Customers](https://docs.railz.ai/reference/getcustomers)
- [Deposits](https://docs.railz.ai/reference/get-deposits) \(Incremental sync\)
- [Estimates](https://docs.railz.ai/reference/get-estimates) \(Incremental sync\)
- [Balance Sheets Month (Financial Statements)](https://docs.railz.ai/reference/getbalancesheets) \(Incremental sync\)
- [Balance Sheets Quarter (Financial Statements)](https://docs.railz.ai/reference/getbalancesheets) \(Incremental sync\)
- [Balance Sheets Year (Financial Statements)](https://docs.railz.ai/reference/getbalancesheets) \(Incremental sync\)
- [Cashflow Statements Month (Financial Statements)](https://docs.railz.ai/reference/getcashflowstatements) \(Incremental sync\)
- [Cashflow Statements Quarter (Financial Statements)](https://docs.railz.ai/reference/getcashflowstatements) \(Incremental sync\)
- [Cashflow Statements Year (Financial Statements)](https://docs.railz.ai/reference/getcashflowstatements) \(Incremental sync\)
- [Income Statements Month (Financial Statements)](https://docs.railz.ai/reference/getincomestatements) \(Incremental sync\)
- [Income Statements Quarter (Financial Statements)](https://docs.railz.ai/reference/getincomestatements) \(Incremental sync\)
- [Income Statements Year (Financial Statements)](https://docs.railz.ai/reference/getincomestatements) \(Incremental sync\)
- [Inventory](https://docs.railz.ai/reference/getinventory)
- [Invoices](https://docs.railz.ai/reference/getinvoices) \(Incremental sync\)
- [Invoices Credit Notes](https://docs.railz.ai/reference/get-invoice-creditnotes) \(Incremental sync\)
- [Invoices Payments](https://docs.railz.ai/reference/getinvoicespayments) \(Incremental sync\)
- [Journal Entries](https://docs.railz.ai/reference/get-journalentries) \(Incremental sync\)
- [Purchase Orders](https://docs.railz.ai/reference/get-purchaseorder) \(Incremental sync\)
- [Refunds](https://docs.railz.ai/reference/get-refund) \(Incremental sync\)
- [Tax Rates](https://docs.railz.ai/reference/gettaxrates)
- [Tracking Categories](https://docs.railz.ai/reference/get-trackingcategories)
- [Trial Balances Month](https://docs.railz.ai/reference/gettrialbalances) \(Incremental sync\)
- [Trial Balances Quarter](https://docs.railz.ai/reference/gettrialbalances) \(Incremental sync\)
- [Trial Balances Year](https://docs.railz.ai/reference/gettrialbalances) \(Incremental sync\)
- [Vendors](https://docs.railz.ai/reference/getvendors)
- [Bank Accounts](https://docs.railz.ai/reference/get-bankaccounts)
- [Bank Transactions](https://docs.railz.ai/reference/get-banktransactions) \(Incremental sync\)
- [Commerce Disputes](https://docs.railz.ai/reference/dispute) \(Incremental sync\)
- [Commerce Orders](https://docs.railz.ai/reference/order) \(Incremental sync\)
- [Commerce Products](https://docs.railz.ai/reference/product) \(Incremental sync\)
- [Commerce Transactions](https://docs.railz.ai/reference/transactions) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Performance considerations

The Railz.ai connector should gracefully handle Railz.ai API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|:--------|:-----------| :------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| 0.1.0   | 2023-01-03 | [20960](https://github.com/airbytehq/airbyte/pull/20960) | DNew Source: Railz.ai                                                       |