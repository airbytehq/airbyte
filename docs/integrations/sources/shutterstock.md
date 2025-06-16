# Shutterstock
Website: https://www.shutterstock.com/
API Reference: https://api-reference.shutterstock.com/#overview

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Your OAuth 2.0 token for accessing the Shutterstock API. Obtain this token from your Shutterstock developer account. |  |
| `start_date` | `string` | Start date.  |  |
| `query_for_image_search` | `string` | Query for image search. The query for image search | mountain |
| `query_for_video_search` | `string` | Query for video search. The Query for `videos_search` stream | mountain |
| `query_for_audio_search` | `string` | Query for audio search. The query for image search | mountain |
| `query_for_catalog_search` | `string` | Query for catalog search. The query for catalog search | mountain |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| images_categories | id | No pagination | ✅ |  ❌  |
| images_search | id | DefaultPaginator | ✅ |  ❌  |
| videos_search | id | DefaultPaginator | ✅ |  ❌  |
| videos_categories | id | No pagination | ✅ |  ❌  |
| audio_search | uuid | DefaultPaginator | ✅ |  ✅  |
| audio_genres | uuid | No pagination | ✅ |  ❌  |
| audio_instruments | uuid | No pagination | ✅ |  ❌  |
| audio_moods | uuid | No pagination | ✅ |  ❌  |
| user_details | id | DefaultPaginator | ✅ |  ❌  |
| user_subscriptions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-06-14 | [61609](https://github.com/airbytehq/airbyte/pull/61609) | Update dependencies |
| 0.0.8 | 2025-05-25 | [60553](https://github.com/airbytehq/airbyte/pull/60553) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60182](https://github.com/airbytehq/airbyte/pull/60182) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59588](https://github.com/airbytehq/airbyte/pull/59588) | Update dependencies |
| 0.0.5 | 2025-04-27 | [58975](https://github.com/airbytehq/airbyte/pull/58975) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58417](https://github.com/airbytehq/airbyte/pull/58417) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57998](https://github.com/airbytehq/airbyte/pull/57998) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57429](https://github.com/airbytehq/airbyte/pull/57429) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56998](https://github.com/airbytehq/airbyte/pull/56998) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
