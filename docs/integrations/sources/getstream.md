# getStream
This getStream connector syncs chat channel data from getStream Chat end-point to your destination. It supports both full refresh and incremental sync modes, efficiently extracting channel metadata, member information, configuration settings, and activity timestamps using cursor-based synchronization. Authentication is handled securely via JWT tokens using your getStream API credentials. Perfect for analyzing chat engagement patterns, monitoring channel growth, and integrating chat data with your business analytics.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  | qbpgvdqmr8je |
| `user_id` | `string` | User ID.  | 01680cea-ba49-4246-a9b3-98fa3f7b0685 |
| `secret_key` | `string` | Secret Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| channels | channel_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-10 | | Initial release by [@brunera1](https://github.com/brunera1) via Connector Builder |

</details>
