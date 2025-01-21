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
| 0.0.11 | 2025-01-18 | [51880](https://github.com/airbytehq/airbyte/pull/51880) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51302](https://github.com/airbytehq/airbyte/pull/51302) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50714](https://github.com/airbytehq/airbyte/pull/50714) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50233](https://github.com/airbytehq/airbyte/pull/50233) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49711](https://github.com/airbytehq/airbyte/pull/49711) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49359](https://github.com/airbytehq/airbyte/pull/49359) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49059](https://github.com/airbytehq/airbyte/pull/49059) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48249](https://github.com/airbytehq/airbyte/pull/48249) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47876](https://github.com/airbytehq/airbyte/pull/47876) | Update dependencies |
| 0.0.2 | 2024-10-22 | [47235](https://github.com/airbytehq/airbyte/pull/47235) | Update dependencies |
| 0.0.1 | 2024-09-05 | [45159](https://github.com/airbytehq/airbyte/pull/45159) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
