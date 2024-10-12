# Tempo.io
This is the Tempo.io source connector that ingests data from the tempo.io API. 
Tempo is a flexible and modular portfolio management solutions for Jira. https://www.tempo.io/

In order to use this source, you must first create an account on Tempo.io and be a business plan user. Once logged in, you will have to add it to your Jira cloud account as an App. 

This source uses OAuth Bearer token for authentication. To obtain your token, head over to Tempo&gt;Settings, scroll down to Data Access and select API integration.
You can find more about the API here https://apidocs.tempo.io/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| workload-schemes | id | DefaultPaginator | ✅ |  ❌  |
| account-categories | id | DefaultPaginator | ✅ |  ❌  |
| account-category-types |  | DefaultPaginator | ✅ |  ❌  |
| holiday-schemes | id | DefaultPaginator | ✅ |  ❌  |
| programs | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| skills | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| work-attributes | key | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-12 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
