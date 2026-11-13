# Pigment

Pigment is a business planning and forecasting platform. This connector reads metadata about your Pigment applications (applications, blocks, views, import configurations and data flows) and can export the data of selected views.

## Configuration

| Input             | Type            | Description                                                                                                                           | Default Value |
| ----------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `metadata_api_key` | `string`        | Modeling Metadata API Key. Pigment API key with the Modeling Metadata scope, used for all streams except `export_view`.               |               |
| `export_api_key`   | `string`        | Export API Key. Pigment API key with the Export scope. Required only for the `export_view` stream.                                    |               |
| `export_view_ids`  | `array[string]` | View IDs to Export. IDs of the Pigment views whose data the `export_view` stream exports. If empty, `export_view` returns no records. |               |

To get an API key, create one in your Pigment workspace with the scopes you need. A single key that has both the Modeling Metadata and Export scopes works for both fields. See Pigment's [API documentation](https://kb.pigment.com/docs/export-data-with-apis) for details.

To find a view ID, list your views with the `views` stream, or use the view's ID from the Pigment API.

## Rate limits

Pigment allows [500 requests per 5 minutes per IP address](https://kb.pigment.com/docs/rate-limits-for-pigment-public-api) across its public API endpoints, and returns HTTP 429 when the limit is exceeded. The connector caps itself at 400 requests per 5 minutes and waits 60 seconds before retrying when it receives a 429.

The limit applies per IP address, not per API key, so other Airbyte sources or scripts that call Pigment from the same IP address share the same budget. The `blocks`, `views` and `import_configurations` streams make one request per parent record (per application or per block), so workspaces with many blocks use more of the budget.

## Streams

| Stream Name             | Primary Key | Pagination    | Supports Full Sync | Supports Incremental |
| ----------------------- | ----------- | ------------- | ------------------ | -------------------- |
| applications            | id          | No pagination | ✅                  | ❌                    |
| blocks                  | id          | No pagination | ✅                  | ❌                    |
| views                   | id          | No pagination | ✅                  | ❌                    |
| import\_configurations  | id          | No pagination | ✅                  | ❌                    |
| data\_flows             | id          | No pagination | ✅                  | ❌                    |
| export\_view            |             | No pagination | ✅                  | ❌                    |

### Notes on specific streams

- **`import_configurations` and `data_flows`**: Pigment returns HTTP 403 for some applications and blocks when the API key's owner lacks access. The connector skips those requests and continues, so these streams can return fewer records than exist in the workspace.
- **`export_view`**: exports the data of each view listed in `export_view_ids`, one request per view.
  - Pigment returns the data as `;`-delimited CSV. Each row becomes one record, with the view's column headers as field names, and all values are strings.
  - The columns depend on the view, so the stream's schema is open.
  - The export includes Pigment's subtotal and total rows (for example a `Total` member) alongside the detail rows. Filter these in downstream queries if you don't want them double counted.
  - Each record includes a `pigment_view_id` field identifying the view it came from.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                                                                      |
| ------- | ---------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| 0.0.1   | 2026-10-15 |              | Initial release by [@your-github-username](https://github.com/your-github-username) via Connector Builder |

</details>
