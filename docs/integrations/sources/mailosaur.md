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
| 0.0.1 | 2024-11-04 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
