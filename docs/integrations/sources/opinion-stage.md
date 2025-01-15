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
| 0.0.7 | 2025-01-11 | [51340](https://github.com/airbytehq/airbyte/pull/51340) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50721](https://github.com/airbytehq/airbyte/pull/50721) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50260](https://github.com/airbytehq/airbyte/pull/50260) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49726](https://github.com/airbytehq/airbyte/pull/49726) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49360](https://github.com/airbytehq/airbyte/pull/49360) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49060](https://github.com/airbytehq/airbyte/pull/49060) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
