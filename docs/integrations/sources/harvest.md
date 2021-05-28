# Harvest

## Overview

The Hubspot connector can be used to sync your Harvest data. It supports full refresh sync for all streams and incremental sync for all streams except of Expense Reports streams which are: Clients Report, Projects Report, Categories Report, Team Report.
Incremental sync is also now available for Company stream, but it always has only one record.

### Output schema

Several output streams are available from this source:

* [Client Contacts](https://help.getharvest.com/api-v2/clients-api/clients/contacts/)
* [Clients](https://help.getharvest.com/api-v2/clients-api/clients/clients/)
* [Company](https://help.getharvest.com/api-v2/company-api/company/company/)
* [Invoice Messages](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-messages/)
* [Invoice Payments](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-payments/)
* [Invoices](https://help.getharvest.com/api-v2/invoices-api/invoices/invoices/)
* [Invoice Item Categories](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-item-categories/)
* [Estimate Messages](https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-messages/)
* [Estimates](https://help.getharvest.com/api-v2/estimates-api/estimates/estimates/)
* [Estimate Item Categories](https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-item-categories/)
* [Expenses](https://help.getharvest.com/api-v2/expenses-api/expenses/expenses/)
* [Expense Categories](https://help.getharvest.com/api-v2/expenses-api/expenses/expense-categories/)
* [Tasks](https://help.getharvest.com/api-v2/tasks-api/tasks/tasks/)
* [Time Entries](https://help.getharvest.com/api-v2/timesheets-api/timesheets/time-entries/)
* [Project User Assignments](https://help.getharvest.com/api-v2/projects-api/projects/user-assignments/)
* [Project Task Assignments](https://help.getharvest.com/api-v2/projects-api/projects/task-assignments/)
* [Projects](https://help.getharvest.com/api-v2/projects-api/projects/projects/)
* [Roles](https://help.getharvest.com/api-v2/roles-api/roles/roles/)
* [User Billable Rates](https://help.getharvest.com/api-v2/users-api/users/billable-rates/)
* [User Cost Rates](https://help.getharvest.com/api-v2/users-api/users/cost-rates/)
* [User Project Assignments](https://help.getharvest.com/api-v2/users-api/users/project-assignments/)
* [Expense Reports](https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/)
* [Uninvoiced Report](https://help.getharvest.com/api-v2/reports-api/reports/uninvoiced-report/)
* [Time Reports](https://help.getharvest.com/api-v2/reports-api/reports/time-reports/)
* [Project Budget Report](https://help.getharvest.com/api-v2/reports-api/reports/project-budget-report/)


### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

Harvest connector has rate limitations. See [rate limitations](https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting) docs.

## Getting started

### Requirements

* Harvest Account
* Harvest Authorized OAuth2 API Client to create Access Token and get account ID

### Setup guide

This connector supports only authentication with API Key. To obtain API key follow the instructions below:

1. Go to Account Settings page (login/password are in LastPass);
1. Under Integrations section press Authorized OAuth2 API Clients button;
1. New page will be opened on which you need to click on Create New Personal Access Token button and follow instructions.

See [docs](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/) for more details.