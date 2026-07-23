# AppsFlyer

The Airbyte Source for [AppsFlyer](https://www.appsflyer.com/) lets you extract raw and aggregate attribution data from AppsFlyer's Pull API into your destination of choice.

## Prerequisites

- An AppsFlyer account with access to the app you want to sync.
- An AppsFlyer **API token (V2.0)**. Only an account admin can create or view this token, and it is tied to that admin. If the account admin changes, AppsFlyer issues a new token and you must update the connector's configuration with it.
- The **app ID** of the app you want to sync, as it appears in AppsFlyer. This is the platform-specific store identifier: the package name for Android apps (for example, `com.example.app`) and the App Store ID prefixed with `id` for iOS apps (for example, `id123456789`).

## Setup guide

### Step 1: Get your AppsFlyer API token

1. Sign in to AppsFlyer as an account admin.
2. Generate or copy your **API token (V2.0)**. See [AppsFlyer's documentation on API tokens](https://support.appsflyer.com/hc/en-us/articles/360004562377) for the current location in the dashboard.

The connector authenticates to AppsFlyer's Pull API using this token as a bearer token, so no other credentials are required.

### Step 2: Set up the source in Airbyte

Provide the following configuration:

| Field | Required | Description |
| :--- | :--- | :--- |
| `app_id` | Yes | The app identifier as it appears in AppsFlyer (Android package name or iOS `id`-prefixed App Store ID). |
| `api_token` | Yes | Your AppsFlyer API token (V2.0). |
| `start_date` | Yes | The date to start syncing from when no previous state exists. Accepts `YYYY-MM-DD` or `YYYY-MM-DD HH:mm:ss`. Raw data reports are limited to the most recent 90 days; if the start date is more than 90 days in the past, the connector automatically uses a date 90 days ago. |
| `timezone` | No | The time zone in which your app's data is stored, found in the app settings in the AppsFlyer console. Defaults to `UTC`. Provide a valid [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) name such as `US/Pacific`. |

## Supported sync modes

The AppsFlyer source supports both **Full Refresh** and **Incremental** syncs for all streams. Incremental syncs use each stream's timestamp field (`install_time`, `event_time`, or `date`) as the cursor.

## Supported streams

### Raw data reports

| Stream | Category | Cursor |
| :--- | :--- | :--- |
| `installs` | Non-organic | `install_time` |
| `in_app_events` | Non-organic | `event_time` |
| `uninstall_events` | Non-organic | `event_time` |
| `organic_installs` | Organic | `install_time` |
| `organic_in_app_events` | Organic | `event_time` |
| `organic_uninstall_events` | Organic | `event_time` |
| `retargeting_installs` | Retargeting | `install_time` |
| `retargeting_in_app_events` | Retargeting | `event_time` |

### Aggregate reports

| Stream | Category | Cursor |
| :--- | :--- | :--- |
| `daily_report` | User acquisition | `date` |
| `partners_report` | User acquisition | `date` |
| `partners_events_report` | User acquisition | `date` |
| `geo_report` | User acquisition | `date` |
| `geo_events_report` | User acquisition | `date` |
| `retargeting_daily_report` | Retargeting | `date` |
| `retargeting_partners_report` | Retargeting | `date` |
| `retargeting_partners_events_report` | Retargeting | `date` |
| `retargeting_geo_report` | Retargeting | `date` |
| `retargeting_geo_events_report` | Retargeting | `date` |

### Unsupported reports

The following AppsFlyer report types are not currently synced by this connector:

- Reinstall raw data reports
- Ad revenue raw data
- Postbacks
- Protect360 fraud

## Performance considerations

- **90-day raw data window**: AppsFlyer only serves raw data reports for the most recent 90 days. The connector caps the effective start date at 90 days ago, so historical raw data older than 90 days cannot be retrieved.
- **Rate limits and quotas**: AppsFlyer enforces daily quotas on the Pull API. When the raw data quota is exhausted, the connector waits until quota resets at midnight (UTC) before retrying. When an aggregate report limit is reached, the connector waits and retries. The connector also honors the `Retry-After` header and retries on HTTP 429 and 5xx responses.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                                     |
| :------ | :--------- | :----------------------------------------------------- | :------------------------------------------ |
| 0.3.1 | 2026-07-23 | [82242](https://github.com/airbytehq/airbyte/pull/82242) | Bump base image to python-connector-base 4.1.1 (Python 3.13.14) |
| 0.3.0 | 2026-04-27 | [77123](https://github.com/airbytehq/airbyte/pull/77123) | Migrate to airbyte-cdk 7.x and update base image |
| 0.2.40 | 2025-05-17 | [60656](https://github.com/airbytehq/airbyte/pull/60656) | Update dependencies |
| 0.2.39 | 2025-05-10 | [59774](https://github.com/airbytehq/airbyte/pull/59774) | Update dependencies |
| 0.2.38 | 2025-05-03 | [59359](https://github.com/airbytehq/airbyte/pull/59359) | Update dependencies |
| 0.2.37 | 2025-04-26 | [58748](https://github.com/airbytehq/airbyte/pull/58748) | Update dependencies |
| 0.2.36 | 2025-04-19 | [58244](https://github.com/airbytehq/airbyte/pull/58244) | Update dependencies |
| 0.2.35 | 2025-04-12 | [57618](https://github.com/airbytehq/airbyte/pull/57618) | Update dependencies |
| 0.2.34 | 2025-04-05 | [57111](https://github.com/airbytehq/airbyte/pull/57111) | Update dependencies |
| 0.2.33 | 2025-03-29 | [56605](https://github.com/airbytehq/airbyte/pull/56605) | Update dependencies |
| 0.2.32 | 2025-03-22 | [56154](https://github.com/airbytehq/airbyte/pull/56154) | Update dependencies |
| 0.2.31 | 2025-03-08 | [55380](https://github.com/airbytehq/airbyte/pull/55380) | Update dependencies |
| 0.2.30 | 2025-03-01 | [54869](https://github.com/airbytehq/airbyte/pull/54869) | Update dependencies |
| 0.2.29 | 2025-02-22 | [54228](https://github.com/airbytehq/airbyte/pull/54228) | Update dependencies |
| 0.2.28 | 2025-02-15 | [53895](https://github.com/airbytehq/airbyte/pull/53895) | Update dependencies |
| 0.2.27 | 2025-02-01 | [52901](https://github.com/airbytehq/airbyte/pull/52901) | Update dependencies |
| 0.2.26 | 2025-01-25 | [51286](https://github.com/airbytehq/airbyte/pull/51286) | Update dependencies |
| 0.2.25 | 2024-12-28 | [50438](https://github.com/airbytehq/airbyte/pull/50438) | Update dependencies |
| 0.2.24 | 2024-12-21 | [50173](https://github.com/airbytehq/airbyte/pull/50173) | Update dependencies |
| 0.2.23 | 2024-12-14 | [49296](https://github.com/airbytehq/airbyte/pull/49296) | Update dependencies |
| 0.2.22 | 2024-11-25 | [48652](https://github.com/airbytehq/airbyte/pull/48652) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.21 | 2024-10-29 | [47039](https://github.com/airbytehq/airbyte/pull/47039) | Update dependencies |
| 0.2.20 | 2024-10-12 | [46823](https://github.com/airbytehq/airbyte/pull/46823) | Update dependencies |
| 0.2.19 | 2024-10-05 | [46393](https://github.com/airbytehq/airbyte/pull/46393) | Update dependencies |
| 0.2.18 | 2024-09-28 | [46202](https://github.com/airbytehq/airbyte/pull/46202) | Update dependencies |
| 0.2.17 | 2024-09-21 | [45746](https://github.com/airbytehq/airbyte/pull/45746) | Update dependencies |
| 0.2.16 | 2024-09-14 | [45510](https://github.com/airbytehq/airbyte/pull/45510) | Update dependencies |
| 0.2.15 | 2024-09-07 | [45234](https://github.com/airbytehq/airbyte/pull/45234) | Update dependencies |
| 0.2.14 | 2024-08-31 | [44956](https://github.com/airbytehq/airbyte/pull/44956) | Update dependencies |
| 0.2.13 | 2024-08-24 | [44633](https://github.com/airbytehq/airbyte/pull/44633) | Update dependencies |
| 0.2.12 | 2024-08-17 | [44226](https://github.com/airbytehq/airbyte/pull/44226) | Update dependencies |
| 0.2.11 | 2024-08-10 | [43572](https://github.com/airbytehq/airbyte/pull/43572) | Update dependencies |
| 0.2.10 | 2024-08-03 | [43229](https://github.com/airbytehq/airbyte/pull/43229) | Update dependencies |
| 0.2.9 | 2024-07-27 | [42681](https://github.com/airbytehq/airbyte/pull/42681) | Update dependencies |
| 0.2.8 | 2024-07-20 | [42322](https://github.com/airbytehq/airbyte/pull/42322) | Update dependencies |
| 0.2.7 | 2024-07-13 | [41831](https://github.com/airbytehq/airbyte/pull/41831) | Update dependencies |
| 0.2.6 | 2024-07-10 | [41600](https://github.com/airbytehq/airbyte/pull/41600) | Update dependencies |
| 0.2.5 | 2024-07-09 | [41146](https://github.com/airbytehq/airbyte/pull/41146) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40766](https://github.com/airbytehq/airbyte/pull/40766) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40476](https://github.com/airbytehq/airbyte/pull/40476) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40059](https://github.com/airbytehq/airbyte/pull/40059) | Update dependencies |
| 0.2.1 | 2024-06-11 | [39407](https://github.com/airbytehq/airbyte/pull/39407) | Fix Organic In-App Events Stream |
| 0.2.0 | 2024-05-19 | [38339](https://github.com/airbytehq/airbyte/pull/38339) | Migrate to [AppsFlyer API V2](https://support.appsflyer.com/hc/en-us/articles/12399683708305-Bulletin-API-token-changes?query=token) |
| 0.1.2 | 2024-06-06 | [39187](https://github.com/airbytehq/airbyte/pull/39187) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38436](https://github.com/airbytehq/airbyte/pull/38436) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2021-03-22 | [2544](https://github.com/airbytehq/airbyte/pull/2544) | Adding the appsflyer singer based connector |

</details>
