# Deputy
This is the Deputy source that ingests data from the Deputy API.

Deputy is a software that simplifies employee scheduling, timesheets and HR in one place https://www.deputy.com/

In order to use this source you must first create an account on Deputy.
Once logged in, your Deputy install will have a specific URL in the structure of `https://[installname].[geo].deputy.com` - This is the same URL that will be the base API url .

To obtain your bearer token to use the API, follow the steps shown here https://developer.deputy.com/deputy-docs/docs/the-hello-world-of-deputy
This will have you create an oauth application and create an access token. Enter the access token in the input field.

You can learn more about the API here https://developer.deputy.com/deputy-docs/reference/getlocations

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | Base URL. The base url for your deputy account to make API requests. Example: `https://my890.as.deputy.com` |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| locations | Id | No pagination | ✅ |  ❌  |
| employees | Id | No pagination | ✅ |  ❌  |
| award_lists | AwardCode | No pagination | ✅ |  ❌  |
| departments | Id | No pagination | ✅ |  ❌  |
| timesheets | Id | No pagination | ✅ |  ❌  |
| tasks | Id | No pagination | ✅ |  ❌  |
| news_feed | Id | No pagination | ✅ |  ❌  |
| addresses | Id | No pagination | ✅ |  ❌  |
| categories | Id | No pagination | ✅ |  ❌  |
| comments | Id | No pagination | ✅ |  ❌  |
| company_periods | Id | No pagination | ✅ |  ❌  |
| employee_agreements | Id | No pagination | ✅ |  ❌  |
| employee | Id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.12 | 2025-02-22 | [54446](https://github.com/airbytehq/airbyte/pull/54446) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53351](https://github.com/airbytehq/airbyte/pull/53351) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52829](https://github.com/airbytehq/airbyte/pull/52829) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52315](https://github.com/airbytehq/airbyte/pull/52315) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51674](https://github.com/airbytehq/airbyte/pull/51674) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51100](https://github.com/airbytehq/airbyte/pull/51100) | Update dependencies |
| 0.0.6 | 2025-01-04 | [50585](https://github.com/airbytehq/airbyte/pull/50585) | Update dependencies |
| 0.0.5 | 2024-12-21 | [49991](https://github.com/airbytehq/airbyte/pull/49991) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49534](https://github.com/airbytehq/airbyte/pull/49534) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49170](https://github.com/airbytehq/airbyte/pull/49170) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48934](https://github.com/airbytehq/airbyte/pull/48934) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-27 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
