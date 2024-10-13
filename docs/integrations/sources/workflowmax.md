# Workflowmax
Website: https://app.workflowmax2.com/
API Documentation: https://app.swaggerhub.com/apis-docs/WorkflowMax-BlueRock/WorkflowMax-BlueRock-OpenAPI3/0.1#/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |
| `account_id` | `string` | Account ID. The account id for workflowmax |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| stafflist | UUID | DefaultPaginator | ✅ |  ❌  |
| clientlist | UUID | DefaultPaginator | ✅ |  ❌  |
| clients_documents | uuid | No pagination | ✅ |  ❌  |
| clientgrouplist | UUID | DefaultPaginator | ✅ |  ❌  |
| costlist | UUID | DefaultPaginator | ✅ |  ❌  |
| invoice_current | UUID | DefaultPaginator | ✅ |  ❌  |
| invoicelist | UUID | DefaultPaginator | ✅ |  ✅  |
| joblist | UUID | DefaultPaginator | ✅ |  ✅  |
| job_tasks | UUID | DefaultPaginator | ✅ |  ✅  |
| leadlist | UUID | DefaultPaginator | ✅ |  ✅  |
| purchaseorderlist | ID | DefaultPaginator | ✅ |  ✅  |
| tasklist | UUID | DefaultPaginator | ✅ |  ❌  |
| quotelist | UUID | DefaultPaginator | ✅ |  ✅  |
| supplierlist | UUID | DefaultPaginator | ✅ |  ❌  |
| timelist | UUID | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-13 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
