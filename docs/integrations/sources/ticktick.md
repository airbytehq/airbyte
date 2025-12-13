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
| 0.0.15 | 2025-12-09 | [70787](https://github.com/airbytehq/airbyte/pull/70787) | Update dependencies |
| 0.0.14 | 2025-11-25 | [69869](https://github.com/airbytehq/airbyte/pull/69869) | Update dependencies |
| 0.0.13 | 2025-11-18 | [69673](https://github.com/airbytehq/airbyte/pull/69673) | Update dependencies |
| 0.0.12 | 2025-10-29 | [68914](https://github.com/airbytehq/airbyte/pull/68914) | Update dependencies |
| 0.0.11 | 2025-10-21 | [68549](https://github.com/airbytehq/airbyte/pull/68549) | Update dependencies |
| 0.0.10 | 2025-10-14 | [67889](https://github.com/airbytehq/airbyte/pull/67889) | Update dependencies |
| 0.0.9 | 2025-10-07 | [67510](https://github.com/airbytehq/airbyte/pull/67510) | Update dependencies |
| 0.0.8 | 2025-09-30 | [66828](https://github.com/airbytehq/airbyte/pull/66828) | Update dependencies |
| 0.0.7 | 2025-09-23 | [66370](https://github.com/airbytehq/airbyte/pull/66370) | Update dependencies |
| 0.0.6 | 2025-09-09 | [65718](https://github.com/airbytehq/airbyte/pull/65718) | Update dependencies |
| 0.0.5 | 2025-09-03 | [64942](https://github.com/airbytehq/airbyte/pull/64947) | Add oauth2 method. Ignore archived projects on stream `projects`. Added API budget to proactively not hit rate limits. |
| 0.0.4 | 2025-08-24 | [65458](https://github.com/airbytehq/airbyte/pull/65458) | Update dependencies |
| 0.0.3 | 2025-08-16 | [64962](https://github.com/airbytehq/airbyte/pull/64962) | Update dependencies |
| 0.0.2 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-05 | | Initial release by [@luutuankiet](https://github.com/luutuankiet) via Connector Builder |

</details>
