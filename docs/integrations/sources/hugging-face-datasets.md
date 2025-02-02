# Hugging Face - Datasets
Imports datasets from Hugging Face ([https://huggingface.co/datasets](https://huggingface.co/datasets))

Only datasets with [Parquet exports](https://huggingface.co/docs/dataset-viewer/en/parquet) can be imported with this connector.
## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `dataset_name` | `string` | Dataset Name.  |  |
| `dataset_subsets` | `array` | Dataset Subsets. Dataset Subsets to import. Will import all of them if nothing is provided (see https://huggingface.co/docs/dataset-viewer/en/configs_and_splits for more details) |  |
| `dataset_splits` | `array` | Dataset Splits. Splits to import. Will import all of them if nothing is provided (see https://huggingface.co/docs/dataset-viewer/en/configs_and_splits for more details) |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| rows |  | DefaultPaginator | ✅ |  ❌  |
| splits |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-01 | [52789](https://github.com/airbytehq/airbyte/pull/52789) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52244](https://github.com/airbytehq/airbyte/pull/52244) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51820](https://github.com/airbytehq/airbyte/pull/51820) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51202](https://github.com/airbytehq/airbyte/pull/51202) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50621](https://github.com/airbytehq/airbyte/pull/50621) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50079](https://github.com/airbytehq/airbyte/pull/50079) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49609](https://github.com/airbytehq/airbyte/pull/49609) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49233](https://github.com/airbytehq/airbyte/pull/49233) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48911](https://github.com/airbytehq/airbyte/pull/48911) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-28 | | Initial release by [@michel-tricot](https://github.com/michel-tricot) via Connector Builder |

</details>
