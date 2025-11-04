# Keepa_API (Product Data)
Retrieves detailed Amazon product metadata and time-series history directly from the Keepa API.
Supports querying by ASIN and exposes parameters such as offers, pricing, stock, reviews, buybox, A+ content, and more.
Ideal for e-commerce analytics, competitive research, and price tracking pipelines.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key. Keepa API credential sent as key query param. Example: k3ePa_ABCDEFG123456 |  |
| `asins` | `array` | Amazon Product ASIN&#39;s. List of ASINs; connector calls Keepa once per ASIN. Example: [&quot;B0088PUEPK&quot;,&quot;B0F6XSV7XB&quot;] |  |
| `domain_id` | `integer` | Domain ID. Amazon locale code (1=com, 2=co.uk, 3=de, 4=fr, 5=co.jp, 6=ca, 8=it, 9=es, 10=in, 11=com.mx) Example: 1 | 1 |
| `days` | `integer` | Days window. History length to return; 0 = all time, small values for daily runs. 1 day, 2 days, 3 days... Example: 2 | 2 |
| `stats_days` | `integer` | Stats days. Window (days) for the stats block Keepa returns. Example: 180 | 180 |
| `history` | `integer` | Include history. 1 to include CSV price/rank histories; 0 to omit. Example: 1 | 1 |
| `historical_variations` | `integer` | Include historical variations. 1 maps to Keepa param historical-variations=1; 0 to omit. Example: 1 | 1 |
| `offers` | `integer` | Include offers. ≥20 enables offer-dependent channels; 0 disables. Offer dependent channels: rating, buybox, stock, aplus, videos, and rental. Example: 20 | 20 |
| `rating` | `integer` | Include rating/reviews. 1 to include the reviews object; 0 to omit. CSV rating channels require offers &gt; 0. Example: 1  | 1 |
| `buybox` | `integer` | Include buy box histories. 1 to include buy box time series; 0 to omit. Requires to be offers &gt; 0 for use. Example: 1 | 1 |
| `stock` | `integer` | Include stock signals. 1 to include stock-related channels; 0 to omit. Requires to be offers &gt; 0 for use. Example: 1 | 1 |
| `aplus` | `integer` | Include A+ content. 1 to return A+ content metadata; 0 to omit. Requires to be offers &gt; 0 for use. Example: 1 | 1 |
| `videos` | `integer` | Include videos metadata. 1 to include product video metadata; 0 to omit. Requires to be offers &gt; 0 for use. Example: 1 | 1 |
| `rental` | `integer` | Include rental fields. 1 to include rental data (rare); 0 to omit. Requires to be offers &gt; 0 for use. Example: 0 | 1 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Keepa Product (Raw) | asin | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-04 | | Initial release by [@Christian-Suarez-che](https://github.com/Christian-Suarez-che) via Connector Builder |

</details>
