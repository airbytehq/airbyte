# Gmail
Gmail is the email service provided by Google.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `include_spam_and_trash` | `boolean` | Include Spam &amp; Trash. Include drafts/messages from SPAM and TRASH in the results. Defaults to false. | false |

Note that this connector uses the Google API OAuth2.0 for authentication. To get started, follow the steps [here](https://developers.google.com/gmail/api/auth/web-server#create_a_client_id_and_client_secret) to retrieve `client_id` and `client_secret`. See [here](https://developers.google.com/identity/protocols/oauth2/web-server) for more detailed guide on the OAuth flow to retrieve the `client_refresh_token`.

**Also note that the scope required here is `https://www.googleapis.com/auth/gmail.readonly`**

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
