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
| 0.0.3 | 2024-11-05 | [48355](https://github.com/airbytehq/airbyte/pull/48355) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.2 | 2024-11-05 | [48321](https://github.com/airbytehq/airbyte/pull/48321) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
