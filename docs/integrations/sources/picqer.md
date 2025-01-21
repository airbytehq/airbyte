# Picqer

This page contains the setup guide and reference information for the [Picqer](https://picqer.com/) source connector.

## Prerequisites

Picqer user basic http for its authentication, follow the [API documentation](https://picqer.com/en/api/) and visit settings page to get your api key.
Configure the API key as your username and leave password field as blank

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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-05 | [45159](https://github.com/airbytehq/airbyte/pull/45159) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>