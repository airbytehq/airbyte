# Yuki
Yuki is a Belgian/Dutch accounting software. This connector enables syncing of general ledger transactions.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `API_KEY` | `string` | API Key.  |  |
| `ADMINISTRATION_ID` | `string` | Administration ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Transactions | id | ❌ | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-25 | | Initial release by [@tom-dk](https://github.com/tom-dk) via Connector Builder |

</details>