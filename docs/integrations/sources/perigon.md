# Perigon
Website: https://www.perigon.io/
API Reference: https://docs.perigon.io/reference/all-news

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the Perigon API. Obtain it by creating an account at https://www.perigon.io/sign-up and verifying your email. The API key will be visible on your account dashboard. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| articles | articleId | DefaultPaginator | ✅ |  ✅  |
| stories | id | DefaultPaginator | ✅ |  ✅  |
| journalists | id | No pagination | ✅ |  ✅  |
| sources | id | No pagination | ✅ |  ✅  |
| people | wikidataId | No pagination | ✅ |  ✅  |
| companies | id | No pagination | ✅ |  ✅  |
| topics | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date              | Pull Request | Subject        |
|---------|-------------------|--------------|----------------|
| 0.0.25 | 2025-12-09 | [70471](https://github.com/airbytehq/airbyte/pull/70471) | Update dependencies |
| 0.0.24 | 2025-11-25 | [69958](https://github.com/airbytehq/airbyte/pull/69958) | Update dependencies |
| 0.0.23 | 2025-11-18 | [69631](https://github.com/airbytehq/airbyte/pull/69631) | Update dependencies |
| 0.0.22 | 2025-10-29 | [68935](https://github.com/airbytehq/airbyte/pull/68935) | Update dependencies |
| 0.0.21 | 2025-10-21 | [68283](https://github.com/airbytehq/airbyte/pull/68283) | Update dependencies |
| 0.0.20 | 2025-10-14 | [67859](https://github.com/airbytehq/airbyte/pull/67859) | Update dependencies |
| 0.0.19 | 2025-10-07 | [67499](https://github.com/airbytehq/airbyte/pull/67499) | Update dependencies |
| 0.0.18 | 2025-09-30 | [66958](https://github.com/airbytehq/airbyte/pull/66958) | Update dependencies |
| 0.0.17 | 2025-09-23 | [66414](https://github.com/airbytehq/airbyte/pull/66414) | Update dependencies |
| 0.0.16 | 2025-09-09 | [65881](https://github.com/airbytehq/airbyte/pull/65881) | Update dependencies |
| 0.0.15 | 2025-09-05 | [65966](https://github.com/airbytehq/airbyte/pull/65966) | Update to CDK v7.0.0 |
| 0.0.14 | 2025-08-23 | [65190](https://github.com/airbytehq/airbyte/pull/65190) | Update dependencies |
| 0.0.13 | 2025-08-16 | [64984](https://github.com/airbytehq/airbyte/pull/64984) | Update dependencies |
| 0.0.12 | 2025-08-02 | [64182](https://github.com/airbytehq/airbyte/pull/64182) | Update dependencies |
| 0.0.11 | 2025-07-26 | [63839](https://github.com/airbytehq/airbyte/pull/63839) | Update dependencies |
| 0.0.10 | 2025-07-19 | [63422](https://github.com/airbytehq/airbyte/pull/63422) | Update dependencies |
| 0.0.9 | 2025-07-12 | [63167](https://github.com/airbytehq/airbyte/pull/63167) | Update dependencies |
| 0.0.8 | 2025-07-05 | [62578](https://github.com/airbytehq/airbyte/pull/62578) | Update dependencies |
| 0.0.7 | 2025-06-28 | [62326](https://github.com/airbytehq/airbyte/pull/62326) | Update dependencies |
| 0.0.6 | 2025-06-21 | [61873](https://github.com/airbytehq/airbyte/pull/61873) | Update dependencies |
| 0.0.5 | 2025-06-14 | [60076](https://github.com/airbytehq/airbyte/pull/60076) | Update dependencies |
| 0.0.4 | 2025-05-03 | [59090](https://github.com/airbytehq/airbyte/pull/59090) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58522](https://github.com/airbytehq/airbyte/pull/58522) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57891](https://github.com/airbytehq/airbyte/pull/57891) | Update dependencies |
| 0.0.1 | 2025-04-06 | [57494](https://github.com/airbytehq/airbyte/pull/57494) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
