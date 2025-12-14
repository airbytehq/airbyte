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
| 0.0.41 | 2025-12-09 | [70468](https://github.com/airbytehq/airbyte/pull/70468) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70018](https://github.com/airbytehq/airbyte/pull/70018) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69378](https://github.com/airbytehq/airbyte/pull/69378) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68799](https://github.com/airbytehq/airbyte/pull/68799) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68218](https://github.com/airbytehq/airbyte/pull/68218) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67867](https://github.com/airbytehq/airbyte/pull/67867) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67407](https://github.com/airbytehq/airbyte/pull/67407) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66397](https://github.com/airbytehq/airbyte/pull/66397) | Update dependencies |
| 0.0.33 | 2025-09-09 | [66054](https://github.com/airbytehq/airbyte/pull/66054) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65368](https://github.com/airbytehq/airbyte/pull/65368) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64600](https://github.com/airbytehq/airbyte/pull/64600) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64206](https://github.com/airbytehq/airbyte/pull/64206) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63917](https://github.com/airbytehq/airbyte/pull/63917) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63503](https://github.com/airbytehq/airbyte/pull/63503) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63096](https://github.com/airbytehq/airbyte/pull/63096) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62652](https://github.com/airbytehq/airbyte/pull/62652) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61825](https://github.com/airbytehq/airbyte/pull/61825) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61131](https://github.com/airbytehq/airbyte/pull/61131) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60604](https://github.com/airbytehq/airbyte/pull/60604) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59877](https://github.com/airbytehq/airbyte/pull/59877) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59255](https://github.com/airbytehq/airbyte/pull/59255) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58760](https://github.com/airbytehq/airbyte/pull/58760) | Update dependencies |
| 0.0.19 | 2025-04-19 | [57716](https://github.com/airbytehq/airbyte/pull/57716) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57037](https://github.com/airbytehq/airbyte/pull/57037) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56694](https://github.com/airbytehq/airbyte/pull/56694) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56059](https://github.com/airbytehq/airbyte/pull/56059) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55433](https://github.com/airbytehq/airbyte/pull/55433) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54762](https://github.com/airbytehq/airbyte/pull/54762) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54324](https://github.com/airbytehq/airbyte/pull/54324) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53812](https://github.com/airbytehq/airbyte/pull/53812) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53292](https://github.com/airbytehq/airbyte/pull/53292) | Update dependencies |
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
