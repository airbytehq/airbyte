# Fastly
Website: https://manage.fastly.com/
API Reference: https://www.fastly.com/documentation/reference/api/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `fastly_api_token` | `string` | Fastly API Token. Your Fastly API token. You can generate this token in the Fastly web interface under Account Settings or via the Fastly API. Ensure the token has the appropriate scope for your use case. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| current_user | id | No pagination | ✅ |  ✅  |
| service | id | DefaultPaginator | ✅ |  ✅  |
| service_details | id | DefaultPaginator | ✅ |  ✅  |
| service_version | uuid | DefaultPaginator | ✅ |  ✅  |
| service_dictionaries | id | DefaultPaginator | ✅ |  ✅  |
| service_backend | uuid | DefaultPaginator | ✅ |  ✅  |
| service_domain | uuid | DefaultPaginator | ✅ |  ✅  |
| service_acl | uuid | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58337](https://github.com/airbytehq/airbyte/pull/58337) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57843](https://github.com/airbytehq/airbyte/pull/57843) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57528](https://github.com/airbytehq/airbyte/pull/57528) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
