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
| 0.0.1 | 2024-11-09 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
