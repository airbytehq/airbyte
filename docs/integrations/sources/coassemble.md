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
| 0.0.11 | 2025-02-01 | [52795](https://github.com/airbytehq/airbyte/pull/52795) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52339](https://github.com/airbytehq/airbyte/pull/52339) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51699](https://github.com/airbytehq/airbyte/pull/51699) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51123](https://github.com/airbytehq/airbyte/pull/51123) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50570](https://github.com/airbytehq/airbyte/pull/50570) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50025](https://github.com/airbytehq/airbyte/pull/50025) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49483](https://github.com/airbytehq/airbyte/pull/49483) | Update dependencies |
| 0.0.4 | 2024-12-12 | [48926](https://github.com/airbytehq/airbyte/pull/48926) | Update dependencies |
| 0.0.3 | 2024-11-04 | [47865](https://github.com/airbytehq/airbyte/pull/47865) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47526](https://github.com/airbytehq/airbyte/pull/47526) | Update dependencies |
| 0.0.1 | 2024-09-19 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
