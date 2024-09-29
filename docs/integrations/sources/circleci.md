# Circleci
Website: https://app.circleci.com/
API Docs: 
- v1-https://circleci.com/docs/api/v1/index.html
- v2-https://circleci.com/docs/api/v2/index.html
API page: https://app.circleci.com/settings/user/tokens

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `org_id` | `string` | Organization ID. The org ID found in `https://app.circleci.com/settings/organization/circleci/xxxxx/overview` |  |
| `start_date` | `string` | Start date.  |  |
| `organizational_slug` | `string` | Organizational slug. Organizational slug |  |
| `project_slug` | `string` | Project slug. Project slug for getting information about it |  |

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

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-29 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>