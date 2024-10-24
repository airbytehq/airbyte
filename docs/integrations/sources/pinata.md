# Pinata
This is the source connector for the Pinata API that ingests data from both Pinata files and IPFS files https://pinata.cloud/

This API uses bearer tokens for authentication, in order to generate your token create an account on pinata. Once logged in click on the API Keys button in the left sidebar, then click “New Key” in the top right.
Create a new key and copy the JWT token, this will be used in your bearer Auth  https://docs.pinata.cloud/quickstart

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| files | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| ipfs_files | id | DefaultPaginator | ✅ |  ❌  |
| ipfs_groups | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-24 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
