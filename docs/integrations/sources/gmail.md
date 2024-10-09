# Gmail
Gmail is the email service provided by Google.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `includeSpamTrash` | `boolean` | Include Spam &amp; Trash. Include drafts/messages from SPAM and TRASH in the results. Defaults to false. | false |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| profile |  | No pagination | ✅ |  ❌  |
| drafts | id | DefaultPaginator | ✅ |  ❌  |
| labels | id | No pagination | ✅ |  ❌  |
| labels_details | id | No pagination | ✅ |  ❌  |
| messages | id | DefaultPaginator | ✅ |  ❌  |
| messages_details | id | No pagination | ✅ |  ❌  |
| threads | id | DefaultPaginator | ✅ |  ❌  |
| threads_details | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-09 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
