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
| 0.0.3 | 2024-12-14 | [49562](https://github.com/airbytehq/airbyte/pull/49562) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48953](https://github.com/airbytehq/airbyte/pull/48953) | Update dependencies |
| 0.0.1 | 2024-10-16 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
