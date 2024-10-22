# referralhero
[Referral Hero](https://referralhero.com) is a tool for creating, managing, and analyzing referral programs to boost customer acquisition and engagement.
With this connector, you can streamline the transfer of campaign-related data for better integration into your analytics, CRM, or marketing platforms.

Referral Hero Source Connector is a designed to sync referral data between your Referral Hero campaigns and your destination airbyte connectors.


## Generate API Token
Please follow the instructions in the following [referralhero](https://support.referralhero.com/integrate/rest-api) page to generate the api token


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | uuid | DefaultPaginator | ✅ |  ❌  |
| leaderboard |  | DefaultPaginator | ✅ |  ❌  |
| bonuses |  | DefaultPaginator | ✅ |  ❌  |
| subscribers | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-07 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
