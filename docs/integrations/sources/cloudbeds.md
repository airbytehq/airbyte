# Cloudbeds
This is Cloudbeds source that ingests data from the Cloudbeds API.

Cloudbeds is an unified hospitality platform https://cloudbeds.com

In order to use this source, you must first create a cloudbeds account. Once logged in, navigate to the API credentials page for your property by clicking Account > Apps & Marketplace in the upper right corner.  Use the menu on the top to navigate to the API Credentials Page. Click the New Credentials button, fill in the details and click on Create. This will create an application, then click on the API Key and provide all the required scopes as needed. 

You can learn more about the API here https://hotels.cloudbeds.com/api/v1.2/docs/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| guests | guestID | DefaultPaginator | ✅ |  ❌  |
| hotels |  | DefaultPaginator | ✅ |  ❌  |
| rooms | propertyID | DefaultPaginator | ✅ |  ❌  |
| reservations | reservationID | DefaultPaginator | ✅ |  ❌  |
| transactions | transactionID | DefaultPaginator | ✅ |  ❌  |
| packages | itemID | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
