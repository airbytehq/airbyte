# Shippo
This is the Shippo source for ingesting data using the Shippo API.

Shippo is your one-stop solution for shipping labels. Whether you use our app to ship or API to power your logistics workflow, Shippo gives you scalable shipping tools, the best rates, and world-class support https://goshippo.com/

In order to use this source, you must first create a Shippo account. Once logged in, head over to Settings -&gt; Advanced -&gt; API and click on generate new token. You can learn more about the API here https://docs.goshippo.com/shippoapi/public-api/#tag/Overview 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `shippo_token` | `string` | Shippo Token. The bearer token used for making requests |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| addresses | id | DefaultPaginator | ✅ |  ❌  |
| parcels | object_id | DefaultPaginator | ✅ |  ❌  |
| custom_items | object_id | DefaultPaginator | ✅ |  ❌  |
| accounts | object_id | DefaultPaginator | ✅ |  ❌  |
| carrier_acounts | object_id | DefaultPaginator | ✅ |  ❌  |
| shipments | object_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-28 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
