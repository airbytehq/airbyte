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
| 0.0.6 | 2024-12-14 | [49547](https://github.com/airbytehq/airbyte/pull/49547) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49315](https://github.com/airbytehq/airbyte/pull/49315) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49020](https://github.com/airbytehq/airbyte/pull/49020) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47750](https://github.com/airbytehq/airbyte/pull/47750) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47587](https://github.com/airbytehq/airbyte/pull/47587) | Update dependencies |
| 0.0.1 | 2024-08-20 | | Initial release by natikgadzhi via Connector Builder |

</details>
