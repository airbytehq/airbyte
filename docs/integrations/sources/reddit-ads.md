# Reddit Ads

The Reddit Ads source syncs an ad account, campaigns, ads, ad groups, and daily account, campaign, ad group, and ad performance metrics from the [Reddit Ads API v3](https://ads-api.reddit.com/docs/v3/api/reddit-advertising-api) for a single ad account.

## Prerequisites

- A [Reddit Ads](https://ads.reddit.com) account with at least one ad account, and a Reddit user who can access the ad account you want to sync.
- The **Ad Account ID** of the ad account you want to sync. It starts with `a2_`. See [Find your ad account ID](#find-your-ad-account-id).
- Credentials for the **Authentication** field, depending on the option you choose:
  - **Authenticate with Reddit**: Nothing to prepare. You sign in to Reddit from Airbyte, and Airbyte obtains the refresh token for you.
  - **Use your own Reddit app**:
    - The **OAuth Client ID** and **OAuth Client Secret** of a Reddit developer app. The app ID and secret Reddit shows for the app are the client ID and client secret this connector uses. Only business admins with a verified Reddit account can create a developer app. See [Create a developer app](#create-a-developer-app).
    - An **OAuth Refresh Token** for that app, authorized with the `adsread` scope. See [Get a refresh token](#get-a-refresh-token).
- Optional: a **User Agent** to send when the connector requests access tokens from Reddit. If you leave it empty, the connector sends an Airbyte user agent.

## Setup guide

The connector offers two **Authentication** options:

- **Authenticate with Reddit**: Sign in to Reddit from Airbyte, and Airbyte obtains the refresh token for you. This is the default option in Airbyte Cloud. You don't need your own developer app, so skip [Create a developer app](#create-a-developer-app) and [Get a refresh token](#get-a-refresh-token).
- **Use your own Reddit app**: Enter the client ID, client secret, and refresh token of a Reddit developer app you manage. Use this option in self-managed Airbyte, or if you already have a developer app. Complete [Create a developer app](#create-a-developer-app) and [Get a refresh token](#get-a-refresh-token) first.

Sources created before version 0.2.0 move to **Use your own Reddit app** automatically and keep their existing client ID, client secret, and refresh token, so they need no action.

### Step 1: Set up Reddit Ads

#### Create a developer app

You need a developer app only for the **Use your own Reddit app** option.

1. In [Reddit Ads Manager](https://ads.reddit.com), open your business's **Developer Applications** page.
2. Select **Add Apps** > **Create an app**, then fill in the app name, About URL, redirect URL, and primary contact. Reddit requires a redirect URL even though the connector never uses it interactively, so any URL you control works, such as `https://example.com/oauth/callback`.
3. Select **Create App**. Reddit shows the app ID and secret. Copy both. The app ID is your **OAuth Client ID** and the secret is your **OAuth Client Secret**.

If you already have a Reddit app under **Preferences** > **Apps**, you can select **Add Apps** > **Migrate an existing app** instead. Migrating limits the app's scope to the Ads API.

For details, see Reddit's [Create a Developer Application](https://ads-api.reddit.com/docs/v3/guides/quick-start/create-dev-app) guide.

#### Get a refresh token

You need a refresh token only for the **Use your own Reddit app** option. The connector authenticates with the OAuth refresh token grant, so you need a long-lived refresh token. Get one with the authorization code flow described in Reddit's [authentication guide](https://ads-api.reddit.com/docs/v3/guides/quick-start/authenticate).

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

#### Find your ad account ID

Sign in to [Reddit Ads Manager](https://ads.reddit.com/account/). Your ad account ID appears in the top right corner and starts with `a2_`.

You can also open **Business Manager** > **Assets** > **Ad Accounts** in Reddit Ads Manager, where the ID appears under the ad account's name and starts with `a2_`. Alternatively, call [List Ad Accounts By Business](https://ads-api.reddit.com/docs/v3/api/ad-accounts) with an access token for your app.

### Step 2: Set up the Reddit Ads connector in Airbyte

Apart from **Authentication**, the source has the same fields in Airbyte Cloud and Airbyte Open Source:

- **Ad Account ID**: Required. The ID from [Find your ad account ID](#find-your-ad-account-id), such as `a2_abc123`.
- **User Agent**: Optional. The [user agent](https://ads-api.reddit.com/docs/v3/api/reddit-advertising-api#user-agents) the connector sends when it requests a new access token from Reddit's token endpoint, `https://www.reddit.com/api/v1/access_token`. Reddit recommends the format `platform:app_id:version (by /u/username)`, for example `airbyte:reddit-ads-sync:v1.0 (by /u/your-username)`. If you leave it empty, the connector sends `airbyte:source-reddit-ads:v1`. The connector doesn't send this value on the requests that read your ads data.
- **Start Date**: Optional. The earliest data to sync, in RFC 3339 format with a UTC offset, such as `2024-05-11T00:00:00Z`. It applies to the incremental streams: it's the earliest `modified_at` for `ad`, `ad_group`, and `campaign`, and the earliest report date for the four report streams. If you leave it empty, those streams start 24 months before the current sync.
- **Number of Concurrent Workers**: Optional. The number of requests the connector runs in parallel, from 1 to 10. The default is 3. Higher values can speed up syncs, but they make Reddit rate limiting more likely.
- **Report Lookback Window (Days)**: Optional. How many whole days before the last synced report date to re-read on each incremental sync, from 0 to 30. The default is 7 days.

#### For Airbyte Cloud:

1. In Airbyte Cloud, create a new source and select **Reddit Ads**.
2. Under **Authentication**, select **Authenticate with Reddit**, then select **Authenticate your Reddit Ads account**. Sign in to Reddit as a user who can access the ad account you want to sync, and select **Allow**. If you prefer to use your own developer app, select **Use your own Reddit app** instead and follow step 2 of [For Airbyte Open Source](#for-airbyte-open-source).
3. Enter the **Ad Account ID**.
4. Optionally, set **User Agent**, **Start Date**, **Number of Concurrent Workers**, and **Report Lookback Window (Days)**.
5. Select **Set up source**.

#### For Airbyte Open Source:

1. In Airbyte, create a new source and select **Reddit Ads**.
2. Under **Authentication**, select **Use your own Reddit app**, then enter the **OAuth Client ID** and **OAuth Client Secret** from [Create a developer app](#create-a-developer-app) and the **OAuth Refresh Token** from [Get a refresh token](#get-a-refresh-token).
3. Enter the **Ad Account ID**.
4. Optionally, set **User Agent**, **Start Date**, **Number of Concurrent Workers**, and **Report Lookback Window (Days)**.
5. Select **Set up source**.

## Supported sync modes

The Reddit Ads source supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

`ad_account` supports full refresh only. The other seven streams support both full refresh and incremental sync.

## Supported Streams

| Stream | API endpoint | Primary key | Incremental cursor |
| --- | --- | --- | --- |
| `ad_account` | `GET /api/v3/ad_accounts/{ad_account_id}` | `id` | None |
| `ad` | `GET /api/v3/ad_accounts/{ad_account_id}/ads` | `id` | `modified_at` |
| `ad_group` | `GET /api/v3/ad_accounts/{ad_account_id}/ad_groups` | `id` | `modified_at` |
| `campaign` | `GET /api/v3/ad_accounts/{ad_account_id}/campaigns` | `id` | `modified_at` |
| `ad_account_report` | `POST /api/v3/ad_accounts/{ad_account_id}/reports` | `account_id`, `date` | `date` |
| `campaign_report` | `POST /api/v3/ad_accounts/{ad_account_id}/reports` | `campaign_id`, `date` | `date` |
| `ad_group_report` | `POST /api/v3/ad_accounts/{ad_account_id}/reports` | `ad_group_id`, `date` | `date` |
| `ad_report` | `POST /api/v3/ad_accounts/{ad_account_id}/reports` | `ad_id`, `date` | `date` |

All eight streams read from the single ad account you configure. To sync more than one ad account, create one source per account.

`campaign_report`, `ad_account_report`, `ad_group_report`, and `ad_report` return one row per campaign, account, ad group, or ad per UTC day, respectively, with delivery and conversion metrics such as impressions, clicks, spend, reach, frequency, and per-objective conversion counts and values.

### Performance considerations

Reddit applies rate limits per Reddit app, authorized user, and endpoint group, so sources that use the same app and Reddit user share those limits. The connector calls endpoints in two groups:

| Reddit rate limit group | Endpoints | Streams | Quota |
| --- | --- | --- | --- |
| `ads-campaign-management-read` | Get Ad Account, List Ads, List Ad Groups, List Campaigns | `ad_account`, `ad`, `ad_group`, `campaign` | 400 requests per 60 seconds |
| `ads-reporting` | Get A Report | `ad_account_report`, `campaign_report`, `ad_group_report`, `ad_report` | 60 requests per 60 seconds |

The connector throttles its own requests to stay within these quotas. It only counts the requests it makes itself, so other sources that use the same app and Reddit user can still push it over the limit. Each report stream requests contiguous three-day UTC windows per call, so a long backfill makes many report calls.

By default, the connector runs up to 3 requests in parallel. You can change this with **Number of Concurrent Workers**, up to a maximum of 10. If syncs hit rate limits often, lower this value.

The connector retries `429` and `5xx` responses up to 10 times with exponential backoff. For the full list of endpoint groups and quotas, see Reddit's [rate limiting](https://ads-api.reddit.com/docs/v3/guides/quick-start/rate-limiting#rate-limit-endpoint-groups) documentation.

The connector reuses an access token until it expires, then refreshes it. If a request still fails with `401`, the connector refreshes the token and retries that request. If Reddit returns a new refresh token during a refresh, the connector saves it to the source configuration, so you don't have to rotate it yourself.

## Limitations & Troubleshooting

### Sync behavior and limitations

- **Report metrics use micro-units.** Reddit returns `spend`, `cpc`, `cpv`, `ecpm`, and the `conversion_*_ecpa` metrics multiplied by 1,000,000, and the `conversion_*_total_value` metrics multiplied by 100. The connector loads these values unchanged, so divide them in your destination before reporting on currency amounts. Since version 1.0.0, `spend` and the `conversion_*_total_value` metrics are integers, and integer division truncates in some warehouses, so cast them to a decimal type before you divide.
- **Recent report data changes after it lands.** Reddit says metrics can take up to 6 hours to stabilize, and it applies late conversions for earlier hours or days in a daily refresh. Each incremental report-stream sync re-reads the last synced date plus the configured **Report Lookback Window (Days)**. Conversion metrics follow your ad account's attribution window, so raise the lookback to cover it, up to 30 days, if you need late conversions on older days. Use **Incremental | Append + Deduped** so re-read rows replace the earlier ones. The row for the current UTC day stays partial until a sync runs after that day ends.
- **Report streams re-read days without data.** A report stream saves the date of the latest row it read as its state. If an ad account has no delivery after that date, each incremental sync requests all later days again, and an account that has never had delivery requests the full 24 months on every sync.
- **Refresh the source schema after upgrading to 1.0.0.** Version 1.0.0 types the `ad` and `campaign` timestamps as date-times, the report `date` as a date in `YYYY-MM-DD` format, and 26 count and micro-currency report metrics plus `campaign.spend_cap` as integers. It also adds `start_time` and `end_time` to `campaign`. Connections that sync only `ad_account` and `ad_group` need no action. Clear a stream only if a sync fails after the schema refresh: some destinations, such as S3 Data Lake and other Iceberg destinations, can't change an existing column's type. In that case, back up the affected tables, then clear only the streams named in the error and sync them again. For the full steps and the risks of clearing report streams, see the [Reddit Ads migration guide](./reddit-ads-migrations.md#upgrading-to-100).
- **Refresh `campaign_report` after upgrading from a version earlier than 0.3.0.** Earlier versions requested report windows with gaps, so any sync that covered more than three days, including the first sync, left some dates missing or partial. Each incremental sync also re-sent the row for the day before the last synced date with only that day's last 7 hours of data. The lookback window only corrects recent days, so run a [refresh](https://docs.airbyte.com/platform/operator-guides/refreshes) with **Refresh stream and retain records**. In **Incremental | Append** mode, keep the latest row for each `campaign_id` and `date`. Don't use **Refresh stream and remove records** or **Clear**: Reddit only serves the last 24 months of report data, so older rows can't be synced again. Full refresh syncs correct themselves on the next sync.
- **Report history has a limit.** Delivery data goes back 24 months, and reach and frequency data start in June 2024. If you set **Start Date** earlier than 24 months ago, report streams still start 24 months before the current sync, because Reddit rejects requests for older report data. `ad`, `ad_group`, and `campaign` aren't clamped.
- **Report streams use fixed breakdowns.** Each report stream breaks metrics down by its entity ID and UTC date. `ad_group_report` and `ad_report` are also broken down by campaign, so their rows include `campaign_id`. `ad_account_report` sets `account_id` to your **Ad Account ID**. To get the ad group of an `ad_report` row, join `ad` on `ad_id`. Breakdowns such as country or region, and custom conversion events by name, aren't available.
- **Versions earlier than 0.0.9 synced only the first page of each stream.** Reddit returns the next page token URL-encoded, and earlier versions passed it back without decoding it, so every stream stopped after its first page. If you upgraded from an earlier version and records are missing in your destination, clear the affected streams and run a new sync.
- **`ad`, `ad_group`, and `campaign` read every record on each sync.** The Reddit API can't filter these lists by `modified_at`, so each incremental sync requests every record in the ad account and keeps only those modified since the previous sync, or since **Start Date** on the first sync. Sync duration scales with the size of the account, not with the amount of new data.
- **Deletions aren't detected.** The connector doesn't detect or mark deletions. Reddit marks a deleted ad, ad group, or campaign with a `configured_status` or `effective_status` of `DELETED`; if Reddit still lists that item, the connector syncs it with that status. If Reddit stops listing an item, its last-synced row stays in your destination until a **Full Refresh | Overwrite** sync replaces the table.

### Troubleshooting

| Error | Cause and fix |
| --- | --- |
| Refresh token was rejected by the OAuth provider | Reddit's token endpoint rejected the refresh token or the client credentials. If you use **Authenticate with Reddit**, select **Authenticate your Reddit Ads account** again. If you use **Use your own Reddit app**, confirm the OAuth Client ID and Client Secret, then [get a new refresh token](#get-a-refresh-token) with `duration=permanent`. |
| Reddit denied access to ad account (HTTP 403) | The refresh token lacks the `adsread` scope, or the Reddit user who authorized it can't access this ad account. Re-authenticate, or get a new refresh token with the `adsread` scope, while signed in as a user with access to the ad account. |
| Reddit could not find ad account (HTTP 404) or Reddit rejected the ad account ID | The **Ad Account ID** is wrong. [Find your ad account ID](#find-your-ad-account-id), which starts with `a2_`, and update the source. |
| Reddit rejected the request as invalid (HTTP 400) | Reddit rejected the request for a reason unrelated to the ad account. The error message includes the explanation Reddit returned. |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------------- | -------------- | ---------------- |
| 1.0.3 | 2026-10-27 | [90048](https://github.com/airbytehq/airbyte/pull/90048) | Update dependencies |
| 1.0.2 | 2026-10-22 | [89672](https://github.com/airbytehq/airbyte/pull/89672) | Promote to certified |
| 1.0.1 | 2026-10-22 | [89670](https://github.com/airbytehq/airbyte/pull/89670) | Use Reddit's official icon from the Reddit Brand System; document where to find the ad account ID |
| 1.0.0 | 2026-10-20 | [89083](https://github.com/airbytehq/airbyte/pull/89083) | Type timestamp, date and integer fields to match Reddit's API and normalize report `date` to `YYYY-MM-DD` |
| 0.4.1 | 2026-10-20 | [88784](https://github.com/airbytehq/airbyte/pull/88784) | Update dependencies |
| 0.4.0 | 2026-10-16 | [88964](https://github.com/airbytehq/airbyte/pull/88964) | Add ad_account, ad_group, ad_account_report, ad_group_report and ad_report streams; show Reddit's field-level reason in HTTP 400 error messages |
| 0.3.0 | 2026-10-15 | [88963](https://github.com/airbytehq/airbyte/pull/88963) | Fix campaign_report windows that skipped one day in every three and overwrote earlier days with partial data; add a configurable report lookback window |
| 0.2.0 | 2026-10-14 | [88145](https://github.com/airbytehq/airbyte/pull/88145) | Add OAuth (Authenticate with Reddit) for Airbyte Cloud with automatic config migration to a credentials object; make User Agent optional |
| 0.1.1 | 2026-10-06 | [88015](https://github.com/airbytehq/airbyte/pull/88015) | Update dependencies |
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
