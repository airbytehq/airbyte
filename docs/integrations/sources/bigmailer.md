# BigMailer
An Airbyte connector for [BigMailer](https://bigmailer.com) would facilitate seamless data syncing between BigMailer and other platforms. This connector would allow users to pull data from BigMailer, such as *brands*, *contacts*, *lists*, *fields*, *message types*, *segments*, *bulk campaigns*, *transactional campaigns*, *suppression lists*, and *users*, into various data destinations for further analysis, reporting, or automation tasks.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. You can create and find it on the API key management page in your BigMailer account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| brands | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| lists | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |
| message-types | id | DefaultPaginator | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ❌  |
| bulk_campaigns | id | DefaultPaginator | ✅ |  ❌  |
| transactional_campaigns | id | DefaultPaginator | ✅ |  ❌  |
| suppression_lists |  | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-12-12 | [49287](https://github.com/airbytehq/airbyte/pull/49287) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49031](https://github.com/airbytehq/airbyte/pull/49031) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
