# smsmode Rcs

A source connector for the smsmode API dedicated to RCS (Rich Communication Services), automatically retrieving the rolling last 30 days of message logs (MT & MO merged) and monthly channel-specific consumption data.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| rcs_messages |  | DefaultPaginator | ✅ |  ❌  |
| consumptions_rcs |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2026-09-08 | [79710](https://github.com/airbytehq/airbyte/pull/79710) | Remove `start_date` config in favor of an automatic rolling 30-day window; partition `rcs_messages` across MT and MO directions |
| 0.0.1 | 2026-06-15 | [79710](https://github.com/airbytehq/airbyte/pull/79710) | Initial release by [@CaladeTechnologies](https://github.com/CaladeTechnologies) via Connector Builder |

</details>
