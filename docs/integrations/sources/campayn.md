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
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
