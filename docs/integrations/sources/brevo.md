# Brevo
Website: https://www.brevo.com/
Auth page: https://app.brevo.com/settings/keys/api
API Docs: https://developers.brevo.com/reference/getting-started-1

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| contacts_attributes |  | DefaultPaginator | ✅ |  ❌  |
| contacts_folders_lists | id | DefaultPaginator | ✅ |  ❌  |
| contacts_folders | id | DefaultPaginator | ✅ |  ❌  |
| contacts_segments | id | DefaultPaginator | ✅ |  ✅  |
| contacts_lists_contacts |  | DefaultPaginator | ✅ |  ✅  |
| contacts_lists | id | DefaultPaginator | ✅ |  ❌  |
| senders | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ✅  |
| companies_attributes |  | DefaultPaginator | ✅ |  ❌  |
| crm_pipeline_stages | id | DefaultPaginator | ✅ |  ❌  |
| crm_pipeline_details_all | pipeline | DefaultPaginator | ✅ |  ❌  |
| crm_attributes_deals |  | DefaultPaginator | ✅ |  ❌  |
| crm_deals | id | DefaultPaginator | ✅ |  ❌  |
| crm_tasktypes | id | DefaultPaginator | ✅ |  ❌  |
| crm_tasks | id | DefaultPaginator | ✅ |  ✅  |
| crm_notes | id | DefaultPaginator | ✅ |  ✅  |
| domains | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | No pagination | ✅ |  ✅  |
| account | organization_id | DefaultPaginator | ✅ |  ❌  |
| organization_invited_users | email | DefaultPaginator | ✅ |  ❌  |
| emailCampaigns | id | DefaultPaginator | ✅ |  ✅  |
| smsCampaigns | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-11 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>