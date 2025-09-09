# ticktick
Source for the ticktick openapi endpoint at https://developer.ticktick.com/

## Configuration

| Input           | Type     | Description                                                                                                                       | Default Value |
| --------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `client_id`     | `string` | Application client id created by going to the [ticktick application center](https://developer.ticktick.com/manage)                |
| `client_secret` | `string` | Application client id                                                                                                             |
| `api_key`       | `string` | (optional) token obtained from running the oauth workflow. Can use this value directly and bypasss `client_id` / `client_secret`. |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | No pagination | ✅ |  ❌  |
| tasks | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.5 | 2025-09-03 | [64942](https://github.com/airbytehq/airbyte/pull/64947) | Add oauth2 method. Ignore archived projects on stream `projects`. Added API budget to proactively not hit rate limits. |
| 0.0.4 | 2025-08-24 | [65458](https://github.com/airbytehq/airbyte/pull/65458) | Update dependencies |
| 0.0.3 | 2025-08-16 | [64962](https://github.com/airbytehq/airbyte/pull/64962) | Update dependencies |
| 0.0.2 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-05 | | Initial release by [@luutuankiet](https://github.com/luutuankiet) via Connector Builder |

</details>
