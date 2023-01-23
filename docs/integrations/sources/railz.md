# Recharge

This source can sync data for the [Recharge API](https://docs.railz.ai/).
This page guides you through the process of setting up the Recharge source connector.

## Prerequisites

- A Railz account with permission to access data from accounts you want to sync.
- Railz Client ID and Secret key

## Setup guide

### Step 1: Set up Railz

Generate API key [on the dashboard](https://dashboard.railz.ai/developers/api-keys) and take it's client_id and secret_key.

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account;
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
- [Bills Credit Notes](https://docs.railz.ai/reference/bill-creditnotes) \(Incremental sync\)
- [Bills Payments](https://docs.railz.ai/reference/getbillspayments) \(Incremental sync\)
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
- [Business Valuations](https://docs.railz.ai/reference/businessValuations) \(Incremental sync\)
- [Credit Scores](https://docs.railz.ai/reference/get-creditscores) \(Incremental sync\)
- [Credit Ratings](https://docs.railz.ai/reference/get-creditratings) \(Incremental sync\)
- [Financial Forecasts Month Balance Sheets](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Month Cashflow Statements](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Month Income Statements](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Quarter Balance Sheets](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Quarter Cashflow Statements](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Quarter Income Statements](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Year Balance Sheets](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Year Cashflow Statements](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Financial Forecasts Year Income Statements](https://docs.railz.ai/reference/get-financialforecasts) \(Incremental sync\)
- [Fraud Risk Metrics Month](https://docs.railz.ai/reference/financialfraudmetrics) \(Incremental sync\)
- [Fraud Risk Metrics Quarter](https://docs.railz.ai/reference/financialfraudmetrics) \(Incremental sync\)
- [Fraud Risk Metrics Year](https://docs.railz.ai/reference/financialfraudmetrics) \(Incremental sync\)
- [Financial Ratios Month](https://docs.railz.ai/reference/get-financialratios) \(Incremental sync\)
- [Financial Ratios Quarter](https://docs.railz.ai/reference/get-financialratios) \(Incremental sync\)
- [Financial Ratios Year](https://docs.railz.ai/reference/get-financialratios) \(Incremental sync\)
- [Portfolio Metrics](https://docs.railz.ai/reference/getportfoliometrics) \(Incremental sync\)
- [Probability Of Default](https://docs.railz.ai/reference/probabilityofdefaults) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Service support

Here is a table of streams service support (for those streams which provide data for services):

|                                                 | freshbooks   | quickbooks   | quickbooksDesktop   | xero   | oracleNetsuite   | sageBusinessCloud   | sageIntacct   | dynamicsBusinessCentral   | wave   | shopify   | square   | plaid   |
|:------------------------------------------------|:-------------|:-------------|:--------------------|:-------|:-----------------|:--------------------|:--------------|:--------------------------|:-------|:----------|:---------|:--------|
| customers                                       | True         | True         | True                | True   | True             | True                | True          | True                      | True   | False     | False    | False   |
| accounts                                        | True         | True         | True                | True   | True             | True                | True          | True                      | True   | False     | False    | False   |
| inventory                                       | True         | True         | True                | True   | True             | True                | True          | True                      | True   | False     | False    | False   |
| tax_rates                                       | True         | True         | True                | True   | True             | False               | True          | True                      | True   | False     | False    | False   |
| tracking_categories                             | True         | True         | True                | True   | True             | False               | True          | False                     | False  | False     | False    | False   |
| vendors                                         | True         | True         | True                | True   | True             | True                | True          | True                      | True   | False     | False    | False   |
| bank_accounts                                   | False        | False        | False               | False  | False            | False               | False         | False                     | False  | True      | False    | True    |
| accounting_transactions                         | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| bank_transfers                                  | False        | False        | False               | True   | False            | False               | False         | False                     | False  | False     | False    | False   |
| bills                                           | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| bills_credit_notes                              | False        | True         | False               | True   | True             | False               | True          | False                     | False  | False     | False    | False   |
| bills_payments                                  | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| deposits                                        | False        | True         | False               | True   | False            | False               | False         | False                     | False  | False     | False    | False   |
| estimates                                       | True         | True         | False               | True   | False            | False               | False         | False                     | False  | False     | False    | False   |
| invoices                                        | True         | True         | True                | True   | True             | True                | True          | True                      | True   | False     | False    | False   |
| invoices_credit_notes                           | True         | True         | False               | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| invoices_payments                               | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| journal_entries                                 | True         | True         | True                | True   | True             | True                | True          | False                     | False  | False     | False    | False   |
| purchase_orders                                 | False        | True         | False               | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| refunds                                         | False        | True         | False               | True   | False            | False               | False         | False                     | False  | False     | False    | False   |
| bank_transactions                               | False        | False        | False               | False  | False            | False               | False         | False                     | False  | False     | False    | True    |
| commerce_disputes                               | False        | False        | False               | False  | False            | False               | False         | False                     | False  | True      | True     | False   |
| commerce_orders                                 | False        | False        | False               | False  | False            | False               | False         | False                     | False  | True      | True     | False   |
| commerce_products                               | False        | False        | False               | False  | False            | False               | False         | False                     | False  | True      | True     | False   |
| commerce_transactions                           | False        | False        | False               | False  | False            | False               | False         | False                     | False  | True      | True     | False   |
| business_valuations                             | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| credit_ratings                                  | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| credit_scores                                   | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| probability_of_default                          | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| ap_aging_month                                  | True         | True         | True                | False  | False            | False               | False         | True                      | False  | False     | False    | False   |
| ar_aging_month                                  | True         | True         | True                | False  | False            | False               | True          | True                      | False  | False     | False    | False   |
| balance_sheets_month                            | True         | True         | True                | True   | False            | False               | False         | True                      | False  | False     | False    | False   |
| cashflow_statements_month                       | False        | True         | False               | False  | False            | False               | False         | True                      | False  | False     | False    | False   |
| income_statements_month                         | True         | True         | True                | True   | False            | False               | False         | True                      | False  | False     | False    | False   |
| trial_balances_month                            | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| fraud_risk_metrics_month                        | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_ratios_month                          | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_month_balance_sheets        | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_month_income_statements     | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_month_cashflow_statements   | True         | True         | True                | True   | True             | False               | True          | True                      | False  | True      | False    | False   |
| ap_aging_quarter                                | True         | True         | True                | False  | False            | False               | False         | True                      | False  | False     | False    | False   |
| ar_aging_quarter                                | True         | True         | True                | False  | False            | False               | True          | True                      | False  | False     | False    | False   |
| balance_sheets_quarter                          | True         | True         | True                | True   | False            | False               | False         | True                      | False  | False     | False    | False   |
| cashflow_statements_quarter                     | False        | True         | False               | False  | False            | False               | False         | True                      | False  | False     | False    | False   |
| income_statements_quarter                       | True         | True         | True                | True   | False            | False               | False         | True                      | False  | False     | False    | False   |
| trial_balances_quarter                          | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| fraud_risk_metrics_quarter                      | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_ratios_quarter                        | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_quarter_balance_sheets      | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_quarter_income_statements   | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_quarter_cashflow_statements | True         | True         | True                | True   | True             | False               | True          | True                      | False  | True      | False    | False   |
| ap_aging_year                                   | True         | True         | True                | False  | False            | False               | False         | True                      | False  | False     | False    | False   |
| ar_aging_year                                   | True         | True         | True                | False  | False            | False               | True          | True                      | False  | False     | False    | False   |
| balance_sheets_year                             | True         | True         | True                | True   | False            | False               | False         | True                      | False  | False     | False    | False   |
| cashflow_statements_year                        | False        | True         | False               | False  | False            | False               | False         | True                      | False  | False     | False    | False   |
| income_statements_year                          | True         | True         | True                | True   | False            | False               | False         | True                      | False  | False     | False    | False   |
| trial_balances_year                             | True         | True         | True                | True   | True             | True                | True          | True                      | False  | False     | False    | False   |
| fraud_risk_metrics_year                         | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_ratios_year                           | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_year_balance_sheets         | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_year_income_statements      | True         | True         | True                | True   | True             | False               | True          | True                      | False  | False     | False    | False   |
| financial_forecasts_year_cashflow_statements    | True         | True         | True                | True   | True             | False               | True          | True                      | False  | True      | False    | False   |

Some of services marked as supported by stream may not return any data. [Here](https://docs.railz.ai/docs/supported-integrations) is more information of services support.
Also you can check supported services by endpoint or vise versa on this [dataType API](https://docs.railz.ai/reference/datatypes)

### Performance considerations

The Railz connector should gracefully handle Railz API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|:--------|:-----------| :------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| 0.1.0   | 2023-01-23 | [20960](https://github.com/airbytehq/airbyte/pull/20960) | New Source: Railz                                                                         |
