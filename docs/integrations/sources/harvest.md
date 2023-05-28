# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

To set up the Harvest source connector, you'll need the [Harvest Account ID and API key](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).

## Setup Guide

To set up the Harvest source connector in Airbyte, follow the steps below:

### Step 1: Account ID

1. Obtain the `Account ID` from your Harvest account. The Account ID is required for all Harvest requests in pair with Personal Access Token.
2. To find your `Account ID`, log in to your [Harvest](https://id.getharvest.com) account.
3. Click on your profile picture in the top-right corner and select **Account Settings** from the dropdown menu.
4. In the Account Settings page, copy the `Account ID` found under the **Company information** section.
5. In the Airbyte configuration form, paste the `Account ID` in the `Account ID` field.

### Step 2: Start Date

Enter the date in the `Start Date` field in the UTC date and time format YYYY-MM-DDTHH:mm:ssZ. Data added on and after this date will be replicated.

### Step 3: Authentication Mechanism

Choose an authentication method: either OAuth or Personal Access Token.

#### Authenticate via Harvest (OAuth)

1. To use OAuth, you need to register a new developer application to generate your `Client ID` and `Client Secret`. Visit the [Create new OAuth application](https://id.getharvest.com/oauth2/applications/new) page and fill in the required fields.
2. After creating the application, you’ll be redirected to the applications list. Click the name of the new application to see its `Client ID` and `Client Secret.`
3. In the Airbyte configuration form, choose "Authenticate via Harvest (OAuth)" from the `Authentication Mechanism` dropdown.
4. Enter the `Client ID` and `Client Secret` in their respective fields.
5. Click the "Authenticate your Harvest account" button, log in to your Harvest account, and authorize your Harvest application.

#### Authenticate with Personal Access Token

1. To generate a Personal Access Token, log into your [Harvest](https://id.getharvest.com) account.
2. Click on your profile picture in the top-right corner and select **Developer** from the dropdown menu.
3. Click the "Create New Personal Access Token" button and specify a description for your token.
4. Copy the generated token from the **API Token** field.
5. In the Airbyte configuration form, choose "Authenticate with Personal Access Token" from the `Authentication Mechanism` dropdown.
6. Enter the `Personal Access Token` in the `API Token` field.

After completing these steps, click the "Set up source" button to finish setting up the Harvest source connector in Airbyte.

For additional information about Harvest authentication, check the Harvest documentation on [authentication](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).

## Supported sync modes

The Harvest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

* [Client Contacts](https://help.getharvest.com/api-v2/clients-api/clients/contacts/) \(Incremental\)
* [Clients](https://help.getharvest.com/api-v2/clients-api/clients/clients/) \(Incremental\)
* [Company](https://help.getharvest.com/api-v2/company-api/company/company/)
* [Invoice Messages](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-messages/) \(Incremental\)
* [Invoice Payments](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-payments/) \(Incremental\)
* [Invoices](https://help.getharvest.com/api-v2/invoices-api/invoices/invoices/) \(Incremental\)
* [Invoice Item Categories](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-item-categories/) \(Incremental\)
* [Estimate Messages](https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-messages/) \(Incremental\)
* [Estimates](https://help.getharvest.com/api-v2/estimates-api/estimates/estimates/) \(Incremental\)
* [Estimate Item Categories](https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-item-categories/) \(Incremental\)
* [Expenses](https://help.getharvest.com/api-v2/expenses-api/expenses/expenses/) \(Incremental\)
* [Expense Categories](https://help.getharvest.com/api-v2/expenses-api/expenses/expense-categories/) \(Incremental\)
* [Tasks](https://help.getharvest.com/api-v2/tasks-api/tasks/tasks/) \(Incremental\)
* [Time Entries](https://help.getharvest.com/api-v2/timesheets-api/timesheets/time-entries/) \(Incremental\)
* [Project User Assignments](https://help.getharvest.com/api-v2/projects-api/projects/user-assignments/) \(Incremental\)
* [Project Task Assignments](https://help.getharvest.com/api-v2/projects-api/projects/task-assignments/) \(Incremental\)
* [Projects](https://help.getharvest.com/api-v2/projects-api/projects/projects/) \(Incremental\)
* [Roles](https://help.getharvest.com/api-v2/roles-api/roles/roles/) \(Incremental\)
* [User Billable Rates](https://help.getharvest.com/api-v2/users-api/users/billable-rates/)
* [User Cost Rates](https://help.getharvest.com/api-v2/users-api/users/cost-rates/)
* [User Project Assignments](https://help.getharvest.com/api-v2/users-api/users/project-assignments/) \(Incremental\)
* [Expense Reports](https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/)
* [Uninvoiced Report](https://help.getharvest.com/api-v2/reports-api/reports/uninvoiced-report/)
* [Time Reports](https://help.getharvest.com/api-v2/reports-api/reports/time-reports/)
* [Project Budget Report](https://help.getharvest.com/api-v2/reports-api/reports/project-budget-report/)

## Performance considerations

The connector is restricted by the [Harvest rate limits](https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                            |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------|
| 0.1.17  l 2023-03-03 | [22983](https://github.com/airbytehq/airbyte/pull/22983) | Specified date formatting in specification                        |
| 0.1.16  | 2023-02-07 | [22417](https://github.com/airbytehq/airbyte/pull/22417) | Turn on default HttpAvailabilityStrategy                                           |
| 0.1.15  | 2023-01-27 | [22008](https://github.com/airbytehq/airbyte/pull/22008) | Set `AvailabilityStrategy` for streams explicitly to `None`                        |
| 0.1.14  | 2023-01-09 | [21151](https://github.com/airbytehq/airbyte/pull/21151) | Skip 403 FORBIDDEN for all stream                                                  |
| 0.1.13  | 2022-12-22 | [20810](https://github.com/airbytehq/airbyte/pull/20810) | Skip 403 FORBIDDEN for `EstimateItemCategories` stream                             |
| 0.1.12  | 2022-12-16 | [20572](https://github.com/airbytehq/airbyte/pull/20572) | Introduce replication end date                                                     |
| 0.1.11  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                      |
| 0.1.10  | 2022-08-08 | [15221](https://github.com/airbytehq/airbyte/pull/15221) | Added `parent_id` for all streams which have parent stream                         |
| 0.1.9   | 2022-08-04 | [15312](https://github.com/airbytehq/airbyte/pull/15312) | Fix `started_time` and `ended_time` format schema error and updated report slicing |
| 0.1.8   | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions                                                     |
| 0.1.6   | 2021-11-14 | [7952](https://github.com/airbytehq/airbyte/pull/7952)   | Implement OAuth 2.0 support                                                        |
| 0.1.5   | 2021-09-28 | [5747](https://github.com/airbytehq/airbyte/pull/5747)   | Update schema date-time fields                                                     |
| 0.1.4   | 2021-06-22 | [5701](https://github.com/airbytehq/airbyte/pull/5071)   | Harvest normalization failure: fixing the schemas                                  |
| 0.1.3   | 2021-06-22 | [4274](https://github.com/airbytehq/airbyte/pull/4274)   | Fix wrong data type on `statement_key` in `clients` stream                         |
| 0.1.2   | 2021-06-07 | [4222](https://github.com/airbytehq/airbyte/pull/4222)   | Correct specification parameter name                                               |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                    |
| 0.1.0   | 2021-06-07 | [3709](https://github.com/airbytehq/airbyte/pull/3709)   | Release Harvest connector!                                                         |
