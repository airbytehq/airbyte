# Picqer
  Website: https://picqer.com/
  Authentication Docs:
  https://picqer.com/en/api#h-authentication
  API Docs: https://picqer.com/en/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `organization_name` | `string` | Organization Name. The organization name which is used to login to picqer |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | idcustomer | DefaultPaginator | ✅ |  ❌  |
| products | idproduct | DefaultPaginator | ✅ |  ✅  |
| products_stock |  | DefaultPaginator | ✅ |  ❌  |
| orders | idorder | DefaultPaginator | ✅ |  ✅  |
| backorders | idbackorder | DefaultPaginator | ✅ |  ✅  |
| returns | idreturn | DefaultPaginator | ✅ |  ✅  |
| purchaseorders | idpurchaseorder | DefaultPaginator | ✅ |  ✅  |
| locations | idlocation | DefaultPaginator | ✅ |  ❌  |
| warehouses | idwarehouse | DefaultPaginator | ✅ |  ❌  |
| users | iduser | DefaultPaginator | ✅ |  ✅  |
| suppliers | idsupplier | DefaultPaginator | ✅ |  ❌  |
| tags | idtag | DefaultPaginator | ✅ |  ❌  |
| templates | idtemplate | DefaultPaginator | ✅ |  ❌  |
| vatgroups | idvatgroup | DefaultPaginator | ✅ |  ❌  |
| stats |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-05 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>