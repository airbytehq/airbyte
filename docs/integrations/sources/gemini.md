# Gemini
Google Gemini for Workspace source connector. Syncs Gemini in Google Workspace activity from the Google Workspace Admin SDK Reports API (gemini_in_workspace_apps application, feature_utilization events). Admins can use it to track Gemini feature adoption and usage across Workspace apps such as Gmail, Docs, Sheets, Slides and Meet, and to support auditing and governance.

Stream: activity_events (incremental, primary key: time + id). Records include the actor (email, profile ID, caller type, application info), events and their parameters, resource IDs, and an isAgenticAction flag.

Authentication: OAuth 2.0 with a refresh token (scopes: admin.reports.audit.readonly and admin.reports.usage.readonly). Requires a Google Workspace admin with access to the Reports API.

Sync behavior: incremental on time in 1-day slices with a 1-day lookback window. The Reports API only retains 180 days of data, so the default start is 180 days ago and earlier start times are moved forward to that limit. The default end is the start of the current UTC day, so only complete days are synced. Retries on 429, 500, 502, 503 and 504 with exponential backoff. The ipAddress, networkInfo, resourceDetails, etag and kind fields are removed from records.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `end_time` | `string` | End Time. End of the report time range in RFC 3339 format  (e.g. 2010-10-28T10:26:35.000Z). If not provided, defaults to the  start of the current day (00:00:00 UTC), meaning only complete  days up to yesterday are synced. The default is derived from  today_utc() (midnight UTC, start-of-day), not now_utc() (the current  timestamp), so the nominal minus-1ms is a no-op against that  start-of-day base and no partial same-day activity is included. |  |
| `client_id` | `string` | Client ID.  |  |
| `start_time` | `string` | Start Time. Start of the report time range in RFC 3339 format (e.g. 2010-10-28T10:26:35.000Z). The API only allows data from the  last 180 days, so earlier dates are automatically adjusted forward  to stay within that window. If not provided, defaults to the start  of the day (00:00:00 UTC) 180 days before the current date, syncing  the maximum available history in whole days. |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_access_token` | `string` | Access token.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| activity_events | time.id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-08 | | Initial release by [@Joshua-omolewa](https://github.com/Joshua-omolewa) via Connector Builder |

</details>
