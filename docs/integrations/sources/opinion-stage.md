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
