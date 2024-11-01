# OpenGSA Perdiem
This provides data related to reimbursement rates that federal agencies use to reimburse their employees.
Docs : https://open.gsa.gov/api/perdiem/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `city` | `string` | city.  |  |
| `state` | `string` | state.  |  |
| `zip` | `string` | zip.  |  |
| `year` | `string` | year.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| mapping_zipcodes_did_statelocations |  | No pagination | ✅ |  ❌  |
| meals_incidental_expenses |  | No pagination | ✅ |  ❌  |
| lodging_rates |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-01 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
