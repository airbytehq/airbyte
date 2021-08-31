# Harvest

## Overview

The Harvest connector can be used to sync your Harvest data. It supports full refresh sync for all streams and incremental sync for all streams except of Expense Reports streams which are: Clients Report, Projects Report, Categories Report, Team Report.
Incremental sync is also now available for Company stream, but it always has only one record.

### Output schema

Several output streams are available from this source:

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


### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Harvest connector will gracefully handle rate limits. For more information, see [the Harvest docs for rate limitations](https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting).

## Getting started

### Requirements

* Harvest Account
* Harvest Authorized OAuth2 API Client to create Access Token and get account ID

### Setup guide

This connector supports only authentication with API Key. To obtain API key follow the instructions below:

1. Go to Account Settings page;
1. Under Integrations section press Authorized OAuth2 API Clients button;
1. New page will be opened on which you need to click on Create New Personal Access Token button and follow instructions.

See [docs](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/) for more details.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.4   | 2021-06-22 | [5701](https://github.com/airbytehq/airbyte/pull/5071) | Harvest normalization failure: fixing the schemas |
| 0.1.3   | 2021-06-22 | [4274](https://github.com/airbytehq/airbyte/pull/4274) | Fix wrong data type on `statement_key` in `clients` stream |
| 0.1.2   | 2021-06-07 | [4222](https://github.com/airbytehq/airbyte/pull/4222) | Correct specification parameter name |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.0   | 2021-06-07 | [3709](https://github.com/airbytehq/airbyte/pull/3709) | Release Harvest connector! |