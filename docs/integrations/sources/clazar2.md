# Clazar


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| buyers | id | DefaultPaginator | ✅ |  ✅  |
| listings | id | DefaultPaginator | ✅ |  ✅  |
| contracts | id | DefaultPaginator | ✅ |  ✅  |
| opportunities | id | DefaultPaginator | ✅ |  ✅  |
| private_offers | id | DefaultPaginator | ✅ |  ✅  |
| analytics_aws_marketplace_disbursements |  | DefaultPaginator | ✅ |  ❌  |
| analytics_aws_marketplace_revenue |  | DefaultPaginator | ✅ |  ❌  |
| analytics_aws_cosell_opportunities |  | DefaultPaginator | ✅ |  ❌  |
| analytics_azure_marketplace_revenue |  | DefaultPaginator | ✅ |  ❌  |
| analytics_azure_marketplace_customers |  | DefaultPaginator | ✅ |  ❌  |
| analytics_azure_marketplace_orders |  | DefaultPaginator | ✅ |  ❌  |
| analytics_azure_marketplace_metered_usage |  | DefaultPaginator | ✅ |  ❌  |
| analytics_azure_cosell_opportunities |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_disbursements |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_disbursements_summary |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_charges_and_usage |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_daily_insights |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_incremental_daily_insights |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_monthly_insights |  | DefaultPaginator | ✅ |  ❌  |
| analytics_gcp_marketplace_incremental_monthly_insights |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-27 | Initial release by [@prashant-mittal9](https://github.com/prashant-mittal9) via Connector Builder|

</details>