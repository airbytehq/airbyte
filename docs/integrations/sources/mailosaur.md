# Mailosaur
Mailosaur is a communication-testing platform .
With this connector we can easily fetch data from messages , servers and transactions streams!
Docs : https://mailosaur.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter API here |  |
| `password` | `string` | Password. Enter your API Key here |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Messages | id | No pagination | ✅ |  ❌  |
| Servers | id | No pagination | ✅ |  ❌  |
| Transactions | timestamp | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-11 | [51159](https://github.com/airbytehq/airbyte/pull/51159) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50639](https://github.com/airbytehq/airbyte/pull/50639) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50098](https://github.com/airbytehq/airbyte/pull/50098) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49607](https://github.com/airbytehq/airbyte/pull/49607) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49260](https://github.com/airbytehq/airbyte/pull/49260) | Update dependencies |
| 0.0.1 | 2024-11-04 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
