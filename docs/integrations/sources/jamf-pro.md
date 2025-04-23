# Jamf Pro
Mobile device management

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `subdomain` | `string` | Subdomain. The unique subdomain for your Jamf Pro instance. |  |
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| computers | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58160](https://github.com/airbytehq/airbyte/pull/58160) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57680](https://github.com/airbytehq/airbyte/pull/57680) | Update dependencies |
| 0.0.1 | 2025-04-08 | | Initial release by [@rrecin](https://github.com/rrecin) via Connector Builder |

</details>
