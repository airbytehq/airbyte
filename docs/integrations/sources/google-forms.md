# Google Forms
Google Forms is a free online tool from Google that allows users to create custom surveys, quizzes, and forms. It enables easy collection and organization of data by automating responses into a connected Google Sheets spreadsheet. With Google Forms, you can design forms with various question types, share them via email or links, and track responses in real-time, making it ideal for feedback collection, event registration, or educational assessments.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `form_id` | `array` | Forms IDs.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | `formId` | No pagination | ✅ |  ❌  |
| form_responses | `responseId` | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.13 | 2025-03-08 | [55328](https://github.com/airbytehq/airbyte/pull/55328) | Update dependencies |
| 0.0.12 | 2025-03-01 | [54933](https://github.com/airbytehq/airbyte/pull/54933) | Update dependencies |
| 0.0.11 | 2025-02-22 | [54429](https://github.com/airbytehq/airbyte/pull/54429) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53728](https://github.com/airbytehq/airbyte/pull/53728) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53376](https://github.com/airbytehq/airbyte/pull/53376) | Update dependencies |
| 0.0.8 | 2025-02-01 | [52821](https://github.com/airbytehq/airbyte/pull/52821) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52298](https://github.com/airbytehq/airbyte/pull/52298) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51676](https://github.com/airbytehq/airbyte/pull/51676) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51057](https://github.com/airbytehq/airbyte/pull/51057) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50568](https://github.com/airbytehq/airbyte/pull/50568) | Update dependencies |
| 0.0.3 | 2024-12-21 | [49501](https://github.com/airbytehq/airbyte/pull/49501) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48967](https://github.com/airbytehq/airbyte/pull/48967) | Update dependencies |
| 0.0.1 | 2024-11-09 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
