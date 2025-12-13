# Blogger
Google Blogger is a free blogging platform by Google that allows users to create and manage their own blogs with ease. It offers customizable templates, user-friendly tools, and integration with other Google services, making it simple to publish content and reach a wide audience. 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| blogs | id | DefaultPaginator | ✅ |  ❌  |
| posts |  | DefaultPaginator | ✅ |  ❌  |
| pages | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.35 | 2025-12-09 | [70654](https://github.com/airbytehq/airbyte/pull/70654) | Update dependencies |
| 0.0.34 | 2025-11-25 | [69950](https://github.com/airbytehq/airbyte/pull/69950) | Update dependencies |
| 0.0.33 | 2025-11-18 | [69493](https://github.com/airbytehq/airbyte/pull/69493) | Update dependencies |
| 0.0.32 | 2025-10-29 | [68738](https://github.com/airbytehq/airbyte/pull/68738) | Update dependencies |
| 0.0.31 | 2025-10-21 | [68271](https://github.com/airbytehq/airbyte/pull/68271) | Update dependencies |
| 0.0.30 | 2025-10-14 | [67844](https://github.com/airbytehq/airbyte/pull/67844) | Update dependencies |
| 0.0.29 | 2025-10-07 | [67200](https://github.com/airbytehq/airbyte/pull/67200) | Update dependencies |
| 0.0.28 | 2025-09-30 | [66321](https://github.com/airbytehq/airbyte/pull/66321) | Update dependencies |
| 0.0.27 | 2025-08-16 | [65048](https://github.com/airbytehq/airbyte/pull/65048) | Update dependencies |
| 0.0.26 | 2025-07-26 | [63795](https://github.com/airbytehq/airbyte/pull/63795) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62530](https://github.com/airbytehq/airbyte/pull/62530) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61887](https://github.com/airbytehq/airbyte/pull/61887) | Update dependencies |
| 0.0.23 | 2025-06-15 | [60602](https://github.com/airbytehq/airbyte/pull/60602) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59841](https://github.com/airbytehq/airbyte/pull/59841) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59355](https://github.com/airbytehq/airbyte/pull/59355) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58736](https://github.com/airbytehq/airbyte/pull/58736) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58258](https://github.com/airbytehq/airbyte/pull/58258) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57632](https://github.com/airbytehq/airbyte/pull/57632) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57116](https://github.com/airbytehq/airbyte/pull/57116) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56571](https://github.com/airbytehq/airbyte/pull/56571) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56134](https://github.com/airbytehq/airbyte/pull/56134) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55358](https://github.com/airbytehq/airbyte/pull/55358) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54836](https://github.com/airbytehq/airbyte/pull/54836) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54220](https://github.com/airbytehq/airbyte/pull/54220) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53903](https://github.com/airbytehq/airbyte/pull/53903) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53435](https://github.com/airbytehq/airbyte/pull/53435) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52921](https://github.com/airbytehq/airbyte/pull/52921) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52161](https://github.com/airbytehq/airbyte/pull/52161) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51746](https://github.com/airbytehq/airbyte/pull/51746) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51242](https://github.com/airbytehq/airbyte/pull/51242) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50441](https://github.com/airbytehq/airbyte/pull/50441) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50162](https://github.com/airbytehq/airbyte/pull/50162) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49578](https://github.com/airbytehq/airbyte/pull/49578) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49012](https://github.com/airbytehq/airbyte/pull/49012) | Update dependencies |
| 0.0.1 | 2024-11-09 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
