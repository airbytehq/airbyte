# Onfleet
Onfleet is a logistics software.
Using this connector we can extract data from workers , teams , hubs and tasks streams.
Docs : https://docs.onfleet.com/reference/introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `from` | `string` | from.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organization | id | No pagination | ✅ |  ❌  |
| admins | id | No pagination | ✅ |  ❌  |
| workers | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| hubs | id | No pagination | ✅ |  ❌  |
| tasks | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
