# PayFit
Connector for PayFit.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `company_id` | `string` | Company ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Company | id | No pagination | ✅ |  ❌  |
| Collaborators | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.12 | 2025-05-17 | [60081](https://github.com/airbytehq/airbyte/pull/60081) | Update dependencies |
| 0.0.11 | 2025-05-03 | [59464](https://github.com/airbytehq/airbyte/pull/59464) | Update dependencies |
| 0.0.10 | 2025-04-27 | [59081](https://github.com/airbytehq/airbyte/pull/59081) | Update dependencies |
| 0.0.9 | 2025-04-19 | [58506](https://github.com/airbytehq/airbyte/pull/58506) | Update dependencies |
| 0.0.8 | 2025-04-12 | [57907](https://github.com/airbytehq/airbyte/pull/57907) | Update dependencies |
| 0.0.7 | 2025-04-05 | [57368](https://github.com/airbytehq/airbyte/pull/57368) | Update dependencies |
| 0.0.6 | 2025-03-29 | [56729](https://github.com/airbytehq/airbyte/pull/56729) | Update dependencies |
| 0.0.5 | 2025-03-22 | [56162](https://github.com/airbytehq/airbyte/pull/56162) | Update dependencies |
| 0.0.4 | 2025-03-08 | [55063](https://github.com/airbytehq/airbyte/pull/55063) | Update dependencies |
| 0.0.3 | 2025-02-23 | [54555](https://github.com/airbytehq/airbyte/pull/54555) | Update dependencies |
| 0.0.2 | 2025-02-15 | [54022](https://github.com/airbytehq/airbyte/pull/54022) | Update dependencies |
| 0.0.1 | 2025-01-23 | | Initial release by [@remilapeyre](https://github.com/remilapeyre) via Connector Builder |

</details>
