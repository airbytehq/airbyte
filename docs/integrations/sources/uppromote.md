# UpPromote
The Uppromote Connector for Airbyte enables seamless data integration between Uppromote, an affiliate and influencer marketing platform, and your data warehouses or analytics tools.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. For developing your own custom integration with UpPromote, you can create an API key. This is available from Professional plan.  Simply go to Settings > Integration > API > Create API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| affiliates | id | DefaultPaginator | ✅ |  ❌  |
| coupons | id | DefaultPaginator | ✅ |  ❌  |
| referrals | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-10-28 | [47589](https://github.com/airbytehq/airbyte/pull/47589) | Update dependencies |
| 0.0.1 | 2024-10-10 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>
