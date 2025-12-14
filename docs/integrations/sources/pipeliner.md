# Pipeliner

Pipeliner is a CRM tool.
Using this connector we fetch data from various streams such as contacts, data, leads and quotes.
[API Docs](https://pipeliner.stoplight.io/docs/api-docs)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `service` | `string` | Data Center.  |  |
| `spaceid` | `string` | Space ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| activities | id | DefaultPaginator | ✅ |  ❌  |
| clients | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| entities | id | DefaultPaginator | ✅ |  ❌  |
| data | id | DefaultPaginator | ✅ |  ❌  |
| cloud_objects | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |
| forecasts | id | DefaultPaginator | ✅ |  ❌  |
| form_views | id | DefaultPaginator | ✅ |  ❌  |
| entity_scorings | id | DefaultPaginator | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| lead_oppties | id | DefaultPaginator | ✅ |  ❌  |
| memos | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| entity_fitnesses | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| oppty_product_relations | id | DefaultPaginator | ✅ |  ❌  |
| profiles | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| steps | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70476](https://github.com/airbytehq/airbyte/pull/70476) | Update dependencies |
| 0.0.37 | 2025-11-25 | [69954](https://github.com/airbytehq/airbyte/pull/69954) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69604](https://github.com/airbytehq/airbyte/pull/69604) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68923](https://github.com/airbytehq/airbyte/pull/68923) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68217](https://github.com/airbytehq/airbyte/pull/68217) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67828](https://github.com/airbytehq/airbyte/pull/67828) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67493](https://github.com/airbytehq/airbyte/pull/67493) | Update dependencies |
| 0.0.31 | 2025-09-30 | [66964](https://github.com/airbytehq/airbyte/pull/66964) | Update dependencies |
| 0.0.30 | 2025-09-23 | [66419](https://github.com/airbytehq/airbyte/pull/66419) | Update dependencies |
| 0.0.29 | 2025-09-09 | [65848](https://github.com/airbytehq/airbyte/pull/65848) | Update dependencies |
| 0.0.28 | 2025-08-23 | [65217](https://github.com/airbytehq/airbyte/pull/65217) | Update dependencies |
| 0.0.27 | 2025-08-09 | [64684](https://github.com/airbytehq/airbyte/pull/64684) | Update dependencies |
| 0.0.26 | 2025-08-02 | [64228](https://github.com/airbytehq/airbyte/pull/64228) | Update dependencies |
| 0.0.25 | 2025-07-26 | [63929](https://github.com/airbytehq/airbyte/pull/63929) | Update dependencies |
| 0.0.24 | 2025-07-19 | [63417](https://github.com/airbytehq/airbyte/pull/63417) | Update dependencies |
| 0.0.23 | 2025-07-12 | [63269](https://github.com/airbytehq/airbyte/pull/63269) | Update dependencies |
| 0.0.22 | 2025-06-28 | [62407](https://github.com/airbytehq/airbyte/pull/62407) | Update dependencies |
| 0.0.21 | 2025-06-21 | [60160](https://github.com/airbytehq/airbyte/pull/60160) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59508](https://github.com/airbytehq/airbyte/pull/59508) | Update dependencies |
| 0.0.19 | 2025-04-27 | [58529](https://github.com/airbytehq/airbyte/pull/58529) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57846](https://github.com/airbytehq/airbyte/pull/57846) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57327](https://github.com/airbytehq/airbyte/pull/57327) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56774](https://github.com/airbytehq/airbyte/pull/56774) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56195](https://github.com/airbytehq/airbyte/pull/56195) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55052](https://github.com/airbytehq/airbyte/pull/55052) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54591](https://github.com/airbytehq/airbyte/pull/54591) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54009](https://github.com/airbytehq/airbyte/pull/54009) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53473](https://github.com/airbytehq/airbyte/pull/53473) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53029](https://github.com/airbytehq/airbyte/pull/53029) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52512](https://github.com/airbytehq/airbyte/pull/52512) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51877](https://github.com/airbytehq/airbyte/pull/51877) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51358](https://github.com/airbytehq/airbyte/pull/51358) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50694](https://github.com/airbytehq/airbyte/pull/50694) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50276](https://github.com/airbytehq/airbyte/pull/50276) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49656](https://github.com/airbytehq/airbyte/pull/49656) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49321](https://github.com/airbytehq/airbyte/pull/49321) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49077](https://github.com/airbytehq/airbyte/pull/49077) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
