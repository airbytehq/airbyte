# SoChain
Sync address balances, address summaries, address transaction history and network state for Bitcoin, Litecoin, Dogecoin and Zcash, and their testnets, from the [SoChain API](https://sochain.com/docs).

## Prerequisites

None. SoChain works without an API key, up to 2,500 requests a day per IP. For more, create a free key at [sochain.com/dashboard](https://sochain.com/dashboard) (75,000 requests a month) or see [paid plans](https://sochain.com/pricing).

Each sync makes one request per address for `address_balances` and `address_summaries`, one request per 100 transactions per address for `address_transactions`, and one request for `network_info`.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `network` | `string` | Network. The network the addresses are on: BTC, LTC, DOGE, ZEC, BTCTEST (Bitcoin testnet4), LTCTEST, DOGETEST or ZECTEST. | BTC |
| `addresses` | `array` | Addresses. Addresses on that network to sync, written in full. |  |
| `api_key` | `string` | API Key. Optional. Without a key SoChain allows 2,500 requests a day per IP. A free key from https://sochain.com/dashboard gives 75,000 a month; paid plans give more. |  |
| `start_date` | `string` | Start Date. Optional. UTC date to sync address transactions from, in YYYY-MM-DD format. Leave empty to sync each address's full history. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| address_balances | network.address | No pagination | ✅ |  ❌  |
| address_summaries | network.address | No pagination | ✅ |  ❌  |
| address_transactions | network.address.hash | DefaultPaginator | ✅ |  ✅  |
| network_info | network | No pagination | ✅ |  ❌  |

Amounts are decimal strings in coins (for example `"0.00012345"`), so no precision is lost. `address_transactions` syncs confirmed transactions only; incremental syncs use the transaction `time` and look back 3 hours to pick up late blocks.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-24 | | Initial release |

</details>
