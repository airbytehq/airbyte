# Acuity Scheduling

This page contains the setup guide and reference information for the [Acuity Scheduling](https://acuityscheduling.com/) source connector. The connector reads appointments, calendars, clients, appointment types, blocked time, labels, and intake forms from the [Acuity Scheduling API](https://developers.acuityscheduling.com/).

## Prerequisites

- An Acuity Scheduling account with access to the API credentials page in Acuity
- Your Acuity numeric **User ID** and **API Key**

## Setup guide

### Step 1: Get your Acuity API credentials

The Acuity API uses HTTP Basic authentication with your numeric user ID as the username and your API key as the password.

1. Log in to your Acuity Scheduling account.
2. Go to **Integrations** and find your API credentials.
3. Copy your **User ID** and **API Key**.

For more information, see the Acuity [API Quick Start](https://developers.acuityscheduling.com/reference/quick-start).

### Step 2: Set up the connector in Airbyte

1. In Airbyte, go to **Sources** and select **Acuity Scheduling**.
2. For **Username**, enter your numeric Acuity user ID.
3. For **Password**, enter your Acuity API key. Airbyte doesn't mark this field as required, but the Acuity API rejects requests without it.
4. For **Start date**, enter the earliest date to sync, in the format `YYYY-MM-DDTHH:MM:SSZ`. For example, `2024-01-01T00:00:00Z`. The connector uses only the date part of this value, and only for the `appointments` and `blocks` streams.
5. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Your numeric Acuity user ID. |  |
| `password` | `string` | Your Acuity API key. |  |
| `start_date` | `string` | The earliest appointment or block date to sync, in the format `YYYY-MM-DDTHH:MM:SSZ`. |  |

## Supported sync modes

The Acuity Scheduling source connector supports the following sync modes:

- Full Refresh - Overwrite
- Full Refresh - Append
- Incremental - Append (`appointments` and `blocks` streams only)
- Incremental - Append + Deduped (`appointments` and `blocks` streams only)

## Supported streams

| Stream name | API endpoint | Primary key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|--------------|-------------|------------|--------------------|----------------------|
| `appointments` | [`GET /appointments`](https://developers.acuityscheduling.com/reference/get-appointments) | `id` | No pagination | ✅ | ✅ |
| `calendars` | `GET /calendars` | `id` | No pagination | ✅ | ❌ |
| `clients` | `GET /clients` | `email` | No pagination | ✅ | ❌ |
| `appointment-types` | `GET /appointment-types` | `id` | No pagination | ✅ | ❌ |
| `blocks` | [`GET /blocks`](https://developers.acuityscheduling.com/reference/blocks) | `id` | No pagination | ✅ | ✅ |
| `labels` | `GET /labels` | `id` | No pagination | ✅ | ❌ |
| `forms` | `GET /forms` | `id` | No pagination | ✅ | ❌ |

### Stream details

- `appointments`: Scheduled and canceled appointments. The connector requests `showall=true`, so canceled appointments are included. Canceled appointments have `canceled` set to `true`.
- `blocks`: Blocked-off time on your calendars.
- `calendars`, `clients`, `appointment-types`, `labels`, and `forms`: The connector reads all records from these endpoints on every sync. The **Start date** doesn't apply to them.

## Limitations and sync behavior

- **Date filtering uses the appointment or block date.** For `appointments` and `blocks`, the connector sends the start date (or, on incremental syncs, the saved state) as the Acuity `minDate` query parameter. Acuity applies this filter to the date of the appointment or block, not the date the record was created or modified. Records dated before this value aren't synced, even in full refresh mode. Future-dated appointments and blocks are always included.
- **Incremental syncs re-read a one-week window.** Each incremental sync starts seven days before the point where the previous sync ended. Changes to appointments or blocks dated earlier than that window, such as a cancellation of an older appointment, aren't picked up. Run a full refresh to capture them.
- **The `insert_date` cursor field is added by the connector.** Acuity doesn't return an `insert_date` field. The connector adds it to each `appointments` and `blocks` record and sets it to the start date of the sync window, not to a date from the record itself.
- **No pagination.** Each stream makes a single API request. The connector requests up to 100,000 appointments and up to 10,000 blocks per sync. Other endpoints return their full result set in one response.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2026-10-08 | [88363](https://github.com/airbytehq/airbyte/pull/88363) | Replace the default Airbyte icon with the Acuity Scheduling logo |
| 0.0.2 | 2026-04-21 | [76492](https://github.com/airbytehq/airbyte/pull/76492) | Update dependencies |
| 0.0.1 | 2025-07-02 | | Initial release by [@chanronson](https://github.com/chanronson) via Connector Builder |

</details>
