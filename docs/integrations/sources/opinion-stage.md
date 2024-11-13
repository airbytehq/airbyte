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
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
