# Etherscan
API Documentation: https://docs.etherscan.io/api-endpoints/accounts

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Found at `https://etherscan.io/myapikey` |  |
| `eth_address` | `array` | ETH Address. ETH address |  |
| `transaction_hash` | `array` | Transaction hash. For transactions stream |  |
| `block_list` | `array` | Block number list. Blocks number list |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| stats | uuid | No pagination | ✅ |  ❌  |
| gas_tracker | uuid | No pagination | ✅ |  ❌  |
| eth_blocknumber | uuid | No pagination | ✅ |  ❌  |
| account_balance | uuid | No pagination | ✅ |  ❌  |
| contracts_abi | uuid | No pagination | ✅ |  ❌  |
| transaction_exec_status | uuid | No pagination | ✅ |  ❌  |
| transaction_reciept_status | uuid | No pagination | ✅ |  ❌  |
| block_and_uncle_rewards | uuid | No pagination | ✅ |  ❌  |
| block_countdown_time | uuid | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-22 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
