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
| `project_id` | `string` | Project ID found in the project settings, Visit `https://app.circleci.com/settings/project/circleci/ORG_SLUG/YYYYY`  |  |
| `workflow_id` | `array` | Workflow ID's of project pipelines, Could be seen in the URL of pipeline build, Example `https://app.circleci.com/pipelines/circleci/55555xxxxxx/7yyyyyyyyxxxxx/2/workflows/WORKFLOW_ID`  |  |
| `job_number` | `string` | Job Number of the workflow for `jobs` stream, Auto fetches from `workflow_jobs` stream, if not configured  | `2` |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| context | id | DefaultPaginator | ✅ |  ✅  |
| self_ids | id | DefaultPaginator | ✅ |  ❌  |
| self_collaborations | id | DefaultPaginator | ✅ |  ❌  |
| me | analytics_id | DefaultPaginator | ✅ |  ✅  |
| projects | vcs_url | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ✅ |
| specific_project | id | DefaultPaginator | ✅ |  ❌ |
| jobs | number | DefaultPaginator | ✅ |  ❌ |
| workflow | id | DefaultPaginator | ✅ |  ✅ |
| insights_metrics | project_id | DefaultPaginator | ✅ |  ❌ |
| insights_branches | id | DefaultPaginator | ✅ |  ❌ |
| workflow_jobs | id | DefaultPaginator | ✅ |  ✅ |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       |PR| Subject        |
|------------------|------------|---|----------------|
| 0.1.0 | 2024-10-11 |[46729](https://github.com/airbytehq/airbyte/pull/46729)| Remove unwanted optional config parameters |
| 0.0.1 | 2024-09-29 |[46249](https://github.com/airbytehq/airbyte/pull/46249)| Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>