# Circleci
This directory contains the manifest-only connector for [`source-circleci`](https://app.circleci.com/).

## Documentation reference:
- Visit `https://circleci.com/docs/api/v1/index.html` for V1 API documentation
- Visit `https://circleci.com/docs/api/v2/index.html` for V2 API documentation

## Authentication setup
`CircleCI` uses api key authentication, Visit `https://app.circleci.com/settings/user/tokens` for getting your api keys.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `org_id` | `string` | Organization ID. The org ID found in `https://app.circleci.com/settings/organization/circleci/xxxxx/overview` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| context | id | DefaultPaginator | ✅ |  ✅  |
| self_ids | id | DefaultPaginator | ✅ |  ❌  |
| self_collaborations | id | DefaultPaginator | ✅ |  ❌  |
| me | analytics_id | DefaultPaginator | ✅ |  ✅  |
| projects | vcs_url | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       |PR| Subject        |
|------------------|------------|---|----------------|
| 0.0.1 | 2024-09-29 |[46249](https://github.com/airbytehq/airbyte/pull/46249)| Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>