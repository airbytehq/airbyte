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
| 0.0.42 | 2025-12-09 | [70469](https://github.com/airbytehq/airbyte/pull/70469) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70134](https://github.com/airbytehq/airbyte/pull/70134) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69691](https://github.com/airbytehq/airbyte/pull/69691) | Update dependencies |
| 0.0.39 | 2025-10-29 | [69018](https://github.com/airbytehq/airbyte/pull/69018) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68287](https://github.com/airbytehq/airbyte/pull/68287) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67747](https://github.com/airbytehq/airbyte/pull/67747) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67334](https://github.com/airbytehq/airbyte/pull/67334) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66385](https://github.com/airbytehq/airbyte/pull/66385) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65788](https://github.com/airbytehq/airbyte/pull/65788) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65231](https://github.com/airbytehq/airbyte/pull/65231) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64703](https://github.com/airbytehq/airbyte/pull/64703) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64180](https://github.com/airbytehq/airbyte/pull/64180) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63927](https://github.com/airbytehq/airbyte/pull/63927) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63439](https://github.com/airbytehq/airbyte/pull/63439) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63185](https://github.com/airbytehq/airbyte/pull/63185) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62547](https://github.com/airbytehq/airbyte/pull/62547) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62399](https://github.com/airbytehq/airbyte/pull/62399) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61914](https://github.com/airbytehq/airbyte/pull/61914) | Update dependencies |
| 0.0.24 | 2025-06-14 | [60545](https://github.com/airbytehq/airbyte/pull/60545) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60129](https://github.com/airbytehq/airbyte/pull/60129) | Update dependencies |
| 0.0.22 | 2025-05-03 | [59467](https://github.com/airbytehq/airbyte/pull/59467) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59108](https://github.com/airbytehq/airbyte/pull/59108) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58494](https://github.com/airbytehq/airbyte/pull/58494) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57905](https://github.com/airbytehq/airbyte/pull/57905) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57299](https://github.com/airbytehq/airbyte/pull/57299) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56748](https://github.com/airbytehq/airbyte/pull/56748) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56180](https://github.com/airbytehq/airbyte/pull/56180) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55524](https://github.com/airbytehq/airbyte/pull/55524) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55023](https://github.com/airbytehq/airbyte/pull/55023) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54576](https://github.com/airbytehq/airbyte/pull/54576) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53956](https://github.com/airbytehq/airbyte/pull/53956) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53479](https://github.com/airbytehq/airbyte/pull/53479) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53028](https://github.com/airbytehq/airbyte/pull/53028) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52491](https://github.com/airbytehq/airbyte/pull/52491) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51872](https://github.com/airbytehq/airbyte/pull/51872) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51368](https://github.com/airbytehq/airbyte/pull/51368) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50718](https://github.com/airbytehq/airbyte/pull/50718) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50285](https://github.com/airbytehq/airbyte/pull/50285) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49668](https://github.com/airbytehq/airbyte/pull/49668) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49351](https://github.com/airbytehq/airbyte/pull/49351) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49090](https://github.com/airbytehq/airbyte/pull/49090) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-23 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
