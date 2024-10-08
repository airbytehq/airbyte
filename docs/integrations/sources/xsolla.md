# Xsolla
The Xsolla Airbyte Connector enables seamless integration between Xsolla and various data destinations. This connector allows you to extract data from Xsolla’s APIs, such as Game Catalog, Virtual Items, Virtual Currency and more.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to Xsolla Dashboard and from company setting get the api_key |  |
| `project_id` | `number` | Project Id. You can find this parameter in your Publisher Account next to the name of the project . Example: 44056 |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Games Catalog | item_id | DefaultPaginator | ✅ |  ❌  |
| DRM | drm_id | No pagination | ✅ |  ❌  |
| Virtual Items | item_id | DefaultPaginator | ✅ |  ❌  |
| Virtual Currency | item_id | DefaultPaginator | ✅ |  ❌  |
| Virtual Currency Package | item_id | DefaultPaginator | ✅ |  ❌  |
| Bundles | item_id | DefaultPaginator | ✅ |  ❌  |
| Reward Chains | reward_chain_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-01 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>
