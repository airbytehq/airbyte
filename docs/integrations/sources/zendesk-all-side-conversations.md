# zendesk_all_side_conversations
This connector is used to 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `password` | `string` | Password.  |  |
| `username` | `string` | Username.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| side_conversation_events |  | DefaultPaginator | ✅ |  ❌  |
| all_side_conversations |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-02-21 | | Initial release by [@jjose1508](https://github.com/jjose1508) via Connector Builder |

</details>
