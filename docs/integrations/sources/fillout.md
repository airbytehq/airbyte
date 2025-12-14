# Fillout

The Airbyte connector for Fillout.com enables seamless data synchronization between Fillout forms and various target destinations. This connector allows you to extract form submissions and related data from Fillout and transfer it to your chosen data warehouse, analytics platform, or other destinations. With this integration, you can automate workflows, perform data analysis, and centralize data management for improved insights and reporting.

## Configuration

| Input        | Type     | Description                                                                             | Default Value |
| ------------ | -------- | --------------------------------------------------------------------------------------- | ------------- |
| `api_key`    | `string` | API Key. API key to use. Find it in the Developer settings tab of your Fillout account. |               |
| `start_date` | `string` | Start date.                                                                             |               |

## Streams

| Stream Name   | Primary Key  | Pagination       | Supports Full Sync | Supports Incremental |
| ------------- | ------------ | ---------------- | ------------------ | -------------------- |
| forms         | formId       | DefaultPaginator | ✅                 | ❌                   |
| form_metadata | id           | DefaultPaginator | ✅                 | ❌                   |
| submissions   | submissionId | DefaultPaginator | ✅                 | ✅                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                             |
| ------- | ---------- | ------------ | ----------------------------------------------------------------------------------- |
| 0.2.40 | 2025-12-09 | [70550](https://github.com/airbytehq/airbyte/pull/70550) | Update dependencies |
| 0.2.39 | 2025-11-25 | [70014](https://github.com/airbytehq/airbyte/pull/70014) | Update dependencies |
| 0.2.38 | 2025-11-18 | [69481](https://github.com/airbytehq/airbyte/pull/69481) | Update dependencies |
| 0.2.37 | 2025-10-29 | [68801](https://github.com/airbytehq/airbyte/pull/68801) | Update dependencies |
| 0.2.36 | 2025-10-21 | [68454](https://github.com/airbytehq/airbyte/pull/68454) | Update dependencies |
| 0.2.35 | 2025-10-14 | [68039](https://github.com/airbytehq/airbyte/pull/68039) | Update dependencies |
| 0.2.34 | 2025-10-07 | [67308](https://github.com/airbytehq/airbyte/pull/67308) | Update dependencies |
| 0.2.33 | 2025-09-30 | [66766](https://github.com/airbytehq/airbyte/pull/66766) | Update dependencies |
| 0.2.32 | 2025-09-24 | [65783](https://github.com/airbytehq/airbyte/pull/65783) | Update dependencies |
| 0.2.31 | 2025-08-23 | [65296](https://github.com/airbytehq/airbyte/pull/65296) | Update dependencies |
| 0.2.30 | 2025-08-09 | [64711](https://github.com/airbytehq/airbyte/pull/64711) | Update dependencies |
| 0.2.29 | 2025-08-02 | [64323](https://github.com/airbytehq/airbyte/pull/64323) | Update dependencies |
| 0.2.28 | 2025-07-26 | [64034](https://github.com/airbytehq/airbyte/pull/64034) | Update dependencies |
| 0.2.27 | 2025-07-19 | [63579](https://github.com/airbytehq/airbyte/pull/63579) | Update dependencies |
| 0.2.26 | 2025-07-12 | [63006](https://github.com/airbytehq/airbyte/pull/63006) | Update dependencies |
| 0.2.25 | 2025-07-05 | [62802](https://github.com/airbytehq/airbyte/pull/62802) | Update dependencies |
| 0.2.24 | 2025-06-28 | [62368](https://github.com/airbytehq/airbyte/pull/62368) | Update dependencies |
| 0.2.23 | 2025-06-21 | [61966](https://github.com/airbytehq/airbyte/pull/61966) | Update dependencies |
| 0.2.22 | 2025-06-14 | [60424](https://github.com/airbytehq/airbyte/pull/60424) | Update dependencies |
| 0.2.21 | 2025-05-10 | [60038](https://github.com/airbytehq/airbyte/pull/60038) | Update dependencies |
| 0.2.20 | 2025-05-03 | [59411](https://github.com/airbytehq/airbyte/pull/59411) | Update dependencies |
| 0.2.19 | 2025-04-26 | [58857](https://github.com/airbytehq/airbyte/pull/58857) | Update dependencies |
| 0.2.18 | 2025-04-19 | [58370](https://github.com/airbytehq/airbyte/pull/58370) | Update dependencies |
| 0.2.17 | 2025-04-12 | [57836](https://github.com/airbytehq/airbyte/pull/57836) | Update dependencies |
| 0.2.16 | 2025-04-05 | [57273](https://github.com/airbytehq/airbyte/pull/57273) | Update dependencies |
| 0.2.15 | 2025-03-29 | [56538](https://github.com/airbytehq/airbyte/pull/56538) | Update dependencies |
| 0.2.14 | 2025-03-22 | [55926](https://github.com/airbytehq/airbyte/pull/55926) | Update dependencies |
| 0.2.13 | 2025-03-08 | [55317](https://github.com/airbytehq/airbyte/pull/55317) | Update dependencies |
| 0.2.12 | 2025-03-01 | [54943](https://github.com/airbytehq/airbyte/pull/54943) | Update dependencies |
| 0.2.11 | 2025-02-22 | [54388](https://github.com/airbytehq/airbyte/pull/54388) | Update dependencies |
| 0.2.10 | 2025-02-15 | [53771](https://github.com/airbytehq/airbyte/pull/53771) | Update dependencies |
| 0.2.9 | 2025-02-08 | [53327](https://github.com/airbytehq/airbyte/pull/53327) | Update dependencies |
| 0.2.8 | 2025-02-01 | [52800](https://github.com/airbytehq/airbyte/pull/52800) | Update dependencies |
| 0.2.7 | 2025-01-25 | [52352](https://github.com/airbytehq/airbyte/pull/52352) | Update dependencies |
| 0.2.6 | 2025-01-18 | [51689](https://github.com/airbytehq/airbyte/pull/51689) | Update dependencies |
| 0.2.5 | 2025-01-11 | [51112](https://github.com/airbytehq/airbyte/pull/51112) | Update dependencies |
| 0.2.4 | 2024-12-28 | [50515](https://github.com/airbytehq/airbyte/pull/50515) | Update dependencies |
| 0.2.3 | 2024-12-21 | [50068](https://github.com/airbytehq/airbyte/pull/50068) | Update dependencies |
| 0.2.2 | 2024-12-14 | [49530](https://github.com/airbytehq/airbyte/pull/49530) | Update dependencies |
| 0.2.1 | 2024-12-12 | [49189](https://github.com/airbytehq/airbyte/pull/49189) | Update dependencies |
| 0.2.0   | 2024-11-14 |              | Add `formId` to `submissions` stream                                                |
| 0.0.1   | 2024-10-28 |              | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
