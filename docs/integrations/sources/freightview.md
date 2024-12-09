# Freightview
An **Airbyte connector for Freightview** enables seamless data integration by extracting and syncing shipping data from Freightview to your target data warehouses or applications. This connector automates the retrieval of essential shipping details, such as quotes, tracking, and shipment reports, allowing businesses to efficiently analyze and manage logistics operations in a centralized system.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| shipments | shipmentId | DefaultPaginator | ✅ |  ❌  |
| quotes | quoteId | No pagination | ✅ |  ❌  |
| tracking | createdDate | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
