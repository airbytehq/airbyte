# Coassemble
Coassemble is an online training tool that connects people with the information they need - anytime, anyplace.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `user_token` | `string` | User Token.  |  |
| `user_id` | `string` | User ID.  |  |

See the [Coassemble API docs](https://developers.coassemble.com/get-started) for more information to get started and generate API credentials.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| courses | id | DefaultPaginator | ✅ |  ❌  |
| screen_types | - | NoPaginator | ✅ |  ❌  |
| trackings | - | DefaultPaginator | ✅ |  ❌  |

⚠️⚠️ Note: The `screen_types` and `trackings` streams are **Available on request only** as per the [API docs](https://developers.coassemble.com/get-started). Hence, enabling them without having them enabled on the API side would result in errors. ⚠️⚠️

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-19 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
