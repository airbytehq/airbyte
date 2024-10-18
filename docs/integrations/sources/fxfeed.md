# FxFeed
FxFeed provides data related to foreign exchange rates of about 161 currencies.
With this connector we have streams which fetch data for latest and historical data. There is a stream for currency conversion aswell.
Currently Time Series stream has not been implemented due to some problem with response/schema

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `base` | `string` | base. The base currency symbol (e.g., USD, EUR) | USD |
| `currencies` | `string` | currencies. A comma-separated list of currency symbols to retrieve rates for(to  limit output currencies) | EUR,JPY,GBP,AUD,CAD,CHF,CNH,HKD,NZD,INR |
| `date` | `string` | date. The date for historical data in ISO format (YYYY-MM-DD) |  |
| `from` | `string` | From. The three-letter currency code to convert from | USD |
| `to` | `string` | To. The three-letter currency code to convert to | EUR |
| `amount` | `string` | Amount. The amount to be converted | 1 |
| `end_data` | `string` | End Data.  The end date of your preferred timeframe (YYYY-MM-DD) |  |
| `startdate` | `string` | Start Date. The start date of your preferred timeframe (YYYY-MM-DD) |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Latest Currency Data |  | No pagination | ✅ |  ✅  |
| Historical Currency Data |  | No pagination | ✅ |  ✅  |
| Currency Conversion |  | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-18 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
