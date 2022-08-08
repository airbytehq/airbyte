# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

See [docs](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/) for more details.

## Setup guide
### Step 1: Set up Harvest

This connector supports only authentication with API Key. To obtain API key follow the instructions below:

1. Go to Account Settings page;
2. Under Integrations section press Authorized OAuth2 API Clients button;
3. New page will be opened on which you need to click on Create New Personal Access Token button and follow instructions.

## Step 2: Set up the Harvest connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Harvest connector and select **Harvest** from the Source type dropdown.
4. For Airbyte Cloud, click **Authenticate your Harvest account** to sign in with Harvest and authorize your account.
5. Enter your `account_id` 
6. Enter the `replication_start_date` you want your sync to start from
7. Click **Set up source**

### For Airbyte OSS:
1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `api_token`
4. Enter your `account_id` 
5. Enter the `replication_start_date` you want your sync to start from
6. Click **Set up source**

## Supported sync modes

The Harvest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |


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

The Harvest connector will gracefully handle rate limits. For more information, see [the Harvest docs for rate limitations](https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.10 | 2022-08-08 | [15221](https://github.com/airbytehq/airbyte/pull/15221) | Added `parent_id` for all streams which have parent stream |
| 0.1.9 | 2022-08-04 | [15312](https://github.com/airbytehq/airbyte/pull/15312) | Fix `started_time` and `ended_time` format schema error and updated report slicing |
| 0.1.8 | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Update titles and descriptions |
| 0.1.6 | 2021-11-14 | [7952](https://github.com/airbytehq/airbyte/pull/7952) | Implement OAuth 2.0 support |
| 0.1.5 | 2021-09-28 | [5747](https://github.com/airbytehq/airbyte/pull/5747) | Update schema date-time fields |
| 0.1.4 | 2021-06-22 | [5701](https://github.com/airbytehq/airbyte/pull/5071) | Harvest normalization failure: fixing the schemas |
| 0.1.3 | 2021-06-22 | [4274](https://github.com/airbytehq/airbyte/pull/4274) | Fix wrong data type on `statement_key` in `clients` stream |
| 0.1.2 | 2021-06-07 | [4222](https://github.com/airbytehq/airbyte/pull/4222) | Correct specification parameter name |
| 0.1.1 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.0 | 2021-06-07 | [3709](https://github.com/airbytehq/airbyte/pull/3709) | Release Harvest connector! |
