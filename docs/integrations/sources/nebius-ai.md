# Nebius AI
Website: https://studio.nebius.com/
API Reference: https://studio.nebius.com/docs/api-reference

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Limit for each response objects | 20 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| models | id | No pagination | ✅ |  ✅  |
| files | id | No pagination | ✅ |  ✅  |
| file_contents | uuid | No pagination | ✅ |  ❌  |
| batches | id | No pagination | ✅ |  ✅  |
| batch_results | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.17 | 2025-08-23 | [65202](https://github.com/airbytehq/airbyte/pull/65202) | Update dependencies |
| 0.0.16 | 2025-08-09 | [64695](https://github.com/airbytehq/airbyte/pull/64695) | Update dependencies |
| 0.0.15 | 2025-08-02 | [64248](https://github.com/airbytehq/airbyte/pull/64248) | Update dependencies |
| 0.0.14 | 2025-07-26 | [63850](https://github.com/airbytehq/airbyte/pull/63850) | Update dependencies |
| 0.0.13 | 2025-07-19 | [63397](https://github.com/airbytehq/airbyte/pull/63397) | Update dependencies |
| 0.0.12 | 2025-07-12 | [63178](https://github.com/airbytehq/airbyte/pull/63178) | Update dependencies |
| 0.0.11 | 2025-07-05 | [62646](https://github.com/airbytehq/airbyte/pull/62646) | Update dependencies |
| 0.0.10 | 2025-06-28 | [62310](https://github.com/airbytehq/airbyte/pull/62310) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61019](https://github.com/airbytehq/airbyte/pull/61019) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60544](https://github.com/airbytehq/airbyte/pull/60544) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60169](https://github.com/airbytehq/airbyte/pull/60169) | Update dependencies |
| 0.0.6 | 2025-05-03 | [59489](https://github.com/airbytehq/airbyte/pull/59489) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59073](https://github.com/airbytehq/airbyte/pull/59073) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58523](https://github.com/airbytehq/airbyte/pull/58523) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57856](https://github.com/airbytehq/airbyte/pull/57856) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57348](https://github.com/airbytehq/airbyte/pull/57348) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56989](https://github.com/airbytehq/airbyte/pull/56989) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
