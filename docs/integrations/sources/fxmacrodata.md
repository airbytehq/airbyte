# FXMacroData

The FXMacroData source replicates macroeconomic announcements, economic release
calendars, indicator catalogues and FX reference rates from the
[FXMacroData API](https://fxmacrodata.com/documentation/reference?utm_source=github&utm_medium=referral&utm_campaign=airbyte&utm_content=docs).
The data covers 22 currencies and is taken from central banks and national
statistics offices.

## Prerequisites

- For USD macro data, nothing. USD announcements, the USD release calendar and
  the USD indicator catalogue can be read without an API key.
- For any other currency, and for the `forex` stream, an FXMacroData API key.
  See [subscription options](https://fxmacrodata.com/subscribe?utm_source=github&utm_medium=referral&utm_campaign=airbyte&utm_content=docs).

## Setup guide

1. Leave **API Key** empty to sync USD data only, or paste your FXMacroData API
   key. The connector sends it in the `X-API-Key` header.
2. Choose the **Currencies** to sync. The default is `USD`.
3. Under **Indicators**, list the indicator slugs to read for each currency,
   such as `policy_rate`, `inflation`, `unemployment` or `gdp`. Sync the
   `data_catalogue` stream first if you need the full list of slugs for a
   currency.
4. Optionally set a **Start Date** for the `announcements` and `forex` streams.
5. To use the `forex` stream, list **FX Pairs** as `BASE/QUOTE`, for example
   `EUR/USD`.

## Configuration

| Input | Required | Description |
| --- | --- | --- |
| `api_key` | No | FXMacroData API key. Without it, only USD macro data is available. |
| `currencies` | No | Currencies to read announcements, calendar and catalogue rows for. Defaults to `["USD"]`. |
| `indicators` | No | Indicator slugs to read for each currency. Defaults to `["policy_rate", "inflation"]`. Combinations that a currency doesn't publish are skipped with a log message. |
| `start_date` | No | Earliest observation date for `announcements` and `forex`, in `YYYY-MM-DD` format. Leave empty to read the full history your key allows. |
| `forex_pairs` | No | Currency pairs for the `forex` stream, as `BASE/QUOTE`. Requires an API key. Defaults to none. |

## Streams

| Stream | Sync mode | Primary key | Description |
| --- | --- | --- | --- |
| `announcements` | Full refresh, Incremental | `currency`, `indicator`, `date` | Indicator observations from `/v1/announcements/{currency}/{indicator}`, one partition per configured currency and indicator. Cursor: `date`. |
| `calendar` | Full refresh | `currency`, `release`, `announcement_datetime` | Scheduled release dates from `/v1/calendar/{currency}`. |
| `data_catalogue` | Full refresh | `currency`, `indicator` | The indicators available for each currency, with units, frequency, source and coverage, from `/v1/data_catalogue/{currency}`. |
| `forex` | Full refresh, Incremental | `base`, `quote`, `date` | Daily FX reference rates from `/v1/forex/{base}/{quote}` for each configured pair. Cursor: `date`. |

`announcements` and `forex` page through results 100 rows at a time, following
`pagination.next_offset` until `pagination.has_more` is false.

## Limitations and data availability

- Without an API key, USD announcements are limited to the most recent 90 days
  and are delayed by 15 minutes after release. Keyless access is also limited
  to roughly 100 requests per day, and each currency and indicator pair is at
  least one request.
- Non-USD currencies and the `forex` stream return `401` without a key. The
  connector reports this as a configuration error.
- `val` is null on some rows, for example when a source publishes a period
  without a value. The connector passes null through rather than replacing it.
- The incremental cursor is the observation `date`. Revisions to periods before
  the saved cursor are not picked up by incremental syncs; run a full refresh
  to reload revised history.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.0.1 | 2026-10-01 | [87603](https://github.com/airbytehq/airbyte/pull/87603) | Initial release |

</details>
