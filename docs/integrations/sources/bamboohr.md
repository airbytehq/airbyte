# BambooHR
The BambooHR source connector for Airbyte allows seamless extraction of HR data through multiple configurable streams, including `custom_reports_stream`, `employees_directory_stream`, `meta_fields_stream`, `time_off_requests_stream`, `timesheet_entries`, and `employees`.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | api_key. Api key of bamboo hr |  |
| `subdomain` | `string` | subdomain. Sub Domain of bamboo hr |  |
| `start_date` | `string` | Start date.  |  |
| `employee_fields` | `string` | employee_fields. Comma-separated list of fields to include for employees. | firstName,lastName |
| `custom_reports_fields` | `string` | custom_reports_fields. Comma-separated list of fields to include in custom reports. |  |
| `custom_reports_include_default_fields` | `boolean` | custom_reports_include_default_fields. If true, the custom reports endpoint will include the default fields defined here: https://documentation.bamboohr.com/docs/list-of-field-names. | true |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| custom_reports_stream |  | No pagination | ✅ |  ❌  |
| employees_directory_stream | id | No pagination | ✅ |  ❌  |
| meta_fields_stream |  | No pagination | ✅ |  ❌  |
| time_off_requests_stream |  | No pagination | ✅ |  ✅  |
| timesheet_entries | id | No pagination | ✅ |  ✅  |
| employees |  | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-09 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
