# ECB Exchange Rates
- Low-code declarative source that hits https://api.frankfurter.app/{date} to fetch daily ECB
    reference rates directly from the Frankfurter API; no auth required.
  - Accepts start_date (required), optional end_date, base_currency, amount, and an optional list of
    target_currencies; when targets are omitted, the API returns the full rate map for every supported
    currency.
  - Uses a DatetimeStreamSlicer/DatetimeBasedCursor on the date field so incremental syncs request one
    business day at a time and resume automatically.
  - Response schema includes amount, base, date, optional start_date/end_date, and the raw rates object
    (currency→value). Downstream models can explode rates with SQL/ELT if per-currency rows are needed.
  - Designed for stable weekday updates (ECB publishes around 16:00 CET) and lightweight retries via
    DefaultErrorHandler.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start Date. Earliest date (YYYY-MM-DD) to begin pulling ECB exchange rates. |  |
| `end_date` | `string` | End Date. Optional end date; defaults to the current UTC date if not set. |  |
| `base_currency` | `string` | Base Currency. ISO 4217 currency code that serves as the conversion base (defaults to EUR/ECB reference). | EUR |
| `target_currencies` | `array` | Target Currencies. Optional list of ISO 4217 currency codes to limit the response; leave empty to fetch all available currencies. |  |
| `amount` | `number` | Amount. Optional multiplier applied to the conversion result (Frankfurter `amount` parameter). | 1 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ECB Exchange Rates | date | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-06 | | Initial release by [@martin-knap](https://github.com/martin-knap) via Connector Builder |

</details>
