# Breezy HR
An Airbyte source for Breezy applicant tracking system.
## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `company_id` | `string` | Company ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| positions |  | No pagination | ✅ |  ❌  |
| candidates |  | No pagination | ✅ |  ❌  |
| pipelines |  | No pagination | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.3 | 2024-10-29 | [47750](https://github.com/airbytehq/airbyte/pull/47750) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47587](https://github.com/airbytehq/airbyte/pull/47587) | Update dependencies |
| 0.0.1 | 2024-08-20 | | Initial release by natikgadzhi via Connector Builder |

</details>
