# Shiftbase

<HideInUI>

This page contains the setup guide and reference information for the [Shiftbase](https://www.shiftbase.com/) source connector.

</HideInUI>

## Prerequisites

To set up the Shiftbase source connector, you'll need:

- A Shiftbase account with API access
- An **Access Token** generated from the Shiftbase App Center
- The **Account Name** for tracking purposes (you can use any identifier)

### Generating an Access Token

1. Log in to your Shiftbase account
2. Navigate to the App Center
3. Generate a new API Access Token
4. Copy and securely store the token - you'll need it for the connector configuration

## Setup guide

### Set up Shiftbase

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Shiftbase from the Source type dropdown.
4. Enter a name for the Shiftbase connector.
5. Enter your **Account Name** (an identifier for tracking).
6. Enter your **Access Token** from the Shiftbase App Center.
7. Enter your **Start Date** for historical data sync (format: YYYY-MM-DD).
8. Optionally, enter a **Schedule Report End Date** (format: YYYY-MM-DD) to set the end date for the Schedule Detail Report stream. Defaults to 1 month into the future if not provided.
9. Click **Set up source**.

<!-- env:oss -->

#### For Airbyte Open Source

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Shiftbase** from the Source type dropdown.
4. Enter the name for the Shiftbase connector.
5. Add one or more **Accounts** with:
   - **Access Token**: Your Shiftbase API access token generated from the App Center
   - **Account Name**: A name to identify the account
6. For **Start Date**, enter the date in `YYYY-MM-DD` format. Data from this date onwards will be replicated.
7. Optionally, for **Schedule Report End Date**, enter a date in `YYYY-MM-DD` format to set the end date for the Schedule Detail Report stream. If not provided, it defaults to 1 month into the future from the current date.
8. Click **Set up source**.

<!-- /env:oss -->

### Multiple Accounts

The Shiftbase connector supports syncing data from multiple Shiftbase accounts simultaneously. When configuring the connector, you can add multiple account configurations, each with its own access token and account name.

## Supported sync modes

The Shiftbase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (for supported streams)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) (for supported streams)

## Supported Streams

| Stream | Sync Mode | Description |
|:---|:---|:---|
| [Departments](https://developer.shiftbase.com/docs/core/510254d159b47-list-departments) | Full Refresh | Internal departments within the Shiftbase account |
| [Employees](https://developer.shiftbase.com/docs/core/75d0181c0add8-list-employees-in-department) | Full Refresh | List of employees (PII fields like name are excluded) |
| [Absentees](https://developer.shiftbase.com/docs/core/2e1fba402f9bb-list-absentees) | Full Refresh, Incremental | Records of employee absences and leave |
| [Employee Time Distribution](https://developer.shiftbase.com/docs/core/9ceb4dce3acb8-list-employee-time-distribution) | Full Refresh, Incremental | Distribution of worked and planned hours per employee |
| [Availabilities](https://developer.shiftbase.com/docs/core/0b8b4f51ba73a-list-availabilities) | Full Refresh, Incremental | Employee availability slots and preferences |
| [Shifts](https://developer.shiftbase.com/docs/core/c8dbe25e28719-list-shifts) | Full Refresh | Scheduled work shifts and roster details |
| [Users](https://developer.shiftbase.com/docs/core/7b22ead2360d9-list-users) | Full Refresh | User account details (PII excluded, flattened structure) |
| [Employees Report](https://developer.shiftbase.com/docs/core/4d05f64e94419-employees-report) | Full Refresh | Employees report data |
| [Timesheet Detail Report](https://developer.shiftbase.com/docs/core/5612d41bb72b1-timesheet-detail-report) | Full Refresh, Incremental | Detailed timesheet report data |
| [Schedule Detail Report](https://developer.shiftbase.com/docs/core/122ab05b95b82-schedule-detail-report) | Full Refresh, Incremental | Detailed schedule report data |

## Performance considerations

The Shiftbase API has rate limiting in place. The connector handles rate limits automatically with exponential backoff. If you encounter rate limit issues, consider:

- Reducing the sync frequency
- Using incremental sync where available to minimize API calls

## Data type map

| Shiftbase Type | Airbyte Type |
|:---|:---|
| `string` | `string` |
| `integer` | `integer` |
| `boolean` | `boolean` |
| `object` | `object` |
| `array` | `array` |
| `date` | `string` |
| `datetime` | `string` |

## Limitations & Troubleshooting

<details>
<summary>Expand to review</summary>

### Connector limitations

- The `users` stream is flattened and excludes PII (names, emails, phones, addresses) for privacy compliance
- The `employees` stream has the `name` field removed to minimize PII exposure
- Some streams (reports) make day-by-day API calls which may result in longer sync times for large date ranges

### Troubleshooting

- **Connection test fails**: Verify your access token is valid and has not expired
- **Empty streams**: Ensure your Shiftbase account has data for the requested date range
- **Rate limiting**: The connector handles rate limits automatically, but extended syncs may take longer if limits are hit frequently

</details>

## Changelog

<details>
<summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|:---|:---|:---|:---|
| 0.0.1 | 2026-02-03 | [72899](https://github.com/airbytehq/airbyte/pull/72899) | Initial release |

</details>
