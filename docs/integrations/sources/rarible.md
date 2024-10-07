# Rarible
This connector integrates Rarible&#39;s API with Airbyte, enabling seamless data synchronization of NFT activities, collections, and ownership across multiple blockchains. It supports fetching  ownership, orders and other essential details to facilitate real-time updates and analytics for NFT marketplaces.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `collection_id` | `string` | Collection Id.  |  |
| `blockchain` | `string` | Blockchain.  |  |
| `owner` | `string` | Owner.  |  |
| `maker` | `string` | Maker. ETHEREUM OR POLYGON or leave empty to get orders from all blockchains |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| nfts | id | No pagination | ✅ |  ❌  |
| collections | id | No pagination | ✅ |  ❌  |
| statistics |  | No pagination | ✅ |  ❌  |
| orders |  | No pagination | ✅ |  ❌  |
| activities |  | No pagination | ✅ |  ❌  |
| user_owned_nfts |  | No pagination | ✅ |  ❌  |
| users_bid_orders | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-07 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
