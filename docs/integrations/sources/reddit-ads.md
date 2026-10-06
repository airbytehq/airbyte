# Reddit Ads

The Reddit Ads source syncs campaigns, ads, and daily campaign performance metrics from the [Reddit Ads API v3](https://ads-api.reddit.com/docs/v3/api/reddit-advertising-api) for a single ad account.

## Prerequisites

- A [Reddit Ads](https://ads.reddit.com) account with at least one ad account.
- A Reddit developer app, which gives you the app ID and secret this connector uses as its OAuth client ID and client secret. Only business admins with a verified Reddit account can create one.
- An OAuth refresh token for that app, authorized with the `adsread` scope.
- The ID of the ad account you want to sync.

## Set up the Reddit Ads source

### Step 1: Create a developer app

1. In [Reddit Ads Manager](https://ads.reddit.com), open your business's **Developer Applications** page.
2. Select **Add Apps** > **Create an app**, then fill in the app name, About URL, redirect URL, and primary contact. Reddit requires a redirect URL even though the connector never uses it interactively, so any URL you control works, such as `https://example.com/oauth/callback`.
3. Select **Create App**. Reddit shows the app ID and secret. Copy both. The app ID is your **OAuth Client ID** and the secret is your **OAuth Client Secret**.

If you already have a Reddit app under **Preferences** > **Apps**, you can select **Add Apps** > **Migrate an existing app** instead. Migrating limits the app's scope to the Ads API.

For details, see Reddit's [Create a Developer Application](https://ads-api.reddit.com/docs/v3/guides/quick-start/create-dev-app) guide.

### Step 2: Get a refresh token

The connector authenticates with the OAuth refresh token grant, so you need a long-lived refresh token. Get one with the authorization code flow described in Reddit's [authentication guide](https://ads-api.reddit.com/docs/v3/guides/quick-start/authenticate).

1. Sign in to Reddit as the user whose ads data you want to sync, then open the following URL in a browser, replacing the placeholders:

   ```text
   https://www.reddit.com/api/v1/authorize?client_id=YOUR_APP_ID&response_type=code&state=airbyte&redirect_uri=YOUR_REDIRECT_URL&duration=permanent&scope=adsread
   ```

   Set `duration` to `permanent`. A `temporary` authorization doesn't return a refresh token, and the connector can't sync without one. `adsread` is the only scope the connector needs.

2. Select **Allow**. Reddit redirects to your redirect URL with a `code` query parameter. Copy the code, removing any trailing `#_` characters. The code expires after 10 minutes and works only once.

3. Exchange the code for tokens:

   ```bash
   curl -X POST https://www.reddit.com/api/v1/access_token \
     -H 'content-type: application/x-www-form-urlencoded' \
     -A 'YOUR_USER_AGENT' \
     -u 'YOUR_APP_ID:YOUR_APP_SECRET' \
     -d 'grant_type=authorization_code&code=YOUR_CODE&redirect_uri=YOUR_REDIRECT_URL'
   ```

4. Copy the `refresh_token` value from the response. That's your **OAuth Refresh Token**. The connector uses it to obtain access tokens itself, so you don't need the `access_token` value.

### Step 3: Find your ad account ID

In [Reddit Ads Manager](https://ads.reddit.com), open **Business Manager** > **Assets** > **Ad Accounts**. The ID appears under the ad account's name and starts with `a2_`. You can also call [List Ad Accounts By Business](https://ads-api.reddit.com/docs/v3/api/ad-accounts) with the token you just created.

### Step 4: Configure the source in Airbyte

Enter the client ID, client secret, refresh token, and ad account ID, then set the remaining fields:

- **User Agent**: Reddit requires a descriptive user agent on every request, in the format `platform:app_id:version (by /u/username)`. For example, `airbyte:reddit-ads-sync:v1.0 (by /u/your-username)`. Reddit heavily throttles default user agents such as `Python/urllib` or `Java`.
- **Start Date**: Optional. The earliest data to sync, in RFC 3339 format with a UTC offset, such as `2024-05-11T00:00:00Z`. It applies to all three streams: it's the earliest `modified_at` for `ad` and `campaign`, and the earliest report date for `campaign_report`. If you leave it empty, all three streams start 24 months before the current sync.
- **Number of Concurrent Workers**: Optional. The number of requests the connector runs in parallel, from 1 to 10. The default is 3. Higher values can speed up syncs, but they make Reddit rate limiting more likely.

## Supported streams

| Stream | API endpoint | Primary key | Incremental cursor |
| --- | --- | --- | --- |
| `ad` | `GET /api/v3/ad_accounts/{ad_account_id}/ads` | `id` | `modified_at` |
| `campaign` | `GET /api/v3/ad_accounts/{ad_account_id}/campaigns` | `id` | `modified_at` |
| `campaign_report` | `POST /api/v3/ad_accounts/{ad_account_id}/reports` | `campaign_id`, `date` | `date` |

All three streams support full refresh and incremental sync, and all read from the single ad account you configure. To sync more than one ad account, create one source per account.

`campaign_report` returns one row per campaign per day, in GMT, with delivery and conversion metrics such as impressions, clicks, spend, reach, frequency, and per-objective conversion counts and values.

## Sync behavior and limitations

- **Report metrics use micro-units.** Reddit returns `spend`, `cpc`, `cpv`, `ecpm`, and the `conversion_*_ecpa` metrics multiplied by 1,000,000, and the `conversion_*_total_value` metrics multiplied by 100. The connector loads these values unchanged, so divide them in your destination before reporting on currency amounts.
- **Recent report data changes after it lands.** Reddit says metrics can take up to 6 hours to stabilize, and conversion data keeps updating as events arrive. The `campaign_report` stream re-reads a 7-hour window on each sync to pick up late updates, but rows for the last day or two can still change after they're synced.
- **Report history has a limit.** Delivery data goes back 24 months, and reach and frequency data start in June 2024. If you set **Start Date** earlier than 24 months ago, `campaign_report` still starts 24 months before the current sync, because Reddit rejects requests for older report data. The `ad` and `campaign` streams aren't clamped.
- **Reports are campaign-level only.** `campaign_report` breaks metrics down by campaign and date, so ad group and ad metrics aren't available in this connector.
- **Versions earlier than 0.0.9 synced only the first page of each stream.** Reddit returns the next page token URL-encoded, and earlier versions passed it back without decoding it, so every stream stopped after its first page. If you upgraded from an earlier version and records are missing in your destination, clear the affected streams and run a new sync.
- **Start Date filtering happens after the fetch.** For `ad` and `campaign`, the Reddit API has no server-side filter on `modified_at`, so the connector requests every record in the ad account on each sync and discards those modified before your cursor value. Sync duration scales with the size of the account, not with the amount of new data.

## Performance considerations

Reddit applies rate limits per authorized user and per endpoint group, so sources that use the same Reddit user share those limits. The connector calls endpoints in two groups:

| Reddit rate limit group | Endpoints | Streams | Quota |
| --- | --- | --- | --- |
| `ads-campaign-management-read` | List Ads, List Campaigns | `ad`, `campaign` | 400 requests per 60 seconds |
| `ads-reporting` | Get A Report | `campaign_report` | 60 requests per 60 seconds |

The connector throttles its own requests to stay within these quotas. It only counts the requests it makes itself, so other sources or applications that use the same Reddit user can still push the account over the limit. `campaign_report` requests three days of report data per call, so a long backfill makes many report calls in sequence.

By default, the connector runs up to 3 requests in parallel. You can change this with **Number of Concurrent Workers**, up to a maximum of 10. If syncs hit rate limits often, lower this value.

The connector retries `429` and `5xx` responses up to 10 times with exponential backoff. For `campaign_report`, it waits 60 seconds between `5xx` retries. For the full list of policies, see Reddit's [rate limiting](https://ads-api.reddit.com/docs/v3/api/reddit-advertising-api) documentation.

The connector reuses an access token until it expires, then refreshes it. If a request still fails with `401`, the connector refreshes the token and retries that request. If Reddit returns a new refresh token during a refresh, the connector saves it to the source configuration, so you don't have to rotate it yourself.

## Troubleshooting

| Error | Cause and fix |
| --- | --- |
| Refresh token was rejected by the OAuth provider | Reddit's token endpoint rejected the refresh token or the client credentials. Confirm the OAuth Client ID and Client Secret, then [get a new refresh token](#step-2-get-a-refresh-token) with `duration=permanent`. |
| Reddit denied access to ad account (HTTP 403) | The refresh token lacks the `adsread` scope, or the Reddit user who authorized it can't access this ad account. Get a new refresh token with the `adsread` scope while signed in as a user with access to the ad account. |
| Reddit could not find ad account (HTTP 404) or Reddit rejected the ad account ID | The **Ad Account ID** is wrong. [Find your ad account ID](#step-3-find-your-ad-account-id), which starts with `a2_`, and update the source. |
| Reddit rejected the request as invalid (HTTP 400) | Reddit rejected the request for a reason unrelated to the ad account. The error message includes the explanation Reddit returned. |

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `start_time` | `string` | Optional UTC start date applied to all three streams, in YYYY-MM-DDTHH:MM:SSZ format. A value earlier than 24 months ago is clamped for `campaign_report`, because Reddit only serves report data for the last 24 months. | 24 months before the current date |
| `user_agent` | `string` | User Agent. A unique and descriptive user agent string in the format: platform:app_id:version (by /u/yourusername). Required for all requests. |  |
| `ad_account_id` | `string` | The Reddit Ads account ID to sync, shown in Reddit Ads Manager, for example a2_abc123. |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |
| `num_workers` | `integer` | Number of concurrent workers. Higher values speed up syncs but increase the chance of Reddit rate limiting. | 3 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ad | id | DefaultPaginator | ✅ |  ✅  |
| campaign | id | DefaultPaginator | ✅ |  ✅  |
| campaign_report | campaign_id.date | DefaultPaginator | ✅ |  ✅  |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-10-05 | [87043](https://github.com/airbytehq/airbyte/pull/87043) | Show actionable errors for rejected refresh tokens or client credentials, invalid ad account IDs, and 400/403/404 responses, add a client-side API budget and configurable concurrency, add suggested streams, make spec titles human-readable, and add unit tests |
| 0.0.12 | 2026-09-29 | [87338](https://github.com/airbytehq/airbyte/pull/87338) | Update dependencies |
| 0.0.11 | 2026-09-22 | [86789](https://github.com/airbytehq/airbyte/pull/86789) | Update dependencies |
| 0.0.10 | 2026-09-15 | [86198](https://github.com/airbytehq/airbyte/pull/86198) | Update dependencies |
| 0.0.9 | 2026-09-09 | [84850](https://github.com/airbytehq/airbyte/pull/84850) | Fix pagination so every stream syncs all pages instead of only the first |
| 0.0.8 | 2026-09-08 | [85629](https://github.com/airbytehq/airbyte/pull/85629) | Update dependencies |
| 0.0.7 | 2026-08-18 | [84348](https://github.com/airbytehq/airbyte/pull/84348) | Enable acceptance test suite with GSM test secrets |
| 0.0.6 | 2026-08-18 | [84725](https://github.com/airbytehq/airbyte/pull/84725) | Update dependencies |
| 0.0.5 | 2026-08-11 | [84089](https://github.com/airbytehq/airbyte/pull/84089) | Update dependencies |
| 0.0.4 | 2026-08-04 | [83603](https://github.com/airbytehq/airbyte/pull/83603) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83266](https://github.com/airbytehq/airbyte/pull/83266) | Stop refreshing the access token before every request, and refresh it before retrying a 401. Make `start_time` optional, apply it to all three streams, and default it to 24 months before the sync; clamp `campaign_report` to Reddit's 24-month reporting window |
| 0.0.2 | 2026-07-28 | [83100](https://github.com/airbytehq/airbyte/pull/83100) | Update dependencies |
| 0.0.1 | 2026-07-27 | [81399](https://github.com/airbytehq/airbyte/pull/81399) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
