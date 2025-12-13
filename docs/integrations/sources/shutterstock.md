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
| 0.0.26 | 2025-12-09 | [70702](https://github.com/airbytehq/airbyte/pull/70702) | Update dependencies |
| 0.0.25 | 2025-11-25 | [69500](https://github.com/airbytehq/airbyte/pull/69500) | Update dependencies |
| 0.0.24 | 2025-10-29 | [68804](https://github.com/airbytehq/airbyte/pull/68804) | Update dependencies |
| 0.0.23 | 2025-10-21 | [68269](https://github.com/airbytehq/airbyte/pull/68269) | Update dependencies |
| 0.0.22 | 2025-10-14 | [67759](https://github.com/airbytehq/airbyte/pull/67759) | Update dependencies |
| 0.0.21 | 2025-10-07 | [67437](https://github.com/airbytehq/airbyte/pull/67437) | Update dependencies |
| 0.0.20 | 2025-09-30 | [66918](https://github.com/airbytehq/airbyte/pull/66918) | Update dependencies |
| 0.0.19 | 2025-09-24 | [66254](https://github.com/airbytehq/airbyte/pull/66254) | Update dependencies |
| 0.0.18 | 2025-08-24 | [65451](https://github.com/airbytehq/airbyte/pull/65451) | Update dependencies |
| 0.0.17 | 2025-08-16 | [65037](https://github.com/airbytehq/airbyte/pull/65037) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64416](https://github.com/airbytehq/airbyte/pull/64416) | Update dependencies |
| 0.0.15 | 2025-07-26 | [64009](https://github.com/airbytehq/airbyte/pull/64009) | Update dependencies |
| 0.0.14 | 2025-07-20 | [63666](https://github.com/airbytehq/airbyte/pull/63666) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63048](https://github.com/airbytehq/airbyte/pull/63048) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62678](https://github.com/airbytehq/airbyte/pull/62678) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62226](https://github.com/airbytehq/airbyte/pull/62226) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61815](https://github.com/airbytehq/airbyte/pull/61815) | Update dependencies |
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
