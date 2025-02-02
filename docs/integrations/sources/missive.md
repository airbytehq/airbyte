# Missive
This page contains the setup guide and reference information for the [Missive](https://missiveapp.com/) source connector.

## Documentation reference:
Visit `https://missiveapp.com/help/api-documentation/rest-endpoints` for API documentation

## Authentication setup
`Missive` uses Bearer token authentication authentication, Visit your profile settings for getting your api keys. Refer `https://missiveapp.com/help/api-documentation/getting-started` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |
| `start_date` | `string` | Start date.  |  |
| `kind` | `string` | Kind. Kind parameter for `contact_groups` stream | group |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contact_books | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| shared_labels | id | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| conversations | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.10 | 2025-02-01 | [52785](https://github.com/airbytehq/airbyte/pull/52785) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52289](https://github.com/airbytehq/airbyte/pull/52289) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51808](https://github.com/airbytehq/airbyte/pull/51808) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51183](https://github.com/airbytehq/airbyte/pull/51183) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50141](https://github.com/airbytehq/airbyte/pull/50141) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49631](https://github.com/airbytehq/airbyte/pull/49631) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49238](https://github.com/airbytehq/airbyte/pull/49238) | Update dependencies |
| 0.0.3 | 2024-12-11 | [47796](https://github.com/airbytehq/airbyte/pull/47796) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-28 | [47599](https://github.com/airbytehq/airbyte/pull/47599) | Update dependencies |
| 0.0.1 | 2024-09-22 | [45844](https://github.com/airbytehq/airbyte/pull/45844) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
