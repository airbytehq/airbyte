# Opinion Stage
The Airbyte connector for [OpinionStage](https://opinionstage.com) enables seamless data integration from the OpinionStage platform, facilitating the extraction of interactive content data. It streams data from items such as forms, quizzes, and polls, as well as capturing responses and specific questions associated with each item. This connector is ideal for users looking to analyze audience engagement, response patterns, and question insights from OpinionStage in their data workflows.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| items | id | DefaultPaginator | ✅ |  ❌  |
| responses | id | DefaultPaginator | ✅ |  ❌  |
| questions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.42 | 2025-12-09 | [70523](https://github.com/airbytehq/airbyte/pull/70523) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70087](https://github.com/airbytehq/airbyte/pull/70087) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69660](https://github.com/airbytehq/airbyte/pull/69660) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68992](https://github.com/airbytehq/airbyte/pull/68992) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68288](https://github.com/airbytehq/airbyte/pull/68288) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67750](https://github.com/airbytehq/airbyte/pull/67750) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67339](https://github.com/airbytehq/airbyte/pull/67339) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66377](https://github.com/airbytehq/airbyte/pull/66377) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65796](https://github.com/airbytehq/airbyte/pull/65796) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65164](https://github.com/airbytehq/airbyte/pull/65164) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64768](https://github.com/airbytehq/airbyte/pull/64768) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64291](https://github.com/airbytehq/airbyte/pull/64291) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63843](https://github.com/airbytehq/airbyte/pull/63843) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63408](https://github.com/airbytehq/airbyte/pull/63408) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63205](https://github.com/airbytehq/airbyte/pull/63205) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62619](https://github.com/airbytehq/airbyte/pull/62619) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62351](https://github.com/airbytehq/airbyte/pull/62351) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61034](https://github.com/airbytehq/airbyte/pull/61034) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60472](https://github.com/airbytehq/airbyte/pull/60472) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60176](https://github.com/airbytehq/airbyte/pull/60176) | Update dependencies |
| 0.0.22 | 2025-05-03 | [59452](https://github.com/airbytehq/airbyte/pull/59452) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59055](https://github.com/airbytehq/airbyte/pull/59055) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58467](https://github.com/airbytehq/airbyte/pull/58467) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57853](https://github.com/airbytehq/airbyte/pull/57853) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57322](https://github.com/airbytehq/airbyte/pull/57322) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56785](https://github.com/airbytehq/airbyte/pull/56785) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56179](https://github.com/airbytehq/airbyte/pull/56179) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55565](https://github.com/airbytehq/airbyte/pull/55565) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55011](https://github.com/airbytehq/airbyte/pull/55011) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54596](https://github.com/airbytehq/airbyte/pull/54596) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53954](https://github.com/airbytehq/airbyte/pull/53954) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53481](https://github.com/airbytehq/airbyte/pull/53481) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52994](https://github.com/airbytehq/airbyte/pull/52994) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52480](https://github.com/airbytehq/airbyte/pull/52480) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51888](https://github.com/airbytehq/airbyte/pull/51888) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51340](https://github.com/airbytehq/airbyte/pull/51340) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50721](https://github.com/airbytehq/airbyte/pull/50721) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50260](https://github.com/airbytehq/airbyte/pull/50260) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49726](https://github.com/airbytehq/airbyte/pull/49726) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49360](https://github.com/airbytehq/airbyte/pull/49360) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49060](https://github.com/airbytehq/airbyte/pull/49060) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
