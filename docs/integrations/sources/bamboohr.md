# BambooHR
The BambooHR connector for Airbyte seamlessly syncs vital HR data from your BambooHR account to your data warehouse or other destination.  This connector extracts information from custom reports, the employee directory, meta fields, and time-off requests.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | api_key. Api key of bamboo hr |  |
| `subdomain` | `string` | subdomain. Sub Domain of bamboo hr |  |
| `custom_reports_fields` | `array` | custom_reports_fields. Comma-separated list of fields to include in custom reports. |  |
| `custom_reports_include_default_fields` | `boolean` | custom_reports_include_default_fields. If true, the custom reports endpoint will include the default fields defined here: https://documentation.bamboohr.com/docs/list-of-field-names. | true |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| custom_reports_stream |  | No pagination | ✅ |  ❌  |
| employees_directory_stream | id | No pagination | ✅ |  ❌  |
| meta_fields_stream |  | No pagination | ✅ |  ❌  |
| time_off_requests_stream |  | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-02-11 | | Initial release by [@cbeauch](https://github.com/cbeauch) via Connector Builder |

</details>
