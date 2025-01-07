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
| 0.0.8 | 2024-12-28 | [50801](https://github.com/airbytehq/airbyte/pull/50801) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50313](https://github.com/airbytehq/airbyte/pull/50313) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49747](https://github.com/airbytehq/airbyte/pull/49747) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49420](https://github.com/airbytehq/airbyte/pull/49420) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48278](https://github.com/airbytehq/airbyte/pull/48278) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47884](https://github.com/airbytehq/airbyte/pull/47884) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47494](https://github.com/airbytehq/airbyte/pull/47494) | Update dependencies |
| 0.0.1 | 2024-09-05 | [45163](https://github.com/airbytehq/airbyte/pull/45163) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
