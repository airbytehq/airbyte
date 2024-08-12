# Holiday API

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `year` | `string` | Year.  |  |
| `api_key` | `string` | API Key.  |  |
| `country` | `string` | Country Or State. But what if this works | US |
| `number_of_years` | `string` | Number of Years.  | 3 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| holidays | uuid | No pagination | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-12 | Initial release by natikgadzhi via Connector Builder|

</details>