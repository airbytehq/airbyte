# Box Data Extract
The Box Connector enables seamless data extraction from Box, allowing users to access file content from their Box cloud storage. 
This connector helps automate workflows by integrating Box data with other tools, ensuring efficient file management and analysis

## Authentication
Follow [this](https://developer.box.com/guides/authentication/client-credentials/) guide to complete authentication.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client Secret.  |  |
| `Box Subject Type` | `string` | Enterprise  |  |
| `Box Subject ID` | `string` |   |  |
| `Box Folder ID` | `string` |   |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| stream_text_representation_folder | id | none | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.4 | 2024-10-24 | | Initial release by [@BoxDevRel](https://github.com/box-community/airbyte) |

</details>
