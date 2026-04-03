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

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Shiftbase from the Source type dropdown.
4. Enter a name for the Shiftbase connector.
5. Enter your **Account Name** (an identifier for tracking).
6. Enter your **Access Token** from the Shiftbase App Center.
7. Enter your **Start Date** for historical data sync (format: YYYY-MM-DD).
8. Click **Set up source**.

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Shiftbase from the Source type dropdown.
4. Enter a name for the Shiftbase connector.
5. Enter your **Account Name** (an identifier for tracking).
6. Enter your **Access Token** from the Shiftbase App Center.
7. Enter your **Start Date** for historical data sync (format: YYYY-MM-DD).
8. Click **Set up source**.

### Multiple Accounts

The Shiftbase connector supports syncing data from multiple Shiftbase accounts simultaneously. When configuring the connector, you can add multiple account configurations, each with its own access token and account name.

## Supported sync modes

The Shiftbase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature                       | Supported |
|:------------------------------|:----------|
| Full Refresh Sync             | Yes       |
| Incremental - Append Sync     | Yes       |
| Replicate Incremental Deletes | No        |
| SSL connection                | Yes       |
| Namespaces                    | No        |

## Supported Streams

The Shiftbase source connector supports the following streams:

| Stream                      | Sync Mode                   | Description                                              |
|:----------------------------|:----------------------------|:---------------------------------------------------------|
| `departments`               | Full Refresh                | Internal departments within the Shiftbase account        |
| `employees`                 | Full Refresh                | List of employees (PII fields like name are excluded)    |
| `absentees`                 | Full Refresh, Incremental   | Records of employee absences and leave                   |
| `employee_time_distribution`| Full Refresh                | Distribution of worked and planned hours per employee    |
| `availabilities`            | Full Refresh, Incremental   | Employee availability slots and preferences              |
| `shifts`                    | Full Refresh                | Scheduled work shifts and roster details                 |
| `users`                     | Full Refresh                | User account details (PII excluded, flattened structure) |
| `employees_report`          | Full Refresh                | Employees report data                                    |
| `timesheet_detail_report`   | Full Refresh                | Detailed timesheet report data                           |
| `schedule_detail_report`    | Full Refresh                | Detailed schedule report data                            |

### Performance considerations

The Shiftbase API has rate limiting in place. The connector handles rate limits automatically with exponential backoff. If you encounter rate limit issues, consider:

- Reducing the sync frequency
- Using incremental sync where available to minimize API calls

## Data type map

| Shiftbase Type | Airbyte Type |
|:---------------|:-------------|
| `string`       | `string`     |
| `integer`      | `integer`    |
| `boolean`      | `boolean`    |
| `object`       | `object`     |
| `array`        | `array`      |
| `date`         | `string`     |
| `datetime`     | `string`     |

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

| Version | Date       | Pull Request | Subject                                     |
|:--------|:-----------|:-------------|:--------------------------------------------|
| 0.1.46  | 2026-02-03 | TBD          | Initial release with 10 streams             |

</details>
