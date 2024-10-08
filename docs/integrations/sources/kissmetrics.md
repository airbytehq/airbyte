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
| 0.0.1 | 2024-09-21 | [45839](https://github.com/airbytehq/airbyte/pull/45839) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>