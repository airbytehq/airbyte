# Buzzsprout
Website: https://www.buzzsprout.com/
API Docs: https://github.com/buzzsprout/buzzsprout-api/tree/master/sections
Auth Docs: https://github.com/buzzsprout/buzzsprout-api/tree/master?tab=readme-ov-file#authentication
API Keys page: https://www.buzzsprout.com/my/profile/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `podcast_id` | `string` | Podcast ID. Podcast ID found in `my/profile/api` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| episodes | id | No pagination | ✅ |  ✅  |
| podcasts | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-16 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>