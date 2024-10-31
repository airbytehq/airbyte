# Sendowl
Sendowl is an All-in-One Digital Commerce Platform.
Using this connector we can extract data from products , packages , orders , discounts and subscriptions streams.
Docs : https://dashboard.sendowl.com/developers/api/introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products |  | No pagination | ✅ |  ❌  |
| packages | id | No pagination | ✅ |  ❌  |
| orders | id | No pagination | ✅ |  ❌  |
| discounts | id | No pagination | ✅ |  ❌  |
| subscriptions |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
