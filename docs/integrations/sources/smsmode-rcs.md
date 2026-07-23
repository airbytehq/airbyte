# smsmode Rcs
A source connector for the smsmode API dedicated to RCS (Rich Communication Services), supporting message performance logs and monthly channel-specific consumption data tracking.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date. Date de début de récupération de l&#39;historique (Format: YYYY-MM-DD) |  |

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
| 0.0.1 | 2026-06-15 | | Initial release by [@CaladeTechnologies](https://github.com/CaladeTechnologies) via Connector Builder |

</details>
