# Financial Modelling
FMP provides financial data.
Using this connector we can extract data from various endpoints like Stocks list, ETFs list , Exchange Symbols and Historical MarketCap etc
Docs : https://site.financialmodelingprep.com/developer/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `exchange` | `string` | Exchange. The stock exchange : AMEX, AMS, AQS, ASX, ATH, BER, BME, BRU, BSE, BUD, BUE, BVC, CAI, CBOE, CNQ, CPH, DFM, DOH, DUS, DXE, EGX, EURONEXT, HAM, HEL, HKSE, ICE, IOB, IST, JKT, JNB, JPX, KLS, KOE, KSC, KUW, LSE, MCX, MEX, MIL, MUN, NASDAQ, NEO, NSE, NYSE, NZE, OEM, OQX, OSL, OTC, PNK, PRA, RIS, SAO, SAU, SES, SET, SGO, SHH, SHZ, SIX, STO, STU, TAI, TLV, TSX, TSXV, TWO, VIE, VSE, WSE, XETRA | NASDAQ |
| `marketcapmorethan` | `string` | marketCapMoreThan. Used in screener to filter out stocks with a market cap more than the give marketcap |  |
| `marketcaplowerthan` | `string` | marketCapLowerThan. Used in screener to filter out stocks with a market cap lower than the give marketcap |  |
| `start_date` | `string` | Start Date |  |
| `time_frame` | `string` | Time Frame. For example 1min, 5min, 15min, 30min, 1hour, 4hour | 1hour |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Stocks List |  | No pagination | ✅ |  ❌  |
| ETFs List |  | No pagination | ✅ |  ❌  |
| Tradable Search  |  | No pagination | ✅ |  ❌  |
| CIK List |  | No pagination | ✅ |  ❌  |
| Euronext Symbols |  | No pagination | ✅ |  ❌  |
| Exchange Symbols |  | No pagination | ✅ |  ❌  |
| Available Indexes |  | No pagination | ✅ |  ❌  |
| Company Profile |  | No pagination | ✅ |  ❌  |
| Screener (Stock) |  | No pagination | ✅ |  ❌  |
| Historical Market Cap |  | No pagination | ✅ |  ✅  |
| Delisted Companies |  | No pagination | ✅ |  ❌  |
| Exchange Prices |  | No pagination | ✅ |  ❌  |
| All RealTime Full Stock Prices |  | No pagination | ✅ |  ❌  |
| ALL FX Prices |  | No pagination | ✅ |  ❌  |
| Stock Historical Price |  | No pagination | ✅ |  ✅  |
| Forex List |  | No pagination | ✅ |  ❌  |
| Cryptocurrencies List |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2024-12-14 | [49516](https://github.com/airbytehq/airbyte/pull/49516) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49157](https://github.com/airbytehq/airbyte/pull/49157) | Update dependencies |
| 0.0.2 | 2024-11-04 | [48299](https://github.com/airbytehq/airbyte/pull/48299) | Update dependencies |
| 0.0.1 | 2024-10-22 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
