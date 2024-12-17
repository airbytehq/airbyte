# Buzzsprout
This page contains the setup guide and reference information for the [Buzzsprout](https://www.buzzsprout.com/) source connector.

## Documentation reference:
Visit `https://github.com/buzzsprout/buzzsprout-api/tree/master/sections` for API documentation

## Authentication setup
`Source-buzzsprout` uses API keys and podcast id for its authentication,
Visit `https://www.buzzsprout.com/my/profile/api` for getting api key and podcast id
Visit `https://github.com/buzzsprout/buzzsprout-api/tree/master?tab=readme-ov-file#authentication` for knowing more about authentication.

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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.7 | 2024-12-14 | [49564](https://github.com/airbytehq/airbyte/pull/49564) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49278](https://github.com/airbytehq/airbyte/pull/49278) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49029](https://github.com/airbytehq/airbyte/pull/49029) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48228](https://github.com/airbytehq/airbyte/pull/48228) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47747](https://github.com/airbytehq/airbyte/pull/47747) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47645](https://github.com/airbytehq/airbyte/pull/47645) | Update dependencies |
| 0.0.1 | 2024-09-16 | [45608](https://github.com/airbytehq/airbyte/pull/45608) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
