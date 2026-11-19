# TrackingTime

[TrackingTime](https://trackingtime.co) is time tracking software for agencies, professional services, and teams that bill by the hour. This connector syncs time entries, projects, tasks, customers, services, and users to your data warehouse, so you can analyze billable hours, utilization, and project profitability alongside the rest of your data.

## Prerequisites

- A TrackingTime account with admin access, so the connector can read time entries for the whole team.
- A TrackingTime app password.

## Setup guide

### Create an app password in TrackingTime

1. Sign in to TrackingTime as an administrator.
2. Go to **Profile Settings** > **App Passwords**.
3. Select **Add Password** and copy the generated value.

### Set up the TrackingTime connector in Airbyte

1. Click **Sources** and then click **+ New source**.
2. Select **TrackingTime** from the list of sources.
3. Enter the **App Password**.
4. Enter a **Start Date** in `YYYY-MM-DD` format.
5. Click **Set up source**.

The connector uses HTTP Basic authentication, with `API_TOKEN` as the user name and the app password as the password.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `app_password` | `string` | App Password. TrackingTime app password. Create one in TrackingTime under Profile Settings > App Passwords. |  |
| `start_date` | `string` | Start Date. Time entries starting on or after this date are synced. Format YYYY-MM-DD. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| time_entries | ID | DefaultPaginator | ✅ |  ✅  |
| projects | id | No pagination | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | No pagination | ✅ |  ❌  |
| services | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ❌  |

### Notes

- `time_entries` is read in monthly slices using the `Start` field as the cursor. Each incremental sync reads the last 30 days again, so edits to recent entries are picked up. Use a deduplicating sync mode in the destination.
- `time_entries` includes the custom fields of the account as extra columns, named `<Field> (<Object> CF)`, for example `Status (Task CF)`.
- Calendar tokens, session tokens, invite links and avatar URLs are removed from all streams.

## Limitations

- The TrackingTime API returns up to 100 tasks per request, so accounts with many tasks take longer to sync.
- Edits to time entries older than 30 days are only picked up by a full refresh.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-11-19 | | Initial release by [@trackingtime](https://github.com/TrackingTime) |

</details>
