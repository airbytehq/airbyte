# Survicate
This page contains the setup guide and reference information for the [Survicate](https://survicate.com/) source connector.

## Prerequisites
To set up the Survicate source connector with Airbyte, you'll need to create your API keys from theie settings page. Please refer `https://developers.survicate.com/data-export/setup/` for getting your api_key.

## Documentation reference:
Visit `https://developers.survicate.com/data-export/setup/` for API documentation

## Authentication setup
Refer `https://developers.survicate.com/data-export/setup/#authentication` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| surveys | id | DefaultPaginator | ✅ |  ✅  |
| surveys_questions | id | DefaultPaginator | ✅ |  ❌  |
| surveys_responses | uuid | DefaultPaginator | ✅ |  ✅  |
| respondents_attributes |  | DefaultPaginator | ✅ |  ❌  |
| respondents_responses |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | -- | ---------------- |
| 0.0.1 | 2024-09-05 | [45163](https://github.com/airbytehq/airbyte/pull/45163) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
