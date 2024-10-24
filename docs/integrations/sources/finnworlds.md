# Finnworlds
Finnworlds provides data related to finance for globally traded instruments.
With this connector we can easily fetch data from various streams such as Dividends , Stock Splits , Candle Sticks etc
Docs : https://finnworlds.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `list` | `string` | List. Choose isin, ticker, reg_lei or cik | ticker |
| `list_countries_for_bonds` | `string` | List Countries for Bonds.  | country |
| `key` | `string` | API Key.  |  |
| `from` | `string` | From. The date you need candle sticks from  | 2024-09-24 |
| `type_of_bond_` | `string` | Type of bond . For example 10y | 10y |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Bonds List | country | No pagination | ✅ |  ❌  |
| Bonds |  | No pagination | ✅ |  ❌  |
| Dividends List | ticker | No pagination | ✅ |  ❌  |
| Dividends |  | No pagination | ✅ |  ❌  |
| Stock Splits List | ticker | DefaultPaginator | ✅ |  ❌  |
| Stock Splits |  | No pagination | ✅ |  ❌  |
| CandleStick List | ticker | DefaultPaginator | ✅ |  ❌  |
| Historical CandleStick |  | No pagination | ✅ |  ❌  |
| Macro List | country | DefaultPaginator | ✅ |  ❌  |
| Macro Calendar |  | No pagination | ✅ |  ❌  |
| Macro Indicator |  | No pagination | ✅ |  ❌  |
| Commodities List | name | DefaultPaginator | ✅ |  ❌  |
| Commodities | commodity_name | No pagination | ✅ |  ❌  |
| Benchmark List | benchmark | DefaultPaginator | ✅ |  ❌  |
| Benchmark |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-24 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
