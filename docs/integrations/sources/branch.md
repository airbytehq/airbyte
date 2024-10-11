# Branch
Branch Connector
Branch Connector
This directory contains the manifest-only connector for [`source-branch`](https://www.branch.io/).

## Documentation reference:
- Visit `https://help.branch.io/developers-hub/reference/apis-overview` for API documentation

## Authentication setup
`Branch` uses different authentication methods depending on the API in use, Visit `https://help.branch.io/developers-hub/reference/trying-apis#authentication` for more information

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `url` | `string` | url.  The deep link url against which the details are to be fetched. |  |
| `limit` | `integer` | limit. The maximum number of results to return. | 1 |
| `app_id` | `string` | app_id. The App Id |  |
| `fields` | `array` | fields. An array representing fields/columns available in your report |  |
| `job_id` | `string` | job_id. Unique identifier for job. Obtained from POST Export Cohort Analytics API. |  |
| `end_date` | `string` | end_date. The end of the interval time range represented as an ISO-8601 complete datetime including Hours, Minutes, Seconds, and Milliseconds. |  |
| `measures` | `array` | measures. The cohort measures to return. |  |
| `branch_key` | `string` | branch_key. branch key |  |
| `start_date` | `string` | start_date. The start of the interval time range represented as an ISO-8601 complete datetime including Hours, Minutes, Seconds, and Milliseconds. Datetime must be within the last 120 days. |  |
| `data_source` | `string` | data source. A string value representing the cohort type |  |
| `export_date` | `string` | export_date. export date |  |
| `report_type` | `string` | report_type. An array representing event type of your report. |  |
| `access_token` | `string` | access-token. Access Token  |  |
| `branch_secret` | `string` | branch_secret. branch secret |  |
| `request_handle` | `string` | request_handle. The ID returned by the log export queue. |  |
| `granularity_band_count` | `integer` | granularity band count. Number of time units since the cohort event to return to the user. | 7 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| GET Export Request |  | No pagination | ✅ |  ❌  |
| Create Export Request |  | No pagination | ✅ |  ❌  |
| Read Existing Deep Link |  | No pagination | ✅ |  ❌  |
| Export Cohort Analytics |  | DefaultPaginator | ✅ |  ❌  |
| Get Export Download Status |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-11 | [46723] https://github.com/airbytehq/airbyte/pull/46723 | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
