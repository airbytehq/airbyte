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
| 0.0.15 | 2025-03-08 | [55558](https://github.com/airbytehq/airbyte/pull/55558) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55003](https://github.com/airbytehq/airbyte/pull/55003) | Update dependencies |
| 0.0.13 | 2025-02-23 | [54608](https://github.com/airbytehq/airbyte/pull/54608) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53949](https://github.com/airbytehq/airbyte/pull/53949) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53463](https://github.com/airbytehq/airbyte/pull/53463) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53020](https://github.com/airbytehq/airbyte/pull/53020) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52507](https://github.com/airbytehq/airbyte/pull/52507) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51881](https://github.com/airbytehq/airbyte/pull/51881) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51316](https://github.com/airbytehq/airbyte/pull/51316) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50691](https://github.com/airbytehq/airbyte/pull/50691) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50272](https://github.com/airbytehq/airbyte/pull/50272) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49696](https://github.com/airbytehq/airbyte/pull/49696) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49361](https://github.com/airbytehq/airbyte/pull/49361) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49105](https://github.com/airbytehq/airbyte/pull/49105) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
