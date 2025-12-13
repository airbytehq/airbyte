# Sendowl
Sendowl is an All-in-One Digital Commerce Platform.
Using this connector we can extract data from products , packages , orders , discounts and subscriptions streams.
[API Docs](https://dashboard.sendowl.com/developers/api/introduction)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter you API Key |  |
| `password` | `string` | Password. Enter your API secret |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products | id | DefaultPaginator | ✅ |  ❌  |
| packages | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70733](https://github.com/airbytehq/airbyte/pull/70733) | Update dependencies |
| 0.0.37 | 2025-11-25 | [69965](https://github.com/airbytehq/airbyte/pull/69965) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69671](https://github.com/airbytehq/airbyte/pull/69671) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68858](https://github.com/airbytehq/airbyte/pull/68858) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68409](https://github.com/airbytehq/airbyte/pull/68409) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67913](https://github.com/airbytehq/airbyte/pull/67913) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67218](https://github.com/airbytehq/airbyte/pull/67218) | Update dependencies |
| 0.0.31 | 2025-09-30 | [66872](https://github.com/airbytehq/airbyte/pull/66872) | Update dependencies |
| 0.0.30 | 2025-09-23 | [66629](https://github.com/airbytehq/airbyte/pull/66629) | Update dependencies |
| 0.0.29 | 2025-09-09 | [65684](https://github.com/airbytehq/airbyte/pull/65684) | Update dependencies |
| 0.0.28 | 2025-08-23 | [65430](https://github.com/airbytehq/airbyte/pull/65430) | Update dependencies |
| 0.0.27 | 2025-08-16 | [65002](https://github.com/airbytehq/airbyte/pull/65002) | Update dependencies |
| 0.0.26 | 2025-08-02 | [64450](https://github.com/airbytehq/airbyte/pull/64450) | Update dependencies |
| 0.0.25 | 2025-07-26 | [63986](https://github.com/airbytehq/airbyte/pull/63986) | Update dependencies |
| 0.0.24 | 2025-07-20 | [63669](https://github.com/airbytehq/airbyte/pull/63669) | Update dependencies |
| 0.0.23 | 2025-06-21 | [61838](https://github.com/airbytehq/airbyte/pull/61838) | Update dependencies |
| 0.0.22 | 2025-06-14 | [60554](https://github.com/airbytehq/airbyte/pull/60554) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60111](https://github.com/airbytehq/airbyte/pull/60111) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59598](https://github.com/airbytehq/airbyte/pull/59598) | Update dependencies |
| 0.0.19 | 2025-04-27 | [58393](https://github.com/airbytehq/airbyte/pull/58393) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57950](https://github.com/airbytehq/airbyte/pull/57950) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57471](https://github.com/airbytehq/airbyte/pull/57471) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56893](https://github.com/airbytehq/airbyte/pull/56893) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56266](https://github.com/airbytehq/airbyte/pull/56266) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55072](https://github.com/airbytehq/airbyte/pull/55072) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54560](https://github.com/airbytehq/airbyte/pull/54560) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53972](https://github.com/airbytehq/airbyte/pull/53972) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53467](https://github.com/airbytehq/airbyte/pull/53467) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52972](https://github.com/airbytehq/airbyte/pull/52972) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52529](https://github.com/airbytehq/airbyte/pull/52529) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51915](https://github.com/airbytehq/airbyte/pull/51915) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51363](https://github.com/airbytehq/airbyte/pull/51363) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50711](https://github.com/airbytehq/airbyte/pull/50711) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50248](https://github.com/airbytehq/airbyte/pull/50248) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49683](https://github.com/airbytehq/airbyte/pull/49683) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49338](https://github.com/airbytehq/airbyte/pull/49338) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49054](https://github.com/airbytehq/airbyte/pull/49054) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
