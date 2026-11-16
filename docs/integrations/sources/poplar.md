# Poplar

This page contains the setup guide and reference information for the [Poplar](https://www.heypoplar.com/) source connector. Poplar is a direct mail platform. This connector syncs your campaigns, creatives, audiences, mailings, and account information from the [Poplar API](https://docs.heypoplar.com/api).

## Prerequisites

- A Poplar account
- A Poplar **production** access token

### Get an access token

1. Sign in to Poplar and go to the [API credentials page](https://app.heypoplar.com/credentials).
2. Create or copy a production access token.

Poplar also offers test access tokens, identified by a `test` prefix. According to the [Poplar API documentation](https://docs.heypoplar.com/api/api/master), test tokens only work with the mailings endpoint. This connector reads campaigns before it reads mailings and creatives, and it uses the campaigns endpoint to check the connection, so use a production token.

Treat the access token like a password. If it's compromised, revoke it from the API credentials page.

## Setup guide

1. In Airbyte, create a new source and select **Poplar**.
2. For **Access Token**, enter your Poplar production access token.
3. For **Start date**, enter the earliest mailing creation date to sync, in the format `YYYY-MM-DDTHH:MM:SSZ`. This date only applies to the `mailings` stream.
4. Select **Set up source**.

## Supported sync modes

| Stream | Full Refresh | Incremental |
|--------|--------------|-------------|
| `campaigns` | Yes | No |
| `creatives` | Yes | No |
| `audiences` | Yes | No |
| `mailings` | Yes | Yes |
| `me` | Yes | No |

## Supported streams

| Stream | Endpoint | Primary key | Notes |
|--------|----------|-------------|-------|
| `campaigns` | `GET /v1/campaigns` | `id` | All campaigns in your account. |
| `creatives` | `GET /v1/campaign/{id}/creatives` | None | Creatives for each campaign. This stream has no primary key, so it doesn't support deduplication. |
| `audiences` | `GET /v1/audiences` | `id` | All audiences in your account. |
| `mailings` | `GET /v1/campaign/{id}/mailings` | `id` | Mailings for each campaign, filtered by `created_at` between the start date and the current time. Supports incremental sync using the `created_at` cursor. Fetched 100 records per page. |
| `me` | `GET /v1/me` | `id` | Information about the account that owns the access token. |

The `creatives` and `mailings` streams are child streams of `campaigns`. The connector reads every campaign first, then requests creatives and mailings for each campaign ID.

## Limitations and troubleshooting

- **Permission errors**: If Poplar returns HTTP 403 Forbidden for the `campaigns`, `audiences`, `mailings`, or `me` streams, the connector skips that request instead of failing the sync, so the stream may sync zero records. If a stream is unexpectedly empty, confirm that you're using a production token with access to that data. An HTTP 403 response on the `creatives` stream fails the sync.
- **Rate limits**: When Poplar rate-limits a request, the connector waits until the time in the `ratelimit-reset` response header, falling back to exponential backoff, and retries up to 10 times before failing.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.59 | 2026-11-12 | [90404](https://github.com/airbytehq/airbyte/pull/90404) | Simplify stream error handler configuration (no behavior change) |
| 0.0.58 | 2026-11-10 | [91674](https://github.com/airbytehq/airbyte/pull/91674) | Update dependencies |
| 0.0.57 | 2026-11-03 | [90681](https://github.com/airbytehq/airbyte/pull/90681) | Update dependencies |
| 0.0.56 | 2026-10-27 | [90034](https://github.com/airbytehq/airbyte/pull/90034) | Update dependencies |
| 0.0.55 | 2026-10-20 | [89331](https://github.com/airbytehq/airbyte/pull/89331) | Update dependencies |
| 0.0.54 | 2026-10-13 | [88751](https://github.com/airbytehq/airbyte/pull/88751) | Update dependencies |
| 0.0.53 | 2026-10-07 | [88195](https://github.com/airbytehq/airbyte/pull/88195) | Fix rate-limit (HTTP 429) failures: back off using the `ratelimit-reset` header, raise retries from 1 to 10, and fetch `mailings` 100 per page (API maximum) instead of 5 |
| 0.0.52 | 2026-10-06 | [87994](https://github.com/airbytehq/airbyte/pull/87994) | Update dependencies |
| 0.0.51 | 2026-09-29 | [87305](https://github.com/airbytehq/airbyte/pull/87305) | Update dependencies |
| 0.0.50 | 2026-09-22 | [86744](https://github.com/airbytehq/airbyte/pull/86744) | Update dependencies |
| 0.0.49 | 2026-09-15 | [86162](https://github.com/airbytehq/airbyte/pull/86162) | Update dependencies |
| 0.0.48 | 2026-09-08 | [85621](https://github.com/airbytehq/airbyte/pull/85621) | Update dependencies |
| 0.0.47 | 2026-08-18 | [84076](https://github.com/airbytehq/airbyte/pull/84076) | Update dependencies |
| 0.0.46 | 2026-08-04 | [83581](https://github.com/airbytehq/airbyte/pull/83581) | Update dependencies |
| 0.0.45 | 2026-07-28 | [83054](https://github.com/airbytehq/airbyte/pull/83054) | Update dependencies |
| 0.0.44 | 2026-07-21 | [82542](https://github.com/airbytehq/airbyte/pull/82542) | Update dependencies |
| 0.0.43 | 2026-07-14 | [81957](https://github.com/airbytehq/airbyte/pull/81957) | Update dependencies |
| 0.0.42 | 2026-06-30 | [81205](https://github.com/airbytehq/airbyte/pull/81205) | Update dependencies |
| 0.0.41 | 2026-06-23 | [80573](https://github.com/airbytehq/airbyte/pull/80573) | Update dependencies |
| 0.0.40 | 2026-06-16 | [79978](https://github.com/airbytehq/airbyte/pull/79978) | Update dependencies |
| 0.0.39 | 2026-06-09 | [79453](https://github.com/airbytehq/airbyte/pull/79453) | Update dependencies |
| 0.0.38 | 2026-06-02 | [78882](https://github.com/airbytehq/airbyte/pull/78882) | Update dependencies |
| 0.0.37 | 2026-04-28 | [77393](https://github.com/airbytehq/airbyte/pull/77393) | Update dependencies |
| 0.0.36 | 2026-04-21 | [76694](https://github.com/airbytehq/airbyte/pull/76694) | Update dependencies |
| 0.0.35 | 2026-03-31 | [75869](https://github.com/airbytehq/airbyte/pull/75869) | Update dependencies |
| 0.0.34 | 2026-03-17 | [74932](https://github.com/airbytehq/airbyte/pull/74932) | Update dependencies |
| 0.0.33 | 2026-03-10 | [74643](https://github.com/airbytehq/airbyte/pull/74643) | Update dependencies |
| 0.0.32 | 2026-02-24 | [73844](https://github.com/airbytehq/airbyte/pull/73844) | Update dependencies |
| 0.0.31 | 2026-02-17 | [73517](https://github.com/airbytehq/airbyte/pull/73517) | Update dependencies |
| 0.0.30 | 2026-02-03 | [72666](https://github.com/airbytehq/airbyte/pull/72666) | Update dependencies |
| 0.0.29 | 2026-01-20 | [72180](https://github.com/airbytehq/airbyte/pull/72180) | Update dependencies |
| 0.0.28 | 2026-01-14 | [71561](https://github.com/airbytehq/airbyte/pull/71561) | Update dependencies |
| 0.0.27 | 2025-12-18 | [70529](https://github.com/airbytehq/airbyte/pull/70529) | Update dependencies |
| 0.0.26 | 2025-11-25 | [69951](https://github.com/airbytehq/airbyte/pull/69951) | Update dependencies |
| 0.0.25 | 2025-11-18 | [69632](https://github.com/airbytehq/airbyte/pull/69632) | Update dependencies |
| 0.0.24 | 2025-10-29 | [68947](https://github.com/airbytehq/airbyte/pull/68947) | Update dependencies |
| 0.0.23 | 2025-10-21 | [68224](https://github.com/airbytehq/airbyte/pull/68224) | Update dependencies |
| 0.0.22 | 2025-10-14 | [67820](https://github.com/airbytehq/airbyte/pull/67820) | Update dependencies |
| 0.0.21 | 2025-10-07 | [67492](https://github.com/airbytehq/airbyte/pull/67492) | Update dependencies |
| 0.0.20 | 2025-10-01 | [66968](https://github.com/airbytehq/airbyte/pull/66968) | Update dependencies |
| 0.0.19 | 2025-09-23 | [66422](https://github.com/airbytehq/airbyte/pull/66422) | Update dependencies |
| 0.0.18 | 2025-09-10 | [65794](https://github.com/airbytehq/airbyte/pull/65794) | Update dependencies |
| 0.0.17 | 2025-08-23 | [65229](https://github.com/airbytehq/airbyte/pull/65229) | Update dependencies |
| 0.0.16 | 2025-08-09 | [64762](https://github.com/airbytehq/airbyte/pull/64762) | Update dependencies |
| 0.0.15 | 2025-08-02 | [64201](https://github.com/airbytehq/airbyte/pull/64201) | Update dependencies |
| 0.0.14 | 2025-07-26 | [63921](https://github.com/airbytehq/airbyte/pull/63921) | Update dependencies |
| 0.0.13 | 2025-07-19 | [63406](https://github.com/airbytehq/airbyte/pull/63406) | Update dependencies |
| 0.0.12 | 2025-07-12 | [63233](https://github.com/airbytehq/airbyte/pull/63233) | Update dependencies |
| 0.0.11 | 2025-07-05 | [62593](https://github.com/airbytehq/airbyte/pull/62593) | Update dependencies |
| 0.0.10 | 2025-06-28 | [62400](https://github.com/airbytehq/airbyte/pull/62400) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61899](https://github.com/airbytehq/airbyte/pull/61899) | Update dependencies |
| 0.0.8 | 2025-06-14 | [60546](https://github.com/airbytehq/airbyte/pull/60546) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60110](https://github.com/airbytehq/airbyte/pull/60110) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59522](https://github.com/airbytehq/airbyte/pull/59522) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59048](https://github.com/airbytehq/airbyte/pull/59048) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58469](https://github.com/airbytehq/airbyte/pull/58469) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57910](https://github.com/airbytehq/airbyte/pull/57910) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57291](https://github.com/airbytehq/airbyte/pull/57291) | Update dependencies |
| 0.0.1 | 2025-03-31 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
