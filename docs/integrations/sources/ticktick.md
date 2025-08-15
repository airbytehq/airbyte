# ticktick
Source for the ticktick openapi endpoint at https://developer.ticktick.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key optained from running the workflow [get access token](https://developer.ticktick.com/api#/openapi?id=get-access-token)  |  |

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
| 0.0.2 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-05 | | Initial release by [@luutuankiet](https://github.com/luutuankiet) via Connector Builder |

</details>
