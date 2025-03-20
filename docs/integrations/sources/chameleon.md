# Chameleon
This page contains the setup guide and reference information for the [Chameleon](https://app.chameleon.io/) source connector.

## Documentation reference:
Visit `https://developers.chameleon.io/#/apis/overview` for API documentation

## Authentication setup
`Chameleon` uses API Key authentication,
Refer `https://app.chameleon.io/settings/tokens` for getting your API key.


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |
| `filter` | `string` | Filter. Filter for using in the `segments_experiences` stream | tour |
| `end_date` | `string` | End date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| helpbars | id | No pagination | ✅ |  ✅  |
| segments | id | No pagination | ✅ |  ✅  |
| urls | id | No pagination | ✅ |  ✅  |
| url_groups | id | No pagination | ✅ |  ✅  |
| changes | id | No pagination | ✅ |  ✅ |
| launchers | id | No pagination | ✅ |  ✅  |
| tooltips | id | No pagination | ✅ |  ✅  |
| tours | id | No pagination | ✅ |  ✅  |
| surveys | id | No pagination | ✅ |  ✅  |
| survey_responses | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Pull Request | Subject        |
|------------------|------------|--------------|----------------|
| 0.1.15 | 2025-03-08 | [55378](https://github.com/airbytehq/airbyte/pull/55378) | Update dependencies |
| 0.1.14 | 2025-03-01 | [54844](https://github.com/airbytehq/airbyte/pull/54844) | Update dependencies |
| 0.1.13 | 2025-02-22 | [54240](https://github.com/airbytehq/airbyte/pull/54240) | Update dependencies |
| 0.1.12 | 2025-02-15 | [53904](https://github.com/airbytehq/airbyte/pull/53904) | Update dependencies |
| 0.1.11 | 2025-02-08 | [53395](https://github.com/airbytehq/airbyte/pull/53395) | Update dependencies |
| 0.1.10 | 2025-02-01 | [52950](https://github.com/airbytehq/airbyte/pull/52950) | Update dependencies |
| 0.1.9 | 2025-01-25 | [52157](https://github.com/airbytehq/airbyte/pull/52157) | Update dependencies |
| 0.1.8 | 2025-01-18 | [51772](https://github.com/airbytehq/airbyte/pull/51772) | Update dependencies |
| 0.1.7 | 2025-01-11 | [51255](https://github.com/airbytehq/airbyte/pull/51255) | Update dependencies |
| 0.1.6 | 2024-12-28 | [50450](https://github.com/airbytehq/airbyte/pull/50450) | Update dependencies |
| 0.1.5 | 2024-12-21 | [50165](https://github.com/airbytehq/airbyte/pull/50165) | Update dependencies |
| 0.1.4 | 2024-12-14 | [49577](https://github.com/airbytehq/airbyte/pull/49577) | Update dependencies |
| 0.1.3 | 2024-12-12 | [49018](https://github.com/airbytehq/airbyte/pull/49018) | Update dependencies |
| 0.1.2 | 2024-11-04 | [48250](https://github.com/airbytehq/airbyte/pull/48250) | Update dependencies |
| 0.1.1 | 2024-10-29 | [47822](https://github.com/airbytehq/airbyte/pull/47822) | Update dependencies |
| 0.1.0 | 2024-09-29 | [46248](https://github.com/airbytehq/airbyte/pull/46248) | Fix survey_responses stream schema and icon |
| 0.0.2 | 2024-09-21 | [45708](https://github.com/airbytehq/airbyte/pull/45708) | Make end date optional |
| 0.0.1 | 2024-09-18 | [45658](https://github.com/airbytehq/airbyte/pull/45658) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
