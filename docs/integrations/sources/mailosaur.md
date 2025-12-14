# Mailosaur
Mailosaur is a communication-testing platform .
With this connector we can easily fetch data from messages , servers and transactions streams!
Docs : https://mailosaur.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter API here |  |
| `password` | `string` | Password. Enter your API Key here |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Messages | id | No pagination | ✅ |  ❌  |
| Servers | id | No pagination | ✅ |  ❌  |
| Transactions | timestamp | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.40 | 2025-12-09 | [70752](https://github.com/airbytehq/airbyte/pull/70752) | Update dependencies |
| 0.0.39 | 2025-11-25 | [70114](https://github.com/airbytehq/airbyte/pull/70114) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69554](https://github.com/airbytehq/airbyte/pull/69554) | Update dependencies |
| 0.0.37 | 2025-10-29 | [69065](https://github.com/airbytehq/airbyte/pull/69065) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68432](https://github.com/airbytehq/airbyte/pull/68432) | Update dependencies |
| 0.0.35 | 2025-10-14 | [67847](https://github.com/airbytehq/airbyte/pull/67847) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67382](https://github.com/airbytehq/airbyte/pull/67382) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66338](https://github.com/airbytehq/airbyte/pull/66338) | Update dependencies |
| 0.0.32 | 2025-09-09 | [65747](https://github.com/airbytehq/airbyte/pull/65747) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65198](https://github.com/airbytehq/airbyte/pull/65198) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64666](https://github.com/airbytehq/airbyte/pull/64666) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64235](https://github.com/airbytehq/airbyte/pull/64235) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63849](https://github.com/airbytehq/airbyte/pull/63849) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63515](https://github.com/airbytehq/airbyte/pull/63515) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63113](https://github.com/airbytehq/airbyte/pull/63113) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62618](https://github.com/airbytehq/airbyte/pull/62618) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61822](https://github.com/airbytehq/airbyte/pull/61822) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61144](https://github.com/airbytehq/airbyte/pull/61144) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60592](https://github.com/airbytehq/airbyte/pull/60592) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59860](https://github.com/airbytehq/airbyte/pull/59860) | Update dependencies |
| 0.0.20 | 2025-05-03 | [58810](https://github.com/airbytehq/airbyte/pull/58810) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58203](https://github.com/airbytehq/airbyte/pull/58203) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57677](https://github.com/airbytehq/airbyte/pull/57677) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57078](https://github.com/airbytehq/airbyte/pull/57078) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56678](https://github.com/airbytehq/airbyte/pull/56678) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56013](https://github.com/airbytehq/airbyte/pull/56013) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55452](https://github.com/airbytehq/airbyte/pull/55452) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54774](https://github.com/airbytehq/airbyte/pull/54774) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54337](https://github.com/airbytehq/airbyte/pull/54337) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53847](https://github.com/airbytehq/airbyte/pull/53847) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53302](https://github.com/airbytehq/airbyte/pull/53302) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52721](https://github.com/airbytehq/airbyte/pull/52721) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52239](https://github.com/airbytehq/airbyte/pull/52239) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51834](https://github.com/airbytehq/airbyte/pull/51834) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51159](https://github.com/airbytehq/airbyte/pull/51159) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50639](https://github.com/airbytehq/airbyte/pull/50639) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50098](https://github.com/airbytehq/airbyte/pull/50098) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49607](https://github.com/airbytehq/airbyte/pull/49607) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49260](https://github.com/airbytehq/airbyte/pull/49260) | Update dependencies |
| 0.0.1 | 2024-11-04 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
