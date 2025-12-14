# Repairshopr
Repairshopr is a CRM and an integrated marketing platform.
With this connector we can extract data from various streams such as customers , invoices and payments.
[API Documentation](https://api-docs.repairshopr.com/)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `subdomain` | `string` | Sub Domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| appointment types | id | No pagination | ✅ |  ❌  |
| appointments | id | DefaultPaginator | ✅ |  ❌  |
| customer assets | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| estimates | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| items | id | DefaultPaginator | ✅ |  ❌  |
| line items | id | DefaultPaginator | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70593](https://github.com/airbytehq/airbyte/pull/70593) | Update dependencies |
| 0.0.37 | 2025-11-25 | [69998](https://github.com/airbytehq/airbyte/pull/69998) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69584](https://github.com/airbytehq/airbyte/pull/69584) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68871](https://github.com/airbytehq/airbyte/pull/68871) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68368](https://github.com/airbytehq/airbyte/pull/68368) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67922](https://github.com/airbytehq/airbyte/pull/67922) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67538](https://github.com/airbytehq/airbyte/pull/67538) | Update dependencies |
| 0.0.31 | 2025-09-30 | [66441](https://github.com/airbytehq/airbyte/pull/66441) | Update dependencies |
| 0.0.30 | 2025-09-09 | [65656](https://github.com/airbytehq/airbyte/pull/65656) | Update dependencies |
| 0.0.29 | 2025-08-24 | [65452](https://github.com/airbytehq/airbyte/pull/65452) | Update dependencies |
| 0.0.28 | 2025-08-09 | [64804](https://github.com/airbytehq/airbyte/pull/64804) | Update dependencies |
| 0.0.27 | 2025-08-02 | [64418](https://github.com/airbytehq/airbyte/pull/64418) | Update dependencies |
| 0.0.26 | 2025-07-19 | [63610](https://github.com/airbytehq/airbyte/pull/63610) | Update dependencies |
| 0.0.25 | 2025-07-12 | [63039](https://github.com/airbytehq/airbyte/pull/63039) | Update dependencies |
| 0.0.24 | 2025-07-05 | [62726](https://github.com/airbytehq/airbyte/pull/62726) | Update dependencies |
| 0.0.23 | 2025-06-28 | [62267](https://github.com/airbytehq/airbyte/pull/62267) | Update dependencies |
| 0.0.22 | 2025-06-14 | [61620](https://github.com/airbytehq/airbyte/pull/61620) | Update dependencies |
| 0.0.21 | 2025-05-25 | [60507](https://github.com/airbytehq/airbyte/pull/60507) | Update dependencies |
| 0.0.20 | 2025-05-10 | [60146](https://github.com/airbytehq/airbyte/pull/60146) | Update dependencies |
| 0.0.19 | 2025-05-04 | [58397](https://github.com/airbytehq/airbyte/pull/58397) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57928](https://github.com/airbytehq/airbyte/pull/57928) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57295](https://github.com/airbytehq/airbyte/pull/57295) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56754](https://github.com/airbytehq/airbyte/pull/56754) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56222](https://github.com/airbytehq/airbyte/pull/56222) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55053](https://github.com/airbytehq/airbyte/pull/55053) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54618](https://github.com/airbytehq/airbyte/pull/54618) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53967](https://github.com/airbytehq/airbyte/pull/53967) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53491](https://github.com/airbytehq/airbyte/pull/53491) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53022](https://github.com/airbytehq/airbyte/pull/53022) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52531](https://github.com/airbytehq/airbyte/pull/52531) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51909](https://github.com/airbytehq/airbyte/pull/51909) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51367](https://github.com/airbytehq/airbyte/pull/51367) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50682](https://github.com/airbytehq/airbyte/pull/50682) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50255](https://github.com/airbytehq/airbyte/pull/50255) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49690](https://github.com/airbytehq/airbyte/pull/49690) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49366](https://github.com/airbytehq/airbyte/pull/49366) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49092](https://github.com/airbytehq/airbyte/pull/49092) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
