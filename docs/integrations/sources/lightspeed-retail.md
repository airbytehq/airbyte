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
| users | id | CursorPagination | ✅ |  ❌  |
| customers | id | CursorPagination | ✅ |  ❌  |
| audit | id | CursorPagination | ✅ |  ❌  |
| brands | id | CursorPagination | ✅ |  ❌  |
| attributes | id | CursorPagination | ✅ |  ❌  |
| tax | id | CursorPagination | ✅ |  ❌  |
| tags | id | CursorPagination | ✅ |  ❌  |
| suppliers | id | CursorPagination | ✅ |  ❌  |
| serial_numbers | id | CursorPagination | ✅ |  ❌  |
| sales | id | CursorPagination | ✅ |  ❌  |
| registers | id | CursorPagination | ✅ |  ❌  |
| quotes | id | CursorPagination | ✅ |  ❌  |
| services | id | CursorPagination | ✅ |  ❌  |
| promotions | id | CursorPagination | ✅ |  ❌  |
| products | id | CursorPagination | ✅ |  ❌  |
| product_categories | id | CursorPagination | ✅ |  ❌  |
| price_books | id | CursorPagination | ✅ |  ❌  |
| payment_types | id | CursorPagination | ✅ |  ❌  |
| outlets | id | CursorPagination | ✅ |  ❌  |
| inventory | id | CursorPagination | ✅ |  ❌  |
| fulfillments | id | CursorPagination | ✅ |  ❌  |
| customer_groups | id | CursorPagination | ✅ |  ❌  |
| consignments | id | CursorPagination | ✅ |  ❌  |
| consignment_products | product_id | CursorPagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-23 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
