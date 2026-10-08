# Reddit

## Overview

The Reddit source supports _Full Refresh_ as well as _Incremental_ syncs.

_Full Refresh_ sync means every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.
_Incremental_ sync means only changed resources are copied from Reddit. For the first run, it will be a Full Refresh sync.


## Setup guide

### Step 1: Create a Reddit app

1. Visit [Reddit's app preferences page](https://www.reddit.com/prefs/apps) and select **create another app**.
2. Choose the app type:
   - **script** if you want to authenticate with your own Reddit username and password (simplest; does not work for accounts with two-factor authentication).
   - **web app** if you want to authenticate with an OAuth 2.0 refresh token.
3. Set a redirect URI (any URL you control, for example `http://localhost:8080`) and save the app.
4. Copy the **Client ID** (shown below the app name) and the **Client Secret** (labeled `secret`).

### Step 2: Choose an authentication method

Reddit access tokens expire after one hour, so pick one of the first two options to let Airbyte refresh the token on every sync.

#### Option A: Reddit username and password (script app)

Select **Reddit username and password (script app)** and enter the Client ID and Client Secret from Step 1 together with the Reddit username and password of the account that owns the app. Airbyte requests a fresh access token with the OAuth 2.0 `password` grant before each sync.

#### Option B: OAuth 2.0 refresh token

Select **OAuth 2.0 (refresh token)** and enter the Client ID, Client Secret and a refresh token. To obtain a refresh token, complete the [Reddit authorization code flow](https://github.com/reddit-archive/reddit/wiki/OAuth2#authorization) with `duration=permanent` and the scopes you need (`identity`, `read`, `privatemessages`, `mysubreddits`), then exchange the returned `code` at `https://www.reddit.com/api/v1/access_token` (HTTP Basic auth with the Client ID as the username and the Client Secret as the password, body `grant_type=authorization_code&code=<code>&redirect_uri=<redirect_uri>`). Copy the `refresh_token` from the response.

#### Option C: Access token (expires after one hour)

Select **Access token (expires after one hour)** and paste an access token obtained manually, for example with Postman:

- Request - POST `https://www.reddit.com/api/v1/access_token`
- Authorization - Basic Auth - `username: <CLIENT_ID>`, `password: <CLIENT_SECRET>`
- Body - x-www-form-urlencoded - `grant_type: password, username: YOUR_REDDIT_USERNAME, password: YOUR_REDDIT_PASSWORD`

The `access_token` in the response is the API Key. Because Airbyte cannot refresh it, this option only works for one-off syncs; existing connections configured with the legacy top-level `api_key` field are migrated to this option automatically.

## Records and rate limiting

- The Reddit API has [rate limiting of 100 queries per minute (QPM) per OAuth client ID](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki). It is handled with an exponential backoff strategy, with maximum 3 retries.
- Access tokens expire after one hour. With the username/password or refresh token options Airbyte obtains a new token automatically; with the access token option a new token must be generated manually.
- Reddit requires a descriptive `User-Agent`; the connector sends `airbyte:source-reddit:v1 (+https://docs.airbyte.com/integrations/sources/reddit)` on every request.
- The Reddit API has a hard limit of fetching 1000 records per single stream call with subsequent pagination.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `credentials` | `object` | Authentication. One of: OAuth 2.0 refresh token (`client_id`, `client_secret`, `refresh_token`), Reddit username and password (`client_id`, `client_secret`, `username`, `password`), or a short-lived access token (`api_key`). |  |
| `query` | `string` | Query. Specifies the query for searching in reddits and subreddits | airbyte |
| `include_over_18` | `boolean` | Include over 18 flag. Includes mature content | false |
| `exact` | `boolean` | Exact. Specifies exact keyword and reduces distractions |  |
| `limit` | `number` | Limit. Max records per page limit | 1000 |
| `subreddits` | `array` | Subreddits. Subreddits for exploration (`funny`, `r/funny` and `/r/funny` are all accepted) | [r/funny, r/AskReddit] |
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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       |Pull Request | Subject        |
|------------------|------------|--------------|----------------|
| 0.0.67 | 2026-10-07 | [88257](https://github.com/airbytehq/airbyte/pull/88257) | Add refreshable OAuth 2.0 (refresh token / password grant) authentication, send a descriptive User-Agent, fix `subreddit_explore` to iterate over the configured subreddits and read its `created` cursor, and harden pagination against non-object `data` responses |
| 0.0.66 | 2026-10-06 | [88007](https://github.com/airbytehq/airbyte/pull/88007) | Update dependencies |
| 0.0.65 | 2026-09-29 | [87320](https://github.com/airbytehq/airbyte/pull/87320) | Update dependencies |
| 0.0.64 | 2026-09-22 | [86793](https://github.com/airbytehq/airbyte/pull/86793) | Update dependencies |
| 0.0.63 | 2026-09-15 | [86199](https://github.com/airbytehq/airbyte/pull/86199) | Update dependencies |
| 0.0.62 | 2026-09-08 | [85627](https://github.com/airbytehq/airbyte/pull/85627) | Update dependencies |
| 0.0.61 | 2026-08-18 | [84754](https://github.com/airbytehq/airbyte/pull/84754) | Update dependencies |
| 0.0.60 | 2026-08-11 | [84090](https://github.com/airbytehq/airbyte/pull/84090) | Update dependencies |
| 0.0.59 | 2026-08-04 | [83607](https://github.com/airbytehq/airbyte/pull/83607) | Update dependencies |
| 0.0.58 | 2026-07-28 | [83067](https://github.com/airbytehq/airbyte/pull/83067) | Update dependencies |
| 0.0.57 | 2026-07-21 | [82583](https://github.com/airbytehq/airbyte/pull/82583) | Update dependencies |
| 0.0.56 | 2026-07-14 | [81975](https://github.com/airbytehq/airbyte/pull/81975) | Update dependencies |
| 0.0.55 | 2026-06-30 | [81234](https://github.com/airbytehq/airbyte/pull/81234) | Update dependencies |
| 0.0.54 | 2026-06-23 | [80628](https://github.com/airbytehq/airbyte/pull/80628) | Update dependencies |
| 0.0.53 | 2026-06-16 | [80049](https://github.com/airbytehq/airbyte/pull/80049) | Update dependencies |
| 0.0.52 | 2026-06-09 | [79512](https://github.com/airbytehq/airbyte/pull/79512) | Update dependencies |
| 0.0.51 | 2026-06-02 | [78919](https://github.com/airbytehq/airbyte/pull/78919) | Update dependencies |
| 0.0.50 | 2026-04-28 | [77395](https://github.com/airbytehq/airbyte/pull/77395) | Update dependencies |
| 0.0.49 | 2026-04-21 | [76717](https://github.com/airbytehq/airbyte/pull/76717) | Update dependencies |
| 0.0.48 | 2026-03-31 | [75878](https://github.com/airbytehq/airbyte/pull/75878) | Update dependencies |
| 0.0.47 | 2026-03-17 | [74911](https://github.com/airbytehq/airbyte/pull/74911) | Update dependencies |
| 0.0.46 | 2026-02-24 | [73532](https://github.com/airbytehq/airbyte/pull/73532) | Update dependencies |
| 0.0.45 | 2026-02-03 | [72651](https://github.com/airbytehq/airbyte/pull/72651) | Update dependencies |
| 0.0.44 | 2026-01-20 | [72024](https://github.com/airbytehq/airbyte/pull/72024) | Update dependencies |
| 0.0.43 | 2026-01-14 | [71479](https://github.com/airbytehq/airbyte/pull/71479) | Update dependencies |
| 0.0.42 | 2025-12-18 | [70617](https://github.com/airbytehq/airbyte/pull/70617) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70060](https://github.com/airbytehq/airbyte/pull/70060) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69624](https://github.com/airbytehq/airbyte/pull/69624) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68912](https://github.com/airbytehq/airbyte/pull/68912) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68335](https://github.com/airbytehq/airbyte/pull/68335) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67872](https://github.com/airbytehq/airbyte/pull/67872) | Update dependencies |
| 0.0.36 | 2025-10-08 | [67541](https://github.com/airbytehq/airbyte/pull/67541) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66443](https://github.com/airbytehq/airbyte/pull/66443) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65716](https://github.com/airbytehq/airbyte/pull/65716) | Update dependencies |
| 0.0.33 | 2025-08-24 | [65446](https://github.com/airbytehq/airbyte/pull/65446) | Update dependencies |
| 0.0.32 | 2025-08-10 | [64831](https://github.com/airbytehq/airbyte/pull/64831) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64457](https://github.com/airbytehq/airbyte/pull/64457) | Update dependencies |
| 0.0.30 | 2025-07-19 | [63628](https://github.com/airbytehq/airbyte/pull/63628) | Update dependencies |
| 0.0.29 | 2025-07-12 | [63054](https://github.com/airbytehq/airbyte/pull/63054) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62697](https://github.com/airbytehq/airbyte/pull/62697) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62217](https://github.com/airbytehq/airbyte/pull/62217) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61787](https://github.com/airbytehq/airbyte/pull/61787) | Update dependencies |
| 0.0.25 | 2025-06-14 | [60557](https://github.com/airbytehq/airbyte/pull/60557) | Update dependencies |
| 0.0.24 | 2025-05-10 | [60162](https://github.com/airbytehq/airbyte/pull/60162) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59473](https://github.com/airbytehq/airbyte/pull/59473) | Update dependencies |
| 0.0.22 | 2025-04-27 | [59106](https://github.com/airbytehq/airbyte/pull/59106) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58458](https://github.com/airbytehq/airbyte/pull/58458) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57923](https://github.com/airbytehq/airbyte/pull/57923) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57298](https://github.com/airbytehq/airbyte/pull/57298) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56770](https://github.com/airbytehq/airbyte/pull/56770) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56163](https://github.com/airbytehq/airbyte/pull/56163) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55061](https://github.com/airbytehq/airbyte/pull/55061) | Update dependencies |
| 0.0.15 | 2025-02-23 | [54586](https://github.com/airbytehq/airbyte/pull/54586) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53957](https://github.com/airbytehq/airbyte/pull/53957) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53455](https://github.com/airbytehq/airbyte/pull/53455) | Update dependencies |
| 0.0.12 | 2025-02-01 | [53004](https://github.com/airbytehq/airbyte/pull/53004) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52494](https://github.com/airbytehq/airbyte/pull/52494) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51854](https://github.com/airbytehq/airbyte/pull/51854) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51376](https://github.com/airbytehq/airbyte/pull/51376) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50683](https://github.com/airbytehq/airbyte/pull/50683) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50232](https://github.com/airbytehq/airbyte/pull/50232) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49697](https://github.com/airbytehq/airbyte/pull/49697) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49368](https://github.com/airbytehq/airbyte/pull/49368) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49104](https://github.com/airbytehq/airbyte/pull/49104) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47827](https://github.com/airbytehq/airbyte/pull/47827) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47542](https://github.com/airbytehq/airbyte/pull/47542) | Update dependencies |
| 0.0.1 | 2024-08-23 | [44579](https://github.com/airbytehq/airbyte/pull/44579) | Initial release by [btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
