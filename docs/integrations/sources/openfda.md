# OpenFDA
OpenFDA provides access to a number of high-value, high priority and scalable structured datasets, including adverse events, drug product labeling, and recall enforcement reports.
With this conenctor we can fetch data from the streams like Drugs , Animal and Veterinary Adverse Events and Food Adverse Events etc.
Docs:https://open.fda.gov/apis/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Animal and Veterinary Adverse Events | unique_aer_id_number | DefaultPaginator | ✅ |  ❌  |
| Tobacco Problem Reports | report_id | DefaultPaginator | ✅ |  ❌  |
| Food Adverse Events | report_number | DefaultPaginator | ✅ |  ❌  |
| Food Enforcement Reports | recall_number | DefaultPaginator | ✅ |  ❌  |
| Drug Adverse Events |  | DefaultPaginator | ✅ |  ❌  |
| Drug Product Labelling |  | DefaultPaginator | ✅ |  ❌  |
| Drug NDC Library | product_id | DefaultPaginator | ✅ |  ❌  |
| Drug recall Enforcement Reports |  | DefaultPaginator | ✅ |  ❌  |
| Drugs |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2024-12-14 | [49668](https://github.com/airbytehq/airbyte/pull/49668) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49351](https://github.com/airbytehq/airbyte/pull/49351) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49090](https://github.com/airbytehq/airbyte/pull/49090) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-23 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
