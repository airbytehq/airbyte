# Campayn
The Airbyte connector for [Campayn](https://campayn.com/) enables seamless data integration between the Campayn email marketing platform and your data warehouse or analytics system. This connector automates the extraction of subscriber lists, email campaigns, performance metrics, and engagement data from Campayn, allowing businesses to centralize marketing insights, optimize email strategies, and drive data-driven decisions efficiently.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `sub_domain` | `string` | Sub Domain.  |  |
| `api_key` | `string` | API Key. API key to use. Find it in your Campayn account settings. Keep it secure as it grants access to your Campayn data. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | id | No pagination | ✅ |  ❌  |
| forms | id | No pagination | ✅ |  ❌  |
| contacts | id | No pagination | ✅ |  ❌  |
| emails | id | No pagination | ✅ |  ❌  |
| reports | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.23 | 2025-05-17 | [60645](https://github.com/airbytehq/airbyte/pull/60645) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59899](https://github.com/airbytehq/airbyte/pull/59899) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59367](https://github.com/airbytehq/airbyte/pull/59367) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58735](https://github.com/airbytehq/airbyte/pull/58735) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58242](https://github.com/airbytehq/airbyte/pull/58242) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57634](https://github.com/airbytehq/airbyte/pull/57634) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57185](https://github.com/airbytehq/airbyte/pull/57185) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56596](https://github.com/airbytehq/airbyte/pull/56596) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56084](https://github.com/airbytehq/airbyte/pull/56084) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55377](https://github.com/airbytehq/airbyte/pull/55377) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54866](https://github.com/airbytehq/airbyte/pull/54866) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54267](https://github.com/airbytehq/airbyte/pull/54267) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53898](https://github.com/airbytehq/airbyte/pull/53898) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53423](https://github.com/airbytehq/airbyte/pull/53423) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52193](https://github.com/airbytehq/airbyte/pull/52193) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51726](https://github.com/airbytehq/airbyte/pull/51726) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51274](https://github.com/airbytehq/airbyte/pull/51274) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50461](https://github.com/airbytehq/airbyte/pull/50461) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50208](https://github.com/airbytehq/airbyte/pull/50208) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49585](https://github.com/airbytehq/airbyte/pull/49585) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49306](https://github.com/airbytehq/airbyte/pull/49306) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49036](https://github.com/airbytehq/airbyte/pull/49036) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
