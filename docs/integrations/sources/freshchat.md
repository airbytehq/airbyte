# Freshchat
Freshchat is a cloud based messaging solution that allows you to effectively interact with your business users. It provides an efficient messaging service for lead generation, customer engagement, and customer support and thereby, makes your business competent.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `account_name` | `string` | Account Name. The unique account name for your Freshchat instance |  |

To get started, and obtain the API key;
- navigate to Admin > CONFIGURE > API Tokens page
- click the Generate Token button. The authentication server returns the access token.

See more in the [API doc](https://developers.freshchat.com/api/#authentication)

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | account_id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| users_conversations | id | No pagination | ✅ |  ❌  |
| conversations | conversation_id | No pagination | ✅ |  ✅  |
| conversations_messages | id | DefaultPaginator | ✅ |  ✅  |
| conversations_properties | id | No pagination | ✅ |  ❌  |
| agents | id | DefaultPaginator | ✅ |  ✅  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| channels | id | DefaultPaginator | ✅ |  ✅  |
| roles | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-22 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
