# Clinicaltrials
Clinicaltrials provides data related to clinical studies.
Using this connector we can extract data from various streams such as studies and stats.
Docs : https://clinicaltrials.gov/data-api/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `conditions_or_disease` | `string` | Conditions or disease.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| studies |  | DefaultPaginator | ✅ |  ❌  |
| metadata_studies |  | No pagination | ✅ |  ❌  |
| stats |  | No pagination | ✅ |  ❌  |
| stats_field_values |  | No pagination | ✅ |  ❌  |
| stats_field_sizes |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
