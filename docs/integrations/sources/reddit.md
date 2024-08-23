# Reddit
Close #44561
New Source: Reddit
## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `query` | `string` | Query. Specifies the query for searching in reddits and subreddits | airbyte |
| `include_over_18` | `boolean` | Include over 18 flag. Includes mature content | false |
| `exact` | `boolean` | Exact. Specifies exact keyword and reduces distractions |  |
| `limit` | `number` | Limit. Max records per page limit | 1000 |
| `subreddits` | `array` | Subreddits. Subreddits for exploration | [r/funny, r/AskReddit] |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| self | name | No pagination | ✅ |  ❌  |

| search |  | DefaultPaginator | ✅ |  ❌  |

| subreddit_search |  | DefaultPaginator | ✅ |  ❌  |

| message_inbox |  | DefaultPaginator | ✅ |  ❌  |

| subreddit_popular |  | DefaultPaginator | ✅ |  ❌  |

| subreddit_explore |  | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-23 | Initial release by btkcodedev via Connector Builder|

</details>