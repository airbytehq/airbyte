# Adanos

The Adanos source syncs stock and crypto market sentiment from
[Adanos](https://adanos.org/) into your data warehouse. Stock connections support Reddit,
X / FinTwit, financial news, and Polymarket. Crypto connections use Reddit.

## Configuration

| Input          | Type     | Description                                                               | Default value |
| :------------- | :------- | :------------------------------------------------------------------------ | :------------ |
| `api_key`      | `string` | Adanos API key from [adanos.org/register](https://adanos.org/register).   |               |
| `asset_type`   | `string` | Asset class to sync: `stock` or `crypto`.                                 | `stock`       |
| `stock_source` | `string` | Stock source: `reddit`, `x`, `news`, or `polymarket`. Ignored for crypto. | `reddit`      |
| `symbols`      | `array`  | Stock tickers or crypto symbols to sync.                                  |               |
| `start_date`   | `string` | Inclusive UTC start date in `YYYY-MM-DD` format.                          |               |

## Streams

| Stream name        | Primary key    | Pagination            | Full refresh | Incremental |
| :----------------- | :------------- | :-------------------- | :----------- | :---------- |
| `asset_sentiment`  | `asset_symbol` | Per configured symbol | Yes          | No          |
| `asset_mentions`   |                | Offset pagination     | Yes          | No          |
| `trending_assets`  |                | Top 100 assets        | Yes          | No          |
| `market_sentiment` |                | No pagination         | Yes          | No          |

Every emitted record includes `asset_type`, `source`, `period_from`, and `period_to`. Symbol-specific
records also include `asset_symbol`, so records remain attributable when a connection syncs multiple
assets.

## Plan and rate-limit considerations

Adanos applies the limits associated with each user's API key. Free accounts include 250 monthly
requests and up to 30 days of historical lookback. Hobby accounts include 250,000 monthly requests
and up to 90 days. Professional accounts include 2,500,000 monthly requests and up to 365 days.

Each sync makes one sentiment request per configured symbol, one or more paginated mention requests
per symbol, and one request for each aggregate stream. Keep the symbol list and sync frequency within
the quota of your Adanos plan. The connector runs requests serially and caps calls below the API's
lowest per-minute burst limit.

## Getting started

1. Create an API key at [adanos.org/register](https://adanos.org/register).
2. Choose `stock` or `crypto` as the asset type.
3. For stocks, select Reddit, X / FinTwit, News, or Polymarket.
4. Enter at least one asset symbol and a start date within your plan's historical lookback.
5. Test and save the source.

See the [Adanos API documentation](https://api.adanos.org/docs) for endpoint and response details.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the
[Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to
your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull request | Subject                                                                           |
| :------ | :--------- | :----------- | :-------------------------------------------------------------------------------- |
| 0.0.1   | 2026-07-22 |              | Initial release by [@alexander-schneider](https://github.com/alexander-schneider) |

</details>
