# Clarifai

Clarifai is the leading computer vision platform to quickly build and deploy AI on-prem, air-gapped, at the edge, or in the cloud.

API Documentation: https://docs.clarifai.com/api-guide/api-overview/helpful-api-resources/using-postman-with-clarifai-apis

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The personal access token found at `https://clarifai.com/settings/security` |  |
| `user_id` | `string` | User ID. User ID found in settings |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| applications | id | DefaultPaginator | ✅ |   ❌  |
| datasets | id | DefaultPaginator | ✅ |   ❌  |
| models | id | DefaultPaginator | ✅ |   ❌  |
| model_versions | id | DefaultPaginator | ✅ |   ❌  |
| worklows | id | DefaultPaginator | ✅ |   ❌  |
| app_inputs | id | DefaultPaginator | ✅ |   ❌  |
| app_inputs_jobs | id | DefaultPaginator | ✅ |   ❌ |
| app_concepts | id | DefaultPaginator | ✅ |   ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.17 | 2025-03-08 | [55381](https://github.com/airbytehq/airbyte/pull/55381) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54837](https://github.com/airbytehq/airbyte/pull/54837) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54282](https://github.com/airbytehq/airbyte/pull/54282) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53918](https://github.com/airbytehq/airbyte/pull/53918) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53396](https://github.com/airbytehq/airbyte/pull/53396) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52949](https://github.com/airbytehq/airbyte/pull/52949) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52156](https://github.com/airbytehq/airbyte/pull/52156) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51775](https://github.com/airbytehq/airbyte/pull/51775) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51265](https://github.com/airbytehq/airbyte/pull/51265) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50482](https://github.com/airbytehq/airbyte/pull/50482) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50178](https://github.com/airbytehq/airbyte/pull/50178) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49583](https://github.com/airbytehq/airbyte/pull/49583) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49295](https://github.com/airbytehq/airbyte/pull/49295) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48898](https://github.com/airbytehq/airbyte/pull/48898) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-05 | [48355](https://github.com/airbytehq/airbyte/pull/48355) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.2 | 2024-11-05 | [48321](https://github.com/airbytehq/airbyte/pull/48321) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
