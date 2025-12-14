# Encharge
Airbyte connector for [Encharge](https://encharge.io/) enables seamless data integration between Encharge and your data warehouse or other destinations. With this connector, you can easily sync marketing automation data from Encharge. This allows for improved data-driven decision-making and enhanced marketing insights across platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| peoples | id | DefaultPaginator | ✅ |  ❌  |
| accounts | accountId | No pagination | ✅ |  ❌  |
| account_tags | tag | No pagination | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ❌  |
| segment_people | id | DefaultPaginator | ✅ |  ❌  |
| fields | name | No pagination | ✅ |  ❌  |
| schemas | name | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70554](https://github.com/airbytehq/airbyte/pull/70554) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70153](https://github.com/airbytehq/airbyte/pull/70153) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69402](https://github.com/airbytehq/airbyte/pull/69402) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68734](https://github.com/airbytehq/airbyte/pull/68734) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68568](https://github.com/airbytehq/airbyte/pull/68568) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67799](https://github.com/airbytehq/airbyte/pull/67799) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67273](https://github.com/airbytehq/airbyte/pull/67273) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66289](https://github.com/airbytehq/airbyte/pull/66289) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65844](https://github.com/airbytehq/airbyte/pull/65844) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65260](https://github.com/airbytehq/airbyte/pull/65260) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64764](https://github.com/airbytehq/airbyte/pull/64764) | Update dependencies |
| 0.0.30 | 2025-07-26 | [64002](https://github.com/airbytehq/airbyte/pull/64002) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63548](https://github.com/airbytehq/airbyte/pull/63548) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63014](https://github.com/airbytehq/airbyte/pull/63014) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62765](https://github.com/airbytehq/airbyte/pull/62765) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62428](https://github.com/airbytehq/airbyte/pull/62428) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61959](https://github.com/airbytehq/airbyte/pull/61959) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61244](https://github.com/airbytehq/airbyte/pull/61244) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60346](https://github.com/airbytehq/airbyte/pull/60346) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60015](https://github.com/airbytehq/airbyte/pull/60015) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59374](https://github.com/airbytehq/airbyte/pull/59374) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58834](https://github.com/airbytehq/airbyte/pull/58834) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58339](https://github.com/airbytehq/airbyte/pull/58339) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57785](https://github.com/airbytehq/airbyte/pull/57785) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57194](https://github.com/airbytehq/airbyte/pull/57194) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56503](https://github.com/airbytehq/airbyte/pull/56503) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55925](https://github.com/airbytehq/airbyte/pull/55925) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55267](https://github.com/airbytehq/airbyte/pull/55267) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54965](https://github.com/airbytehq/airbyte/pull/54965) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54392](https://github.com/airbytehq/airbyte/pull/54392) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53785](https://github.com/airbytehq/airbyte/pull/53785) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53357](https://github.com/airbytehq/airbyte/pull/53357) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52810](https://github.com/airbytehq/airbyte/pull/52810) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52327](https://github.com/airbytehq/airbyte/pull/52327) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51708](https://github.com/airbytehq/airbyte/pull/51708) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51115](https://github.com/airbytehq/airbyte/pull/51115) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50537](https://github.com/airbytehq/airbyte/pull/50537) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50001](https://github.com/airbytehq/airbyte/pull/50001) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49509](https://github.com/airbytehq/airbyte/pull/49509) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49175](https://github.com/airbytehq/airbyte/pull/49175) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
