# High Level
Proxy connector for [Go High Level](https://gohighlevel.com) (Lead Connector). Requires a paid subscription to the proxy service.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `location_id` | `string` | Location ID.  |  |
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Contacts | id | DefaultPaginator | ✅ |  ❌  |
| Payments | _id | DefaultPaginator | ✅ |  ❌  |
| Form Submissions | id | DefaultPaginator | ✅ |  ❌  |
| Custom Fields | id | No pagination | ✅ |  ❌  |
| Transactions | _id | DefaultPaginator | ✅ |  ❌  |
| Invoices | _id | DefaultPaginator | ✅ |  ❌  |
| Opportunities | id | DefaultPaginator | ✅ |  ❌  |
| Pipelines | id | No pagination | ✅ |  ❌  |
| Subscriptions | _id | DefaultPaginator | ✅ |  ❌  |
| Orders | _id | DefaultPaginator | ✅ |  ❌  |
| Order | _id | No pagination | ✅ |  ❌  |
| Contact Search | id | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.5 | 2024-12-14 | [49640](https://github.com/airbytehq/airbyte/pull/49640) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49237](https://github.com/airbytehq/airbyte/pull/49237) | Update dependencies |
| 0.0.3 | 2024-12-11 | [48901](https://github.com/airbytehq/airbyte/pull/48901) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-28 | [47472](https://github.com/airbytehq/airbyte/pull/47472) | Update dependencies |
| 0.0.1 | 2024-08-23 | | Initial release by [@Stockotaco](https://github.com/stockotaco) via Connector Builder |

</details>
