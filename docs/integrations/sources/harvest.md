# Harvest

This page contains the setup guide and reference information for the Harvest source connector.

## Prerequisites

To set up the Harvest source connector, you'll need the [Harvest Account ID and API key](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces).
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your [Harvest Account ID](https://id.getharvest.com/developers), which can be found in the _Developers_ page on the Harvest website.
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For Authentication mechanism, select **Authenticate via Harvest (OAuth)** from the dropdown and click **Authenticate your Harvest account**. Log in and authorize your Harvest account.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Harvest** from the Source type dropdown.
4. Enter the name for the Harvest connector.
5. Enter your [Harvest Account ID](https://id.getharvest.com/developers), which can be found in the _Developers_ page on the Harvest website.
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For **Authentication mechanism**, select **Authenticate with Personal Access Token** from the dropdown. Enter your [Personal Access Token](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens) which can be obtained by logging into your Harvest account and creating a new token on the _Developers_ page.
8. Click **Set up source**.
<!-- /env:oss -->

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