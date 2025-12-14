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
| 0.0.34 | 2025-12-09 | [70574](https://github.com/airbytehq/airbyte/pull/70574) | Update dependencies |
| 0.0.33 | 2025-11-25 | [69975](https://github.com/airbytehq/airbyte/pull/69975) | Update dependencies |
| 0.0.32 | 2025-11-18 | [69471](https://github.com/airbytehq/airbyte/pull/69471) | Update dependencies |
| 0.0.31 | 2025-10-29 | [68784](https://github.com/airbytehq/airbyte/pull/68784) | Update dependencies |
| 0.0.30 | 2025-10-21 | [68422](https://github.com/airbytehq/airbyte/pull/68422) | Update dependencies |
| 0.0.29 | 2025-10-14 | [68051](https://github.com/airbytehq/airbyte/pull/68051) | Update dependencies |
| 0.0.28 | 2025-10-07 | [67305](https://github.com/airbytehq/airbyte/pull/67305) | Update dependencies |
| 0.0.27 | 2025-09-30 | [66769](https://github.com/airbytehq/airbyte/pull/66769) | Update dependencies |
| 0.0.26 | 2025-09-24 | [66429](https://github.com/airbytehq/airbyte/pull/66429) | Update dependencies |
| 0.0.25 | 2025-09-09 | [65823](https://github.com/airbytehq/airbyte/pull/65823) | Update dependencies |
| 0.0.24 | 2025-08-23 | [65255](https://github.com/airbytehq/airbyte/pull/65255) | Update dependencies |
| 0.0.23 | 2025-08-09 | [64667](https://github.com/airbytehq/airbyte/pull/64667) | Update dependencies |
| 0.0.22 | 2025-08-02 | [64388](https://github.com/airbytehq/airbyte/pull/64388) | Update dependencies |
| 0.0.21 | 2025-07-26 | [64035](https://github.com/airbytehq/airbyte/pull/64035) | Update dependencies |
| 0.0.20 | 2025-07-19 | [63576](https://github.com/airbytehq/airbyte/pull/63576) | Update dependencies |
| 0.0.19 | 2025-07-12 | [62991](https://github.com/airbytehq/airbyte/pull/62991) | Update dependencies |
| 0.0.18 | 2025-07-05 | [62819](https://github.com/airbytehq/airbyte/pull/62819) | Update dependencies |
| 0.0.17 | 2025-06-28 | [62370](https://github.com/airbytehq/airbyte/pull/62370) | Update dependencies |
| 0.0.16 | 2025-06-21 | [61945](https://github.com/airbytehq/airbyte/pull/61945) | Update dependencies |
| 0.0.15 | 2025-06-14 | [61209](https://github.com/airbytehq/airbyte/pull/61209) | Update dependencies |
| 0.0.14 | 2025-05-24 | [60425](https://github.com/airbytehq/airbyte/pull/60425) | Update dependencies |
| 0.0.13 | 2025-05-10 | [60048](https://github.com/airbytehq/airbyte/pull/60048) | Update dependencies |
| 0.0.12 | 2025-05-03 | [59403](https://github.com/airbytehq/airbyte/pull/59403) | Update dependencies |
| 0.0.11 | 2025-04-26 | [58887](https://github.com/airbytehq/airbyte/pull/58887) | Update dependencies |
| 0.0.10 | 2025-04-19 | [57771](https://github.com/airbytehq/airbyte/pull/57771) | Update dependencies |
| 0.0.9 | 2025-04-05 | [57204](https://github.com/airbytehq/airbyte/pull/57204) | Update dependencies |
| 0.0.8 | 2025-03-29 | [56505](https://github.com/airbytehq/airbyte/pull/56505) | Update dependencies |
| 0.0.7 | 2025-03-22 | [55960](https://github.com/airbytehq/airbyte/pull/55960) | Update dependencies |
| 0.0.6 | 2025-03-08 | [55295](https://github.com/airbytehq/airbyte/pull/55295) | Update dependencies |
| 0.0.5 | 2025-03-01 | [54991](https://github.com/airbytehq/airbyte/pull/54991) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54427](https://github.com/airbytehq/airbyte/pull/54427) | Update dependencies |
| 0.0.3 | 2025-02-15 | [53784](https://github.com/airbytehq/airbyte/pull/53784) | Update dependencies |
| 0.0.2 | 2025-02-08 | [47591](https://github.com/airbytehq/airbyte/pull/47591) | Update dependencies |
| 0.0.1 | 2024-09-22 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
