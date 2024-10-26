# Google Slides
Google Slides connector for Airbyte that enables seamless data integration by extracting presentation data, including slide content and metadata. This connector simplifies workflows by automating the flow of presentation data into analytics or reporting tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `presentation_id` | `string` | Presentation Id.  |  |
| `page_id` | `string` | Page Id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| presentation |  | No pagination | ✅ |  ❌  |
| pages | objectId | No pagination | ✅ |  ❌  |
| thumbnail |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-26 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
