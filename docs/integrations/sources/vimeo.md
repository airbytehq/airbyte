# Vimeo
source-vimeo

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. Access token for authenticating API requests. You can generate this token from your Vimeo developer account. |  |
| `video_id` | `string` | video_id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| channels |  | DefaultPaginator | ✅ |  ❌  |
| video |  | DefaultPaginator | ✅ |  ❌  |
| videotags |  | DefaultPaginator | ✅ |  ❌  |
| videotracks |  | DefaultPaginator | ✅ |  ❌  |
| videothumbnail |  | DefaultPaginator | ✅ |  ❌  |
| videocomments |  | DefaultPaginator | ✅ |  ❌  |
| videocredits |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
