# Shiftbase

<HideInUI>

This page contains the setup guide and reference information for the [Shiftbase](https://www.shiftbase.com/) source connector.

</HideInUI>

## Prerequisites

- A Shiftbase account with access to **Settings > App center**.
- A Shiftbase Public API token.

Each connection reads a single Shiftbase account. To sync several accounts, create one source per account.

### Generate an API token

1. In Shiftbase, go to **Settings > App center > Public API**.
2. Click **Install** on the **Public API** tile.
3. Enter a name for the token. Shiftbase then shows the token overview, where you can add more tokens with **+ Add App Token**.
4. Copy the token. You need it to configure the source.

The token inherits the permissions of the account that created it. If a stream returns no data or fails with an authorization error, check that the account can see the same departments, employees, and reports in the Shiftbase UI.

## Setup guide

### Set up the Shiftbase connector in Airbyte

1. Select **Shiftbase** from the list of sources.
2. Enter a **Source name**.
3. For **Access Token**, enter the Public API token you generated.
4. For **Start Date**, enter a date in `YYYY-MM-DD` format. See [How Start Date is used](#how-start-date-is-used).
5. Optional: for **Schedule Report End Date**, enter a date in `YYYY-MM-DD` format. This is the last day fetched by the `schedule_detail_report` stream. If you leave it empty, the connector uses 30 days from the day the sync runs, so future rosters are included.
6. Click **Set up source**.

### How Start Date is used

**Start Date** does more than bound historical data, and its effect differs by stream:

- `departments`, `employees`, and `shifts` send it as the `min_date` request parameter, so records that Shiftbase considers older than this date are excluded.
- `absentees` and `availabilities` use it as the initial cursor value and send it as `min_date`.
- `employee_time_distribution` uses the year of this date as the first year it requests.
- `employees_report` sends it as the report's `from` date.
- `timesheet_detail_report` and `schedule_detail_report` use it as the first day of their day-by-day window.

An early Start Date increases sync time significantly, because the report streams request one day at a time. For example, a Start Date two years in the past means roughly 730 requests per report stream on the first sync.

## Supported sync modes

The Shiftbase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (for supported streams)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) (for supported streams)

`employees_report` has no primary key, so it can't use **Incremental - Append + Deduped** or **Full Refresh - Overwrite + Deduped**.

## Supported streams

| Stream | Sync modes | Cursor field | Description |
|:---|:---|:---|:---|
| [Departments](https://developer.shiftbase.com/docs/core/510254d159b47-list-departments) | Full Refresh | | Departments and their scheduling, clocking, and timesheet settings. |
| [Employees](https://developer.shiftbase.com/docs/core/75d0181c0add8-list-employees-in-department) | Full Refresh | | Employee membership per department. One record per employee and department, with `id`, `department_id`, `team_id`, and `type`. Contains no names or other personal details. |
| [Employee Time Distribution](https://developer.shiftbase.com/docs/core/9ceb4dce3acb8-list-employee-time-distribution) | Full Refresh, Incremental | `year` | Worked hours, worked-hours percentage, and absences per employee per calendar year. |
| [Absentees](https://developer.shiftbase.com/docs/core/2e1fba402f9bb-list-absentees) | Full Refresh, Incremental | `updated` | Absence and leave records, including status, hours, and salary impact. |
| [Availabilities](https://developer.shiftbase.com/docs/core/0b8b4f51ba73a-list-availabilities) | Full Refresh, Incremental | `date` | Availability entries per employee and day. |
| [Shifts](https://developer.shiftbase.com/docs/core/c8dbe25e28719-list-shifts) | Full Refresh | | Shift definitions per department: name, default start and end times, breaks, rate card, and color. These are the templates used to build a roster, not rostered shifts. For rostered shifts, use `schedule_detail_report`. |
| [Users](https://developer.shiftbase.com/docs/core/7b22ead2360d9-list-users) | Full Refresh | | Account attributes per user: employee number, start and end dates, hire date, login and MFA status, locale, and plus/minus hours. Contains no names, email addresses, phone numbers, or addresses. |
| [Employees Report](https://developer.shiftbase.com/docs/core/4d05f64e94419-employees-report) | Full Refresh | | User report from the `reports/users` endpoint, including contract type, function, location, contract hours, and wage at the end of the reporting period. |
| [Timesheet Detail Report](https://developer.shiftbase.com/docs/core/5612d41bb72b1-timesheet-detail-report) | Full Refresh, Incremental | `timesheetDate` | Per-timesheet report rows with clocked and rostered times, breaks, surcharges, overtime, and salary. |
| [Schedule Detail Report](https://developer.shiftbase.com/docs/core/122ab05b95b82-schedule-detail-report) | Full Refresh, Incremental | `rosterDate` | Per-roster report rows with department, team, shift, times, breaks, and salary. Covers future rosters up to **Schedule Report End Date**. |

The connector requests the report streams with `export: json`, so records arrive as flat JSON rows rather than the column-and-row structure the Shiftbase API returns by default.

Airbyte tests the connection by reading `departments`. A failed connection test usually means the token is invalid or the account can't read departments.

### Incremental sync behavior

Incremental streams other than `schedule_detail_report` are configured as data feeds: the connector stops requesting once it passes the cursor window and discards records that fall outside it. Two consequences are worth planning for:

- Records dated in the future are dropped. `availabilities` uses the availability `date` as its cursor, so availability entered for future days doesn't sync. `schedule_detail_report` is the only stream that reads future-dated data, up to **Schedule Report End Date**.
- `availabilities` and `employee_time_distribution` advance on a data date, not an update timestamp. Edits to an already-synced day or year are only picked up if the stream re-reads that window, so use a fresh sync or a full refresh when you need corrected history.

`absentees` cursors on `updated`, so changes to existing absences do sync.

## Performance considerations

- The connector retries HTTP 429, 500, 502, 503, and 504 responses. It waits for the interval in the `Retry-After` response header when Shiftbase sends one, and otherwise backs off exponentially.
- `timesheet_detail_report` and `schedule_detail_report` request one day per API call, so sync duration scales with the length of the date range.
- `employee_time_distribution` makes one call per employee per year: it iterates every department, then every employee in that department, then each year from **Start Date** onward. On large accounts this is the slowest stream by a wide margin.
- No stream paginates. Each request returns the complete result set for its scope, so a wide **Start Date** on `departments`, `shifts`, or `absentees` produces large single responses.

## Limitations & Troubleshooting

<details>
<summary>Expand to review</summary>

### Connector limitations

- The `employees` and `users` streams exclude personal details such as names, email addresses, phone numbers, and addresses. If you need those fields, they aren't available through this connector.
- The report streams carry compensation data (`contractWage`, `timesheetSalary`, `rosterSalary`, `endContractWage`). Restrict access to these tables in your destination accordingly.
- Report stream schemas are fixed by the connector, and some columns are specific to the account they were captured from, such as surcharge percentage columns (`timesheet150.00%`) and custom-field columns (`timesheetCustomFields4490`). Columns your account returns that aren't in the schema are not declared in the catalog, so destinations may drop them.
- `employee_time_distribution` adds a synthetic `year` field as its cursor. Shiftbase doesn't return it; the connector derives it from the requested year.

### Troubleshooting

- **Connection test fails**: Confirm the token is active in **Settings > App center > Public API** and that the account can read departments.
- **A stream is empty**: Check whether **Start Date** excludes the data you expect, and remember that future-dated records only arrive through `schedule_detail_report`.
- **Missing future rosters**: Set **Schedule Report End Date** far enough ahead. Without it, the connector reads only 30 days beyond the sync date.
- **Syncs take hours**: Move **Start Date** forward, or disable `employee_time_distribution` and the report streams you don't need.

</details>

## Changelog

<details>
<summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|:---|:---|:---|:---|
| 0.0.1 | 2026-08-27 | [72899](https://github.com/airbytehq/airbyte/pull/72899) | Initial release |

</details>
