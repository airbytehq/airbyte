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
| 0.0.8 | 2025-01-18 | [51726](https://github.com/airbytehq/airbyte/pull/51726) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51274](https://github.com/airbytehq/airbyte/pull/51274) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50461](https://github.com/airbytehq/airbyte/pull/50461) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50208](https://github.com/airbytehq/airbyte/pull/50208) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49585](https://github.com/airbytehq/airbyte/pull/49585) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49306](https://github.com/airbytehq/airbyte/pull/49306) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49036](https://github.com/airbytehq/airbyte/pull/49036) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
