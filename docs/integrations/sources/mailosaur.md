# Mailosaur
Mailosaur is a communication-testing platform .
With this connector we can easily fetch data from messages , servers and transactions streams!
Docs : https://mailosaur.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter &quot;api&quot; here |  |
| `password` | `string` | Password. Enter your api key here |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Messages | id | No pagination | ✅ |  ❌  |
| Message | id | No pagination | ✅ |  ❌  |
| Servers | id | No pagination | ✅ |  ❌  |
| Server | id | No pagination | ✅ |  ❌  |
| Transactions | timestamp | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-04 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
