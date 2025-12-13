# Bugsnag
BugSnag is an error monitoring and reporting software with best-in-class functionality for mobile apps.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `auth_token` | `string` | Auth Token. Personal auth token for accessing the Bugsnag API. Generate it in the My Account section of Bugsnag settings. |  |
| `start_date` | `string` | Start date.  |  |

You need to generate the `auth_token` to get started. Personal Auth Tokens can be generated in the My Account section of [Bugsnag settings](https://app.bugsnag.com/settings/my-account). For more details, [see here](https://bugsnagapiv2.docs.apiary.io/#introduction/authentication).

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ✅  |
| saved_searches | id | No pagination | ✅ |  ❌  |
| saved_searches_usage_summary |  | No pagination | ✅ |  ❌  |
| errors | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| pivots | event_field_display_id.project_id | No pagination | ✅ |  ❌  |
| supported_integrations | key | No pagination | ✅ |  ❌  |
| collaborators | id | No pagination | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| event_fields | display_id.project_id | No pagination | ✅ |  ❌  |
| releases | id | DefaultPaginator | ✅ |  ✅  |
| trace_fields | display_id.project_id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.36 | 2025-12-09 | [70649](https://github.com/airbytehq/airbyte/pull/70649) | Update dependencies |
| 0.0.35 | 2025-11-25 | [69947](https://github.com/airbytehq/airbyte/pull/69947) | Update dependencies |
| 0.0.34 | 2025-11-18 | [69461](https://github.com/airbytehq/airbyte/pull/69461) | Update dependencies |
| 0.0.33 | 2025-10-29 | [68723](https://github.com/airbytehq/airbyte/pull/68723) | Update dependencies |
| 0.0.32 | 2025-10-21 | [68253](https://github.com/airbytehq/airbyte/pull/68253) | Update dependencies |
| 0.0.31 | 2025-10-14 | [67811](https://github.com/airbytehq/airbyte/pull/67811) | Update dependencies |
| 0.0.30 | 2025-10-07 | [67209](https://github.com/airbytehq/airbyte/pull/67209) | Update dependencies |
| 0.0.29 | 2025-09-30 | [66325](https://github.com/airbytehq/airbyte/pull/66325) | Update dependencies |
| 0.0.28 | 2025-09-09 | [66031](https://github.com/airbytehq/airbyte/pull/66031) | Update dependencies |
| 0.0.27 | 2025-08-16 | [65049](https://github.com/airbytehq/airbyte/pull/65049) | Update dependencies |
| 0.0.26 | 2025-07-26 | [63788](https://github.com/airbytehq/airbyte/pull/63788) | Update dependencies |
| 0.0.25 | 2025-07-19 | [63462](https://github.com/airbytehq/airbyte/pull/63462) | Update dependencies |
| 0.0.24 | 2025-07-12 | [63031](https://github.com/airbytehq/airbyte/pull/63031) | Update dependencies |
| 0.0.23 | 2025-06-28 | [60649](https://github.com/airbytehq/airbyte/pull/60649) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59869](https://github.com/airbytehq/airbyte/pull/59869) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59352](https://github.com/airbytehq/airbyte/pull/59352) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58750](https://github.com/airbytehq/airbyte/pull/58750) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58269](https://github.com/airbytehq/airbyte/pull/58269) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57596](https://github.com/airbytehq/airbyte/pull/57596) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57128](https://github.com/airbytehq/airbyte/pull/57128) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56556](https://github.com/airbytehq/airbyte/pull/56556) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56143](https://github.com/airbytehq/airbyte/pull/56143) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55360](https://github.com/airbytehq/airbyte/pull/55360) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54891](https://github.com/airbytehq/airbyte/pull/54891) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54280](https://github.com/airbytehq/airbyte/pull/54280) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53885](https://github.com/airbytehq/airbyte/pull/53885) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53412](https://github.com/airbytehq/airbyte/pull/53412) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52911](https://github.com/airbytehq/airbyte/pull/52911) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52165](https://github.com/airbytehq/airbyte/pull/52165) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51714](https://github.com/airbytehq/airbyte/pull/51714) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51233](https://github.com/airbytehq/airbyte/pull/51233) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50452](https://github.com/airbytehq/airbyte/pull/50452) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50163](https://github.com/airbytehq/airbyte/pull/50163) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49562](https://github.com/airbytehq/airbyte/pull/49562) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48953](https://github.com/airbytehq/airbyte/pull/48953) | Update dependencies |
| 0.0.1 | 2024-10-16 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
