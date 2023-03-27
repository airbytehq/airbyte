# Fortnox

This page contains the setup guide and reference information for the Fortnox source connector.

Fortnox is a Swedish ERP vendor

## Prerequisites

This Fortnox source uses the [Fortnox API](https://apps.fortnox.se/apidocs) to get data.

For more information around the API, authentication et.c. please see
the [Developer Documentation](https://developer.fortnox.se/)

## Setup guide

### Step 1: Set up Fortnox

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Enter a name for your source
3. Configuration needed for the authentication:
    1. client_id -- Needed to refresh access token
    2. client_secret -- Needed to refresh access token
    3. refresh_token -- Initial refresh token that have been issued by a user in the fortnox tenant with Sysadmin
       privileges
    4. access_token -- Initially this can be set to a dummy-value, when the first refresh is made this will be replaced
    5. token_expiry_date -- Initially this should be set to a date in the past to force an initial refresh.
6. Click **Set up source**

## Supported sync modes

The Fortnox source connector supports the
following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
|:------------------------------|:-----------|
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

| Name                                                                              | Incremental? | Note                                                           |
|:----------------------------------------------------------------------------------|:-------------|:---------------------------------------------------------------|
| [Accounts](https://apps.fortnox.se/apidocs#operation/list_AccountsResource)       | Yes          |                                                                |
| [CostCenters](https://apps.fortnox.se/apidocs#operation/list_CostCentersResource) | Yes          |                                                                |
| [Customers](https://apps.fortnox.se/apidocs#operation/list_CustomersResource)     | Yes          | Incremental is undocumented but seem to work                   |
| [FinancialYears](https://apps.fortnox.se/apidocs#operation/getByDate)             | No           |                                                                |
| [Invoices](https://apps.fortnox.se/apidocs#operation/list_InvoicesResource)       | Yes          | Incremental is undocumented but seem to work                   |
| [Projects](https://apps.fortnox.se/apidocs#operation/list_ProjectsResource)       | Yes          | Incremental is undocumented but seem to work                   |
| [Vouchers](https://apps.fortnox.se/apidocs#operation/list_VouchersResource)       | Yes          |                                                                |
| [VoucherDetails](https://apps.fortnox.se/apidocs#operation/get_VouchersResource)  | Yes          | Many request are being sent, incremental mode strongly advised |

## Changelog

| Version | Date       | Pull Request                                             | Subject                             |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------|
| 0.1.0   | 2023-04-26 | [25556](https://github.com/airbytehq/airbyte/pull/25556) | 🎉 New Source: Fortnox [python cdk] |
