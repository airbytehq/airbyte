# Dropbox Sign
Dropbox Sign is a simple, easy-to-use way to get documents signed securely online.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.hellosign.com/home/myAccount#api |  |
| `start_date` | `string` | Start date.  |  |

See the [API docs](https://developers.hellosign.com/api/reference/authentication/#api-key-management) for details on generating an API Key.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| signature_requests | signature_request_id | DefaultPaginator | ✅ |  ✅  |
| templates | template_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.9 | 2025-01-11 | [51076](https://github.com/airbytehq/airbyte/pull/51076) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50553](https://github.com/airbytehq/airbyte/pull/50553) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50021](https://github.com/airbytehq/airbyte/pull/50021) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49528](https://github.com/airbytehq/airbyte/pull/49528) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49181](https://github.com/airbytehq/airbyte/pull/49181) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48946](https://github.com/airbytehq/airbyte/pull/48946) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47831](https://github.com/airbytehq/airbyte/pull/47831) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47607](https://github.com/airbytehq/airbyte/pull/47607) | Update dependencies |
| 0.0.1 | 2024-09-20 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
