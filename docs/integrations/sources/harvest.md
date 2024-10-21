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
5. Enter your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).
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
5. Enter your [Harvest Account ID](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. For **Authentication mechanism**, select **Authenticate with Personal Access Token** from the dropdown. Enter your [Personal Access Token](https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/#personal-access-tokens).
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Harvest source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Client Contacts](https://help.getharvest.com/api-v2/clients-api/clients/contacts/) \(Incremental\)
- [Clients](https://help.getharvest.com/api-v2/clients-api/clients/clients/) \(Incremental\)
- [Company](https://help.getharvest.com/api-v2/company-api/company/company/)
- [Invoice Messages](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-messages/) \(Incremental\)
- [Invoice Payments](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-payments/) \(Incremental\)
- [Invoices](https://help.getharvest.com/api-v2/invoices-api/invoices/invoices/) \(Incremental\)
- [Invoice Item Categories](https://help.getharvest.com/api-v2/invoices-api/invoices/invoice-item-categories/) \(Incremental\)
- [Estimate Messages](https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-messages/) \(Incremental\)
- [Estimates](https://help.getharvest.com/api-v2/estimates-api/estimates/estimates/) \(Incremental\)
- [Estimate Item Categories](https://help.getharvest.com/api-v2/estimates-api/estimates/estimate-item-categories/) \(Incremental\)
- [Expenses](https://help.getharvest.com/api-v2/expenses-api/expenses/expenses/) \(Incremental\)
- [Expense Categories](https://help.getharvest.com/api-v2/expenses-api/expenses/expense-categories/) \(Incremental\)
- [Tasks](https://help.getharvest.com/api-v2/tasks-api/tasks/tasks/) \(Incremental\)
- [Time Entries](https://help.getharvest.com/api-v2/timesheets-api/timesheets/time-entries/) \(Incremental\)
- [Project User Assignments](https://help.getharvest.com/api-v2/projects-api/projects/user-assignments/) \(Incremental\)
- [Project Task Assignments](https://help.getharvest.com/api-v2/projects-api/projects/task-assignments/) \(Incremental\)
- [Projects](https://help.getharvest.com/api-v2/projects-api/projects/projects/) \(Incremental\)
- [Roles](https://help.getharvest.com/api-v2/roles-api/roles/roles/) \(Incremental\)
- [Users](https://help.getharvest.com/api-v2/users-api/users/users/) \(Incremental\)
- [User Billable Rates](https://help.getharvest.com/api-v2/users-api/users/billable-rates/)
- [User Cost Rates](https://help.getharvest.com/api-v2/users-api/users/cost-rates/)
- [User Project Assignments](https://help.getharvest.com/api-v2/users-api/users/project-assignments/) \(Incremental\)
- [Expense Clients Report](https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#clients-report) \(Incremental\)
- [Expense Projects Report](https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#projects-report) \(Incremental\)
- [Expense Categories Report](https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#expense-categories-report) \(Incremental\)
- [Expense Team Report](https://help.getharvest.com/api-v2/reports-api/reports/expense-reports/#team-report) \(Incremental\)
- [Uninvoiced Report](https://help.getharvest.com/api-v2/reports-api/reports/uninvoiced-report/) \(Incremental\)
- [Time Clients Report](https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#clients-report) \(Incremental\)
- [Time Projects Report](https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#projects-report) \(Incremental\)
- [Time Tasks Report](https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#tasks-report) \(Incremental\)
- [Time Team Report](https://help.getharvest.com/api-v2/reports-api/reports/time-reports/#team-report) \(Incremental\)
- [Project Budget Report](https://help.getharvest.com/api-v2/reports-api/reports/project-budget-report/)

## Performance considerations

The connector is restricted by the [Harvest rate limits](https://help.getharvest.com/api-v2/introduction/overview/general/#rate-limiting).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                           |
|:--------| :--------- | :------------------------------------------------------- |:----------------------------------------------------------------------------------------------------------------------------------|
| 1.1.0 | 2024-10-14 | [46898](https://github.com/airbytehq/airbyte/pull/46898) | Promoting release candidate 1.1.0-rc1 to a main version. |
| 1.1.0-rc1  | 2024-10-09 | [46685](https://github.com/airbytehq/airbyte/pull/46685) | Migrate to Manifest-only |
| 1.0.19 | 2024-10-05 | [46470](https://github.com/airbytehq/airbyte/pull/46470) | Update dependencies |
| 1.0.18 | 2024-09-28 | [46143](https://github.com/airbytehq/airbyte/pull/46143) | Update dependencies |
| 1.0.17 | 2024-09-21 | [45835](https://github.com/airbytehq/airbyte/pull/45835) | Update dependencies |
| 1.0.16 | 2024-09-14 | [45537](https://github.com/airbytehq/airbyte/pull/45537) | Update dependencies |
| 1.0.15 | 2024-09-07 | [44986](https://github.com/airbytehq/airbyte/pull/44986) | Update dependencies |
| 1.0.14 | 2024-08-24 | [44681](https://github.com/airbytehq/airbyte/pull/44681) | Update dependencies |
| 1.0.13 | 2024-08-17 | [44263](https://github.com/airbytehq/airbyte/pull/44263) | Update dependencies |
| 1.0.12 | 2024-08-10 | [43463](https://github.com/airbytehq/airbyte/pull/43463) | Update dependencies |
| 1.0.11 | 2024-08-03 | [43123](https://github.com/airbytehq/airbyte/pull/43123) | Update dependencies |
| 1.0.10 | 2024-07-27 | [42831](https://github.com/airbytehq/airbyte/pull/42831) | Update dependencies |
| 1.0.9 | 2024-07-20 | [42326](https://github.com/airbytehq/airbyte/pull/42326) | Update dependencies |
| 1.0.8 | 2024-07-13 | [41841](https://github.com/airbytehq/airbyte/pull/41841) | Update dependencies |
| 1.0.7 | 2024-07-10 | [41381](https://github.com/airbytehq/airbyte/pull/41381) | Update dependencies |
| 1.0.6 | 2024-07-09 | [41303](https://github.com/airbytehq/airbyte/pull/41303) | Update dependencies |
| 1.0.5 | 2024-07-06 | [41002](https://github.com/airbytehq/airbyte/pull/41002) | Update dependencies |
| 1.0.4 | 2024-06-25 | [40475](https://github.com/airbytehq/airbyte/pull/40475) | Update dependencies |
| 1.0.3 | 2024-06-22 | [40169](https://github.com/airbytehq/airbyte/pull/40169) | Update dependencies |
| 1.0.2 | 2024-05-08 | [38055](https://github.com/airbytehq/airbyte/pull/38055) | Fix error handler for retriable errors |
| 1.0.1 | 2024-04-24 | [36641](https://github.com/airbytehq/airbyte/pull/36641) | Schema descriptions and CDK 0.80.0 |
| 1.0.0 | 2024-04-15 | [35863](https://github.com/airbytehq/airbyte/pull/35863) | Migrates connector to Low Code CDK, Updates incremental substream state to per-partition state |
| 0.2.0 | 2024-04-08 | [36889](https://github.com/airbytehq/airbyte/pull/36889) | Unpin CDK version |
| 0.1.24 | 2024-02-26 | [35541](https://github.com/airbytehq/airbyte/pull/35541) | Improve check command to avoid missing alerts |
| 0.1.23 | 2024-02-19 | [35305](https://github.com/airbytehq/airbyte/pull/35305) | Fix pendulum parsing error |
| 0.1.22 | 2024-02-12 | [35154](https://github.com/airbytehq/airbyte/pull/35154) | Manage dependencies with Poetry. |
| 0.1.21 | 2023-11-30 | [33003](https://github.com/airbytehq/airbyte/pull/33003) | Update expected records |
| 0.1.20 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.19 | 2023-07-26 | [28755](https://github.com/airbytehq/airbyte/pull/28755) | Changed parameters for Time Reports to use 365 days as opposed to 1 year |
| 0.1.18 | 2023-05-29 | [26714](https://github.com/airbytehq/airbyte/pull/26714) | Remove `authSpecification` from spec in favour of `advancedAuth` |
| 0.1.17 | 2023-03-03 | [22983](https://github.com/airbytehq/airbyte/pull/22983) | Specified date formatting in specification |
| 0.1.16 | 2023-02-07 | [22417](https://github.com/airbytehq/airbyte/pull/22417) | Turn on default HttpAvailabilityStrategy |
| 0.1.15 | 2023-01-27 | [22008](https://github.com/airbytehq/airbyte/pull/22008) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.14 | 2023-01-09 | [21151](https://github.com/airbytehq/airbyte/pull/21151) | Skip 403 FORBIDDEN for all stream |
| 0.1.13 | 2022-12-22 | [20810](https://github.com/airbytehq/airbyte/pull/20810) | Skip 403 FORBIDDEN for `EstimateItemCategories` stream |
| 0.1.12 | 2022-12-16 | [20572](https://github.com/airbytehq/airbyte/pull/20572) | Introduce replication end date |
| 0.1.11 | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states. |
| 0.1.10 | 2022-08-08 | [15221](https://github.com/airbytehq/airbyte/pull/15221) | Added `parent_id` for all streams which have parent stream |
| 0.1.9 | 2022-08-04 | [15312](https://github.com/airbytehq/airbyte/pull/15312) | Fix `started_time` and `ended_time` format schema error and updated report slicing |
| 0.1.8 | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Update titles and descriptions |
| 0.1.6 | 2021-11-14 | [7952](https://github.com/airbytehq/airbyte/pull/7952) | Implement OAuth 2.0 support |
| 0.1.5 | 2021-09-28 | [5747](https://github.com/airbytehq/airbyte/pull/5747) | Update schema date-time fields |
| 0.1.4   | 2021-06-22 | [5701](https://github.com/airbytehq/airbyte/pull/5071)   | Harvest normalization failure: fixing the schemas                                                                                 |
| 0.1.3   | 2021-06-22 | [4274](https://github.com/airbytehq/airbyte/pull/4274)   | Fix wrong data type on `statement_key` in `clients` stream                                                                        |
| 0.1.2   | 2021-06-07 | [4222](https://github.com/airbytehq/airbyte/pull/4222)   | Correct specification parameter name                                                                                              |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                   |
| 0.1.0   | 2021-06-07 | [3709](https://github.com/airbytehq/airbyte/pull/3709)   | Release Harvest connector!                                                                                                        |

</details>
