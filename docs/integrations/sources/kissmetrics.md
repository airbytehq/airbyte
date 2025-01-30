# Kissmetrics
This page contains the setup guide and reference information for the [Kissmetrics](https://app.kissmetrics.io/) source connector.

## Documentation reference:
Visit `https://support.kissmetrics.io/reference/overview-1` for API documentation

## Authentication setup
`Kissmetrics` uses Basic Http authentication which uses your username and password,
Refer `https://support.kissmetrics.io/reference/authorization` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products | id | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| properties | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.11 | 2025-01-25 | [52225](https://github.com/airbytehq/airbyte/pull/52225) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51789](https://github.com/airbytehq/airbyte/pull/51789) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51206](https://github.com/airbytehq/airbyte/pull/51206) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50597](https://github.com/airbytehq/airbyte/pull/50597) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50096](https://github.com/airbytehq/airbyte/pull/50096) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49600](https://github.com/airbytehq/airbyte/pull/49600) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49247](https://github.com/airbytehq/airbyte/pull/49247) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48151](https://github.com/airbytehq/airbyte/pull/48151) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47756](https://github.com/airbytehq/airbyte/pull/47756) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47650](https://github.com/airbytehq/airbyte/pull/47650) | Update dependencies |
| 0.0.1 | 2024-09-21 | [45839](https://github.com/airbytehq/airbyte/pull/45839) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
