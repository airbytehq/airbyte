# Eventbrite
New connector to Eventbrite events

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `private_token` | `string` | Private Token. The private token to use for authenticating API requests. |  |
| `organization_id` | `string` | organization_id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| event |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-17 | Initial release by [@nataliekwong](https://github.com/nataliekwong) via Connector Builder|

</details>