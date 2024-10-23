# Chameleon
This page contains the setup guide and reference information for the [Chameleon](https://app.chameleon.io/) source connector.

## Documentation reference:
Visit `https://developers.chameleon.io/#/apis/overview` for API documentation

## Authentication setup
`Chameleon` uses API Key authentication,
Refer `https://app.chameleon.io/settings/tokens` for getting your API key.


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |
| `filter` | `string` | Filter. Filter for using in the `segments_experiences` stream | tour |
| `end_date` | `string` | End date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| helpbars | id | No pagination | ✅ |  ✅  |
| segments | id | No pagination | ✅ |  ✅  |
| urls | id | No pagination | ✅ |  ✅  |
| url_groups | id | No pagination | ✅ |  ✅  |
| changes | id | No pagination | ✅ |  ✅ |
| launchers | id | No pagination | ✅ |  ✅  |
| tooltips | id | No pagination | ✅ |  ✅  |
| tours | id | No pagination | ✅ |  ✅  |
| surveys | id | No pagination | ✅ |  ✅  |
| survey_responses | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Pull Request | Subject        |
|------------------|------------|--------------|----------------|
| 0.1.0 | 2024-09-29 |[46248](https://github.com/airbytehq/airbyte/pull/46248)| Fix survey_responses stream schema and icon |
| 0.0.2 | 2024-09-21 |[45708](https://github.com/airbytehq/airbyte/pull/45708)| Make end date optional |
| 0.0.1 | 2024-09-18 |[45658](https://github.com/airbytehq/airbyte/pull/45658)| Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>