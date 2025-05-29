# SavvyCal
Sync your scheduled meetings and scheduling links from SavvyCal!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to SavvyCal → Settings → Developer → Personal Tokens and make a new token. Then, copy the private key. https://savvycal.com/developers |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ❌  |
| scheduling_links | id | DefaultPaginator | ✅ |  ❌  |
| timezones | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-01 | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder|

</details>