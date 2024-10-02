# Easypost
This directory contains the manifest-only connector for [`source-easypost`](https://www.easypost.com/).

## Documentation reference:
- Visit [`https://docs.easypost.com/docs/addresses`](https://docs.easypost.com/docs/addresses) for API documentation

## Authentication setup
`EasyPost` uses api key authentication routed as Basic Http, Visit `https://docs.easypost.com/docs/authentication` for getting your api keys.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | API Key. The API Key from your easypost settings |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| batches | id | DefaultPaginator | ✅ |  ✅  |
| addresses | id | DefaultPaginator | ✅ |  ❌  |
| trackers | id | DefaultPaginator | ✅ |  ✅  |
| metadata_carriers | name | No pagination | ✅ |  ❌  |
| end_shippers | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ✅  |
| users_children | id | DefaultPaginator | ✅ |  ✅  |
| carrier_accounts | id | DefaultPaginator | ✅ |  ✅  |
| api_keys | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-01 | [46287](https://github.com/airbytehq/airbyte/pull/46287) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
