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
| 0.0.1 | 2024-10-27 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
