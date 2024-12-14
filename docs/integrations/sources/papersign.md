# Papersign
The Airbyte connector for [Papersign](https://paperform.co/products/papersign/) enables seamless integration between Airbyte and Papersign, allowing automated data syncs between your Papersign documents and other platforms. This connector facilitates the extraction, transformation, and loading of e-signature data, document statuses, and user interactions, streamlining workflows and ensuring your e-signature data is easily accessible across systems.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Generate it on your account page at https://paperform.co/account/developer. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| documents | id | DefaultPaginator | ✅ |  ❌  |
| folders | id | No pagination | ✅ |  ❌  |
| spaces | id | No pagination | ✅ |  ❌  |
| webhooks | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2024-12-14 | [49696](https://github.com/airbytehq/airbyte/pull/49696) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49361](https://github.com/airbytehq/airbyte/pull/49361) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49105](https://github.com/airbytehq/airbyte/pull/49105) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
