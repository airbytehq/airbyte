# Gemini for Google Workspace

This source syncs Gemini for Google Workspace activity from the [Google Workspace Admin SDK Reports API](https://developers.google.com/workspace/admin/reports/v1/get-start/overview).
It reads `feature_utilization` events of the `gemini_in_workspace_apps` application, so admins can track Gemini adoption and usage across Workspace apps such as Gmail, Docs, Sheets, Slides, and Meet, and support auditing and governance.

This connector does not read from the Gemini API (Google AI Studio or Vertex AI).

## Prerequisites

- A Google Workspace account with an admin who has the **Reports** admin privilege (for example, a super admin).
- A Google Cloud project where you can enable APIs and create OAuth clients.

## Setup guide

### Step 1: Enable the Admin SDK API

1. In the [Google Cloud console](https://console.cloud.google.com/), select or create a project.
2. Go to **APIs & Services** > **Library**, search for **Admin SDK API**, and click **Enable**.

### Step 2: Create an OAuth client

1. Go to **APIs & Services** > **OAuth consent screen** and configure the consent screen.
   Choose the **Internal** user type so only users in your Workspace organization can authorize the app.
2. Go to **APIs & Services** > **Credentials**, click **Create credentials** > **OAuth client ID**, and choose **Web application**.
3. Under **Authorized redirect URIs**, add `https://developers.google.com/oauthplayground`.
4. Click **Create** and copy the **Client ID** and **Client secret**.

### Step 3: Obtain a refresh token

The connector needs only one OAuth scope:

```text
https://www.googleapis.com/auth/admin.reports.audit.readonly
```

To generate a refresh token with the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground):

1. Click the gear icon, select **Use your own OAuth credentials**, and enter the Client ID and Client secret from Step 2.
2. In **Step 1 - Select & authorize APIs**, enter the scope above and click **Authorize APIs**.
3. Sign in as the Workspace admin with the Reports privilege and grant access.
4. In **Step 2 - Exchange authorization code for tokens**, click **Exchange authorization code for tokens** and copy the **Refresh token**.

If the consent screen uses the **External** user type with the **Testing** publishing status, Google expires refresh tokens after 7 days.
Use the **Internal** user type to avoid this.

### Step 4: Set up the connector in Airbyte

1. In Airbyte, go to **Sources** and select **Gemini for Google Workspace**.
2. Enter the **Client ID**, **Client secret**, and **Refresh token**.
3. Optionally, set **Start Time** and **End Time** in RFC 3339 format, for example `2026-01-01T00:00:00.000Z`.
4. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
| --- | --- | --- | --- |
| `client_id` | `string` | Client ID. OAuth client ID from your Google Cloud project. | |
| `client_secret` | `string` | Client secret. OAuth client secret from your Google Cloud project. | |
| `client_refresh_token` | `string` | Refresh token. Refresh token granted by a Workspace admin with the `admin.reports.audit.readonly` scope. | |
| `start_time` | `string` | Start Time. Start of the report time range in RFC 3339 format. The API only allows data from the last 180 days, so earlier dates are adjusted forward to stay within that window. | Start of the day (00:00:00 UTC) 180 days ago |
| `end_time` | `string` | End Time. End of the report time range in RFC 3339 format. | Start of the current day (00:00:00 UTC) |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
| --- | --- | --- | --- | --- |
| activity_events | time, uniqueQualifier | DefaultPaginator | ✅ | ✅ |

Records include the actor (email, profile ID, caller type, application info), events and their parameters, resource IDs, and an `isAgenticAction` flag.
The `ipAddress`, `networkInfo`, `resourceDetails`, `etag`, and `kind` fields are removed from records.

## Sync behavior

Incremental syncs use the `time` cursor in 1-day slices with a 1-day lookback window, which picks up events that Google reports late.
By default, the end of the range is the start of the current UTC day, so only complete days are synced.
The Reports API only retains 180 days of activity data.

The connector retries HTTP 429, 500, 502, 503, and 504 responses with exponential backoff.
For quota details, see [Reports API limits and quotas](https://developers.google.com/workspace/admin/reports/v1/limits).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-26 | [88377](https://github.com/airbytehq/airbyte/pull/88377) | Initial release by [@Joshua-omolewa](https://github.com/Joshua-omolewa) via Connector Builder |

</details>
