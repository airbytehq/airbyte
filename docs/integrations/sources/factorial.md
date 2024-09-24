# Factorial
Website: https://app.factorialhr.com/
API Docs: https://apidoc.factorialhr.com/reference
Auth Docs: https://apidoc.factorialhr.com/docs/api-keys
API Keys: https://app.factorialhr.com/settings/api-keys

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| public_credentials | id | DefaultPaginator | ✅ |  ❌  |
| webhook_subscriptions | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ✅  |
| schedules | id | DefaultPaginator | ✅ |  ✅  |
| overlap_periods | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| memberships | id | DefaultPaginator | ✅ |  ❌  |
| allowances | id | DefaultPaginator | ✅ |  ❌  |
| blocked_periods | id | DefaultPaginator | ✅ |  ❌  |
| leaves | id | DefaultPaginator | ✅ |  ✅  |
| leave_types | id | DefaultPaginator | ✅ |  ❌  |
| policies | id | DefaultPaginator | ✅ |  ❌  |
| break_configurations | id | DefaultPaginator | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| legal_entities | id | DefaultPaginator | ✅ |  ❌  |
| contract_versions | id | DefaultPaginator | ✅ |  ❌  |
| reference_contracts | id | DefaultPaginator | ✅ |  ❌  |
| taxonomies | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |
| fields_options | id | DefaultPaginator | ✅ |  ❌  |
| fields_resource_fields | id | DefaultPaginator | ✅ |  ❌  |
| employees | id | DefaultPaginator | ✅ |  ✅  |
| cost_centers | id | DefaultPaginator | ✅ |  ❌  |
| company_holidays | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| work_areas | id | DefaultPaginator | ✅ |  ❌  |
| shifts | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-24 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>