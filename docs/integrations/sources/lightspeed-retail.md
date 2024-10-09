# Lightspeed Retail
Lightspeed Retail is a one-stop commerce platform empowering merchants around the world to simplify, scale and provide exceptional customer experiences. This source connector ingests data from the lightspeed retail API https://www.lightspeedhq.com/

In order to use this source, you must first create an account.
Note down the store url name as this will be needed for your subdomain name in the source. 
After logging in, you can create your personal token by navigating to Setup -&gt; Personal Token. You can learn more about the API here https://x-series-api.lightspeedhq.com/reference/listcustomers



 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `subdomain` | `string` | Subdomain. The subdomain for the retailer, e.g., &#39;example&#39; in &#39;example.retail.lightspeed.app&#39;. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| audit | id | DefaultPaginator | ✅ |  ❌  |
| brands | id | DefaultPaginator | ✅ |  ❌  |
| attributes | id | DefaultPaginator | ✅ |  ❌  |
| tax | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| suppliers | id | DefaultPaginator | ✅ |  ❌  |
| serial_numbers | id | DefaultPaginator | ✅ |  ❌  |
| sales | id | DefaultPaginator | ✅ |  ❌  |
| registers | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| services | id | DefaultPaginator | ✅ |  ❌  |
| promotions | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| product_categories | id | DefaultPaginator | ✅ |  ❌  |
| price_books | id | DefaultPaginator | ✅ |  ❌  |
| payment_types | id | DefaultPaginator | ✅ |  ❌  |
| outlets | id | DefaultPaginator | ✅ |  ❌  |
| outlet_taxes | outlet_id.product_id.tax_id | DefaultPaginator | ✅ |  ❌  |
| inventory | id | DefaultPaginator | ✅ |  ❌  |
| fulfillments | id | DefaultPaginator | ✅ |  ❌  |
| customer_groups | id | DefaultPaginator | ✅ |  ❌  |
| consignments | id | DefaultPaginator | ✅ |  ❌  |
| consignment_products | product_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-09 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
