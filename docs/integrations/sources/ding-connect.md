# Ding Connect
Website: https://www.dingconnect.com/
API Reference: https://www.dingconnect.com/Api/Description

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the DingConnect API. You can generate this key by navigating to the Developer tab in the Account Settings section of your DingConnect account. |  |
| `X-Correlation-Id` | `string` | X-Correlation-Id. Optional header to correlate HTTP requests between a client and server. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name                 | Primary Key | Pagination        | Supports Full Sync | Supports Incremental |
|-----------------------------|-------------|-------------------|---------------------|----------------------|
| getcountries                | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| getcurrencies               | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| geterrorcodedescriptions    | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| getproductdescriptions      | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| getproducts                 | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| getpromotions               | uuid        | DefaultPaginator  | ✅                  | ✅                  |
| getproviders                | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| getregions                  | uuid        | DefaultPaginator  | ✅                  | ❌                  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-03 | [56995](https://github.com/airbytehq/airbyte/pull/56995) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
