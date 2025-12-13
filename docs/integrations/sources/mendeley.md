# Mendeley
Website: https://www.mendeley.com/
API Reference: https://dev.mendeley.com/methods/#introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. Could be found at `https://dev.mendeley.com/myapps.html` |  |
| `start_date` | `string` | Start date.  |  |
| `client_secret` | `string` | Client secret. Could be found at `https://dev.mendeley.com/myapps.html` |  |
| `query_for_catalog` | `string` | Query for catalog search. Query for catalog search | Polar Bear |
| `client_refresh_token` | `string` | Refresh token. Use cURL or Postman with the OAuth 2.0 Authorization tab. Set the Auth URL to https://api.mendeley.com/oauth/authorize, the Token URL to https://api.mendeley.com/oauth/token, and use all as the scope. |  |
| `name_for_institution` | `string` | Name for institution. The name parameter for institutions search | City University |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| annotations | id | DefaultPaginator | ✅ |  ✅  |
| catalog_search | id | DefaultPaginator | ✅ |  ❌  |
| identifier_types | uuid | DefaultPaginator | ✅ |  ❌  |
| profile | id | DefaultPaginator | ✅ |  ✅  |
| trashed | id | DefaultPaginator | ✅ |  ✅  |
| groups | id | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ✅  |
| files | id | DefaultPaginator | ✅ |  ✅  |
| documents | id | DefaultPaginator | ✅ |  ✅  |
| subject_areas | uuid | DefaultPaginator | ✅ |  ❌  |
| institutions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.25 | 2025-12-09 | [70789](https://github.com/airbytehq/airbyte/pull/70789) | Update dependencies |
| 0.0.24 | 2025-11-25 | [70120](https://github.com/airbytehq/airbyte/pull/70120) | Update dependencies |
| 0.0.23 | 2025-11-18 | [69540](https://github.com/airbytehq/airbyte/pull/69540) | Update dependencies |
| 0.0.22 | 2025-10-29 | [69050](https://github.com/airbytehq/airbyte/pull/69050) | Update dependencies |
| 0.0.21 | 2025-10-21 | [68448](https://github.com/airbytehq/airbyte/pull/68448) | Update dependencies |
| 0.0.20 | 2025-10-14 | [67848](https://github.com/airbytehq/airbyte/pull/67848) | Update dependencies |
| 0.0.19 | 2025-10-07 | [67392](https://github.com/airbytehq/airbyte/pull/67392) | Update dependencies |
| 0.0.18 | 2025-09-30 | [66348](https://github.com/airbytehq/airbyte/pull/66348) | Update dependencies |
| 0.0.17 | 2025-09-09 | [65818](https://github.com/airbytehq/airbyte/pull/65818) | Update dependencies |
| 0.0.16 | 2025-08-23 | [65207](https://github.com/airbytehq/airbyte/pull/65207) | Update dependencies |
| 0.0.15 | 2025-08-09 | [64782](https://github.com/airbytehq/airbyte/pull/64782) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64273](https://github.com/airbytehq/airbyte/pull/64273) | Update dependencies |
| 0.0.13 | 2025-07-26 | [63851](https://github.com/airbytehq/airbyte/pull/63851) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63433](https://github.com/airbytehq/airbyte/pull/63433) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63166](https://github.com/airbytehq/airbyte/pull/63166) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62565](https://github.com/airbytehq/airbyte/pull/62565) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62155](https://github.com/airbytehq/airbyte/pull/62155) | Update dependencies |
| 0.0.8 | 2025-06-21 | [61865](https://github.com/airbytehq/airbyte/pull/61865) | Update dependencies |
| 0.0.7 | 2025-06-14 | [61154](https://github.com/airbytehq/airbyte/pull/61154) | Update dependencies |
| 0.0.6 | 2025-05-24 | [59843](https://github.com/airbytehq/airbyte/pull/59843) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59297](https://github.com/airbytehq/airbyte/pull/59297) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58827](https://github.com/airbytehq/airbyte/pull/58827) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58180](https://github.com/airbytehq/airbyte/pull/58180) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57676](https://github.com/airbytehq/airbyte/pull/57676) | Update dependencies |
| 0.0.1 | 2025-04-08 | [57512](https://github.com/airbytehq/airbyte/pull/57512) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
