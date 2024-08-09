# Holiday api
This will need format
## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `country` | `string` | Country Or State. For countries, ISO 3166-1 alpha-2 or ISO 3166-1 alpha-3 format. For states / provinces (with our States &amp; Provinces plan), ISO 3166-2 format. Accepts up to 10 comma separated values. | US |
| `number_of_years` | `string` | Number of Years.  | 3 |
| `year` | `string` | Year.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| holidays | uuid | No pagination | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-09 | Initial release by bechurch-test via Connector Builder|

</details>