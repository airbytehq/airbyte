# Reddit

## Overview

The Reddit source supports _Full Refresh_ as well as _Incremental_ syncs.

_Full Refresh_ sync means every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.
_Incremental_ sync means only changed resources are copied from Reddit. For the first run, it will be a Full Refresh sync.


## Steps for getting api_key

We can make a POST request from postman with username and password of reddit inorder to get api_keys for making requests
First make an app for getting id and secret for authentication
1. Go to Reddit's App Preferences Page:
- Visit `https://www.reddit.com/prefs/apps` and select `create another app` and input name and select `script` as option and redirect uri as `https://oauth.pstmn.io/v1/callback`

2. Copy Your App Credentials:
 - After creating the app, you will see the Client ID (below your app name) and Client Secret (labeled as "secret").
 - Client ID: Copy this value as it will be your Authorization Username in Postman.
 - Client Secret: Copy this value as it will be your Authorization Password in Postman.

3. Visit postman web/app
 - Make a new request with following guidelines
 - Request - POST https://www.reddit.com/api/v1/access_token
 - Authorization - Basic Auth - Username: YOUR_COPIED_USERNAME, Password: YOUR_COPIED_PASSWORD
 - Body - x-www-form-urlencoded - grant_type: password, username: YOUR_REDDIT_USERNAME, password: YOUR_REDDIT_PASSWORD

Hit send to receive api_key as response under `access_token`

## Records and rate limiting

- The API has rate limiting as 100 queries per minute (QPM) per OAuth client id, it is dently handled with exponenential backoff strategy, with maximum 3 retries. Refer url for more information: `https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki`
If the api_key expires, user has to manually request for new access token through postman and try again.
- The reddit api has a hard limit of fetch 1000 records for a single stream call with subsequent pagination.

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