# Freightview
An **Airbyte connector for Freightview** enables seamless data integration by extracting and syncing shipping data from Freightview to your target data warehouses or applications. This connector automates the retrieval of essential shipping details, such as quotes, tracking, and shipment reports, allowing businesses to efficiently analyze and manage logistics operations in a centralized system.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| shipments | shipmentId | DefaultPaginator | ✅ |  ❌  |
| quotes | quoteId | No pagination | ✅ |  ❌  |
| tracking | createdDate | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.40 | 2025-12-09 | [70553](https://github.com/airbytehq/airbyte/pull/70553) | Update dependencies |
| 0.0.39 | 2025-11-25 | [69996](https://github.com/airbytehq/airbyte/pull/69996) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69440](https://github.com/airbytehq/airbyte/pull/69440) | Update dependencies |
| 0.0.37 | 2025-10-29 | [68782](https://github.com/airbytehq/airbyte/pull/68782) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68452](https://github.com/airbytehq/airbyte/pull/68452) | Update dependencies |
| 0.0.35 | 2025-10-14 | [68077](https://github.com/airbytehq/airbyte/pull/68077) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67309](https://github.com/airbytehq/airbyte/pull/67309) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66771](https://github.com/airbytehq/airbyte/pull/66771) | Update dependencies |
| 0.0.32 | 2025-09-24 | [65866](https://github.com/airbytehq/airbyte/pull/65866) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65262](https://github.com/airbytehq/airbyte/pull/65262) | Update dependencies |
| 0.0.30 | 2025-08-16 | [64759](https://github.com/airbytehq/airbyte/pull/64759) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63999](https://github.com/airbytehq/airbyte/pull/63999) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63561](https://github.com/airbytehq/airbyte/pull/63561) | Update dependencies |
| 0.0.27 | 2025-07-12 | [62960](https://github.com/airbytehq/airbyte/pull/62960) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62778](https://github.com/airbytehq/airbyte/pull/62778) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62302](https://github.com/airbytehq/airbyte/pull/62302) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61974](https://github.com/airbytehq/airbyte/pull/61974) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61211](https://github.com/airbytehq/airbyte/pull/61211) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60377](https://github.com/airbytehq/airbyte/pull/60377) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59930](https://github.com/airbytehq/airbyte/pull/59930) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59377](https://github.com/airbytehq/airbyte/pull/59377) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58842](https://github.com/airbytehq/airbyte/pull/58842) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58344](https://github.com/airbytehq/airbyte/pull/58344) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57828](https://github.com/airbytehq/airbyte/pull/57828) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57240](https://github.com/airbytehq/airbyte/pull/57240) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56469](https://github.com/airbytehq/airbyte/pull/56469) | Update dependencies |
| 0.0.14 | 2025-03-22 | [55984](https://github.com/airbytehq/airbyte/pull/55984) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55345](https://github.com/airbytehq/airbyte/pull/55345) | Update dependencies |
| 0.0.12 | 2025-03-01 | [54948](https://github.com/airbytehq/airbyte/pull/54948) | Update dependencies |
| 0.0.11 | 2025-02-22 | [54449](https://github.com/airbytehq/airbyte/pull/54449) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53752](https://github.com/airbytehq/airbyte/pull/53752) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53372](https://github.com/airbytehq/airbyte/pull/53372) | Update dependencies |
| 0.0.8 | 2025-02-01 | [52799](https://github.com/airbytehq/airbyte/pull/52799) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52343](https://github.com/airbytehq/airbyte/pull/52343) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51671](https://github.com/airbytehq/airbyte/pull/51671) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51106](https://github.com/airbytehq/airbyte/pull/51106) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50520](https://github.com/airbytehq/airbyte/pull/50520) | Update dependencies |
| 0.0.3 | 2024-12-21 | [49502](https://github.com/airbytehq/airbyte/pull/49502) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49201](https://github.com/airbytehq/airbyte/pull/49201) | Update dependencies |
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
