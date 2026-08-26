# MNTN

MNTN is a platform that lets brands of any size create and launch TV commercials on shows, movies, and live sports. This source reads campaign, creative, and advertiser reporting data from the MNTN Reporting API 3.0 (`api3.mountain.com`).

## Prerequisites

- An MNTN account with access to Reporting.
- Your MNTN Reporting API key.

To find the key, sign in to MNTN, open **My Account** from the account dropdown, click **API** in the left navigation, then click **Copy** next to **Reporting API**. See [Access your Reporting API key](https://help.mountain.com/en/articles/6511970-access-your-reporting-api-key) for details. Every user on your MNTN account can read this key, so treat it like a password.

This source uses MNTN API 3.0. If you also query MNTN from a BI tool or script that still points at `api.mountain.com`, note that [API 1.0 stopped returning reporting data on April 1, 2026](https://help.mountain.com/en/articles/9106215-upgrade-to-api-3-0).

## Configuration

| Input | Type | Description | Default Value |
| --- | --- | --- | --- |
| `api_key` | `string` | API Key. | |
| `start_time` | `string` | start_time. | 2023-01-01 |

Set `start_time` to a date in `YYYY-MM-DD` format. It becomes the `begin` date of every reporting query, so it also sets how far back the first sync of the incremental streams reads.

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
| --- | --- | --- | --- | --- |
| CampaignDetails | ID | No pagination | ✅ | ❌ |
| CreativeDetails | ID.Day | No pagination | ✅ | ✅ |
| Campaign | ID.Day | No pagination | ✅ | ✅ |
| Creative | ID.Day | No pagination | ✅ | ✅ |
| Advertiser | ID.Day | No pagination | ✅ | ✅ |

The streams fall into two groups:

- `CampaignDetails` and `CreativeDetails` return configuration data. `CampaignDetails` returns one row per campaign with its name, status, budget, flight dates, and goal. `CreativeDetails` returns one row per creative per day with its name, creative group, active flag, template creative, and click URL.
- `Campaign`, `Creative`, and `Advertiser` return daily performance metrics at the campaign, creative, and account level: impressions, spend, visits, conversions, order value, ROAS, reach, and frequency.

## Sync behavior and limitations

- Performance metrics use First Touch attribution, which is the API 3.0 default. Each performance stream also carries the equivalent Last Touch fields, such as `LastTouchConversions` and `LastTouchROAS`, so you can compare both models.
- Every field, including numeric metrics and dates, arrives as a string. Cast the values you need in your destination or transformation layer.
- The incremental streams use `Day` as the cursor and read one day per request. A first sync that starts several years in the past therefore issues one request per day in that range, which takes a while. Set `start_time` no earlier than you need.
- `CampaignDetails` has no date dimension, so it always reads from `start_time` through the current date and replaces its rows on each sync.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.0.6 | 2026-08-26 | [85027](https://github.com/airbytehq/airbyte/pull/85027) | Enable acceptance test suite with GSM test secrets |
| 0.0.5 | 2026-08-18 | [84647](https://github.com/airbytehq/airbyte/pull/84647) | Update dependencies |
| 0.0.4 | 2026-08-11 | [84027](https://github.com/airbytehq/airbyte/pull/84027) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83541](https://github.com/airbytehq/airbyte/pull/83541) | Update dependencies |
| 0.0.2 | 2026-07-28 | [83005](https://github.com/airbytehq/airbyte/pull/83005) | Update dependencies |
| 0.0.1 | 2026-07-27 | [81334](https://github.com/airbytehq/airbyte/pull/81334) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
