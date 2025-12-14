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
| 0.0.46 | 2025-12-09 | [70478](https://github.com/airbytehq/airbyte/pull/70478) | Update dependencies |
| 0.0.45 | 2025-11-25 | [69992](https://github.com/airbytehq/airbyte/pull/69992) | Update dependencies |
| 0.0.44 | 2025-11-18 | [69665](https://github.com/airbytehq/airbyte/pull/69665) | Update dependencies |
| 0.0.43 | 2025-10-29 | [68974](https://github.com/airbytehq/airbyte/pull/68974) | Update dependencies |
| 0.0.42 | 2025-10-21 | [68249](https://github.com/airbytehq/airbyte/pull/68249) | Update dependencies |
| 0.0.41 | 2025-10-14 | [67815](https://github.com/airbytehq/airbyte/pull/67815) | Update dependencies |
| 0.0.40 | 2025-10-07 | [67491](https://github.com/airbytehq/airbyte/pull/67491) | Update dependencies |
| 0.0.39 | 2025-09-30 | [66966](https://github.com/airbytehq/airbyte/pull/66966) | Update dependencies |
| 0.0.38 | 2025-09-23 | [66416](https://github.com/airbytehq/airbyte/pull/66416) | Update dependencies |
| 0.0.37 | 2025-09-09 | [65761](https://github.com/airbytehq/airbyte/pull/65761) | Update dependencies |
| 0.0.36 | 2025-08-23 | [65167](https://github.com/airbytehq/airbyte/pull/65167) | Update dependencies |
| 0.0.35 | 2025-08-09 | [64674](https://github.com/airbytehq/airbyte/pull/64674) | Update dependencies |
| 0.0.34 | 2025-08-02 | [64183](https://github.com/airbytehq/airbyte/pull/64183) | Update dependencies |
| 0.0.33 | 2025-07-26 | [63840](https://github.com/airbytehq/airbyte/pull/63840) | Update dependencies |
| 0.0.32 | 2025-07-19 | [63429](https://github.com/airbytehq/airbyte/pull/63429) | Update dependencies |
| 0.0.31 | 2025-07-12 | [63163](https://github.com/airbytehq/airbyte/pull/63163) | Update dependencies |
| 0.0.30 | 2025-07-05 | [62564](https://github.com/airbytehq/airbyte/pull/62564) | Update dependencies |
| 0.0.29 | 2025-06-28 | [62340](https://github.com/airbytehq/airbyte/pull/62340) | Update dependencies |
| 0.0.28 | 2025-06-21 | [61927](https://github.com/airbytehq/airbyte/pull/61927) | Update dependencies |
| 0.0.27 | 2025-06-14 | [61058](https://github.com/airbytehq/airbyte/pull/61058) | Update dependencies |
| 0.0.26 | 2025-05-24 | [60512](https://github.com/airbytehq/airbyte/pull/60512) | Update dependencies |
| 0.0.25 | 2025-05-10 | [60152](https://github.com/airbytehq/airbyte/pull/60152) | Update dependencies |
| 0.0.24 | 2025-05-04 | [59506](https://github.com/airbytehq/airbyte/pull/59506) | Update dependencies |
| 0.0.23 | 2025-04-27 | [59101](https://github.com/airbytehq/airbyte/pull/59101) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58461](https://github.com/airbytehq/airbyte/pull/58461) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57886](https://github.com/airbytehq/airbyte/pull/57886) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57346](https://github.com/airbytehq/airbyte/pull/57346) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56747](https://github.com/airbytehq/airbyte/pull/56747) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56200](https://github.com/airbytehq/airbyte/pull/56200) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55520](https://github.com/airbytehq/airbyte/pull/55520) | Update dependencies |
| 0.0.16 | 2025-03-01 | [55047](https://github.com/airbytehq/airbyte/pull/55047) | Update dependencies |
| 0.0.15 | 2025-02-23 | [54617](https://github.com/airbytehq/airbyte/pull/54617) | Update dependencies |
| 0.0.14 | 2025-02-15 | [54000](https://github.com/airbytehq/airbyte/pull/54000) | Update dependencies |
| 0.0.13 | 2025-02-08 | [52955](https://github.com/airbytehq/airbyte/pull/52955) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52534](https://github.com/airbytehq/airbyte/pull/52534) | Update dependencies |
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
