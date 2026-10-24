# Gemini
This directory contains the manifest-only connector for `source-gemini`.

Google Gemini for Workspace source connector. Syncs Gemini in Google Workspace activity from the Google Workspace Admin SDK Reports API (gemini_in_workspace_apps application, feature_utilization events). Admins can use it to track Gemini feature adoption and usage across Workspace apps such as Gmail, Docs, Sheets, Slides and Meet, and to support auditing and governance.

Stream: activity_events (incremental, primary key: time + id). Records include the actor (email, profile ID, caller type, application info), events and their parameters, resource IDs, and an isAgenticAction flag.

Authentication: OAuth 2.0 with a refresh token (scopes: admin.reports.audit.readonly and admin.reports.usage.readonly). Requires a Google Workspace admin with access to the Reports API.

Sync behavior: incremental on time in 1-day slices with a 1-day lookback window. The Reports API only retains 180 days of data, so the default start is 180 days ago and earlier start times are moved forward to that limit. The default end is the start of the current UTC day, so only complete days are synced. Retries on 429, 500, 502, 503 and 504 with exponential backoff. The ipAddress, networkInfo, resourceDetails, etag and kind fields are removed from records.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-gemini:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-gemini build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-gemini test
```

