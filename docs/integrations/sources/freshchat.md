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
| 0.0.6 | 2025-03-08 | [55295](https://github.com/airbytehq/airbyte/pull/55295) | Update dependencies |
| 0.0.5 | 2025-03-01 | [54991](https://github.com/airbytehq/airbyte/pull/54991) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54427](https://github.com/airbytehq/airbyte/pull/54427) | Update dependencies |
| 0.0.3 | 2025-02-15 | [53784](https://github.com/airbytehq/airbyte/pull/53784) | Update dependencies |
| 0.0.2 | 2025-02-08 | [47591](https://github.com/airbytehq/airbyte/pull/47591) | Update dependencies |
| 0.0.1 | 2024-09-22 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
