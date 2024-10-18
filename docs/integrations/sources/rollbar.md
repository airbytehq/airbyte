# Rollbar
Rollbar is a comprehensive code improvement platform that helps developers to improve their code and deliver the best applications to individual customers in real-time. The platform enables users to proactively discover, predict and resolve errors in no time besides deploying apps with confidence.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `project_access_token` | `string` | Project Access Token.  |  |
| `start_date` | `string` | Start date.  |  |
| `account_access_token` | `string` | Account Access Token.  |  |

To get started you need two access tokens;
- `Account Access Token` for Account level streams (`projects`, `teams`, `users`) and,
- `Project Access Token` for Project level streams.

Follow [this guide](https://docs.rollbar.com/reference/getting-started-1#authentication) to retrieve them.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| items | id | DefaultPaginator | ✅ |  ✅  |
| occurrences | id | DefaultPaginator | ✅ |  ✅  |
| items_metrics | item_counter | No pagination | ✅ |  ❌  |
| deploys | id | DefaultPaginator | ✅ |  ✅  |
| environments | id | DefaultPaginator | ✅ |  ❌  |
| rql_jobs | id | DefaultPaginator | ✅ |  ✅  |
| top_active_items | id | No pagination | ✅ |  ❌  |
| projects | id | No pagination | ✅ |  ✅  |
| teams | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-24 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
