# Veeqo
Veeqo Airbyte connector for Veeqo enables seamless data integration between Veeqo&#39;s inventory and order management platform and various data warehouses or applications. It allows users to sync Veeqo data such as orders, products, inventory levels, and more, making it easier to analyze and manage e-commerce operations. This connector streamlines data workflows, ensuring up-to-date and accurate information for better business insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orders | id | DefaultPaginator | ✅ |  ✅  |
| returns | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| purchase_orders | id | DefaultPaginator | ✅ |  ❌  |
| suppliers | id | DefaultPaginator | ✅ |  ❌  |
| company |  | DefaultPaginator | ✅ |  ❌  |
| warehouses | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| stores | id | DefaultPaginator | ✅ |  ❌  |
| delivery_methods | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.44 | 2025-12-09 | [70718](https://github.com/airbytehq/airbyte/pull/70718) | Update dependencies |
| 0.0.43 | 2025-11-25 | [70191](https://github.com/airbytehq/airbyte/pull/70191) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69642](https://github.com/airbytehq/airbyte/pull/69642) | Update dependencies |
| 0.0.41 | 2025-10-29 | [68953](https://github.com/airbytehq/airbyte/pull/68953) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68369](https://github.com/airbytehq/airbyte/pull/68369) | Update dependencies |
| 0.0.39 | 2025-10-14 | [67939](https://github.com/airbytehq/airbyte/pull/67939) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67322](https://github.com/airbytehq/airbyte/pull/67322) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66953](https://github.com/airbytehq/airbyte/pull/66953) | Update dependencies |
| 0.0.36 | 2025-09-09 | [65742](https://github.com/airbytehq/airbyte/pull/65742) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65418](https://github.com/airbytehq/airbyte/pull/65418) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64859](https://github.com/airbytehq/airbyte/pull/64859) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64395](https://github.com/airbytehq/airbyte/pull/64395) | Update dependencies |
| 0.0.32 | 2025-07-26 | [64084](https://github.com/airbytehq/airbyte/pull/64084) | Update dependencies |
| 0.0.31 | 2025-07-19 | [63616](https://github.com/airbytehq/airbyte/pull/63616) | Update dependencies |
| 0.0.30 | 2025-07-12 | [63241](https://github.com/airbytehq/airbyte/pull/63241) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62702](https://github.com/airbytehq/airbyte/pull/62702) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62216](https://github.com/airbytehq/airbyte/pull/62216) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61766](https://github.com/airbytehq/airbyte/pull/61766) | Update dependencies |
| 0.0.26 | 2025-06-15 | [61249](https://github.com/airbytehq/airbyte/pull/61249) | Update dependencies |
| 0.0.25 | 2025-05-24 | [60746](https://github.com/airbytehq/airbyte/pull/60746) | Update dependencies |
| 0.0.24 | 2025-05-10 | [60007](https://github.com/airbytehq/airbyte/pull/60007) | Update dependencies |
| 0.0.23 | 2025-05-04 | [59552](https://github.com/airbytehq/airbyte/pull/59552) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58920](https://github.com/airbytehq/airbyte/pull/58920) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58567](https://github.com/airbytehq/airbyte/pull/58567) | Update dependencies |
| 0.0.20 | 2025-04-12 | [58017](https://github.com/airbytehq/airbyte/pull/58017) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57483](https://github.com/airbytehq/airbyte/pull/57483) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56806](https://github.com/airbytehq/airbyte/pull/56806) | Update dependencies |
| 0.0.17 | 2025-03-22 | [55610](https://github.com/airbytehq/airbyte/pull/55610) | Update dependencies |
| 0.0.16 | 2025-03-01 | [55146](https://github.com/airbytehq/airbyte/pull/55146) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54479](https://github.com/airbytehq/airbyte/pull/54479) | Update dependencies |
| 0.0.14 | 2025-02-15 | [54082](https://github.com/airbytehq/airbyte/pull/54082) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53525](https://github.com/airbytehq/airbyte/pull/53525) | Update dependencies |
| 0.0.12 | 2025-02-01 | [53093](https://github.com/airbytehq/airbyte/pull/53093) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52383](https://github.com/airbytehq/airbyte/pull/52383) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51976](https://github.com/airbytehq/airbyte/pull/51976) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51456](https://github.com/airbytehq/airbyte/pull/51456) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50756](https://github.com/airbytehq/airbyte/pull/50756) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50344](https://github.com/airbytehq/airbyte/pull/50344) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49789](https://github.com/airbytehq/airbyte/pull/49789) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49408](https://github.com/airbytehq/airbyte/pull/49408) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48254](https://github.com/airbytehq/airbyte/pull/48254) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47811](https://github.com/airbytehq/airbyte/pull/47811) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47488](https://github.com/airbytehq/airbyte/pull/47488) | Update dependencies |
| 0.0.1 | 2024-10-17 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
