# Shiftbase

This page contains the setup guide and reference information for the Shiftbase source connector.

## Prerequisites

- A Shiftbase account with API access
- An Access Token generated from the Shiftbase App Center

## Setup guide

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Shiftbase** from the Source type dropdown.
4. Enter the name for the Shiftbase connector.
5. Add one or more **Accounts** with:
   - **Access Token**: Your Shiftbase API access token generated from the App Center
   - **Account Name**: A name to identify the account
6. For **Start Date**, enter the date in `YYYY-MM-DD` format. Data from this date onwards will be replicated.
7. Click **Set up source**.

<!-- /env:oss -->

## Supported sync modes

The Shiftbase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (for supported streams)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) (for supported streams)

## Supported Streams

- [Employees](https://developer.shiftbase.com/docs/core/75d0181c0add8-list-employees-in-department)
- [Employee Time Distribution](https://developer.shiftbase.com/docs/core/9ceb4dce3acb8-list-employee-time-distribution)
- [Departments](https://developer.shiftbase.com/docs/core/510254d159b47-list-departments)
- [Absentees](https://developer.shiftbase.com/docs/core/2e1fba402f9bb-list-absentees) \(Incremental\)
- [Availabilities](https://developer.shiftbase.com/docs/core/0b8b4f51ba73a-list-availabilities) \(Incremental\)
- [Shifts](https://developer.shiftbase.com/docs/core/c8dbe25e28719-list-shifts)
- [Users](https://developer.shiftbase.com/docs/core/7b22ead2360d9-list-users)
- [Employees Report](https://developer.shiftbase.com/docs/core/4d05f64e94419-employees-report)
- [Timesheet Detail Report](https://developer.shiftbase.com/docs/core/5612d41bb72b1-timesheet-detail-report)
- [Schedule Detail Report](https://developer.shiftbase.com/docs/core/122ab05b95b82-schedule-detail-report)

## Performance considerations

The connector is restricted by Shiftbase's API rate limits. The connector implements automatic rate limit handling with backoff strategies.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
|:--------|:-----------|:---------------------------------------------------------|:----------------|
| 0.1.47  | 2026-02-03 | [TBD](https://github.com/airbytehq/airbyte/pull/TBD)     | Initial release |

</details>
