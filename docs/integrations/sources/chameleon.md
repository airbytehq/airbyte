# Chameleon
Chameleon
Website: https://app.chameleon.io/
API docs: https://developers.chameleon.io/#/apis/overview
API page: https://app.chameleon.io/settings/tokens

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
| changes | id | No pagination | ✅ |  ❌  |
| launchers | id | No pagination | ✅ |  ✅  |
| tooltips | id | No pagination | ✅ |  ✅  |
| tours | id | No pagination | ✅ |  ✅  |
| surveys | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-18 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>