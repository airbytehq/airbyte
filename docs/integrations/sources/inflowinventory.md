# Inflowinventory
As the name suggests , Inflowinventory is an inventory management software.
Using this connector we can extract data from various streams such as customers , productts and sales orders.
Docs : https://cloudapi.inflowinventory.com/docs/index.html#section/Overview

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `companyid` | `string` | CompanyID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| adjustment reasons | adjustmentReasonId | No pagination | ✅ |  ❌  |
| categories | categoryId | No pagination | ✅ |  ❌  |
| currencies | currencyId | No pagination | ✅ |  ❌  |
| customers | customFieldsId | No pagination | ✅ |  ❌  |
| locations | locationId | No pagination | ✅ |  ❌  |
| operation types | operationTypeId | No pagination | ✅ |  ❌  |
| payment terms | paymentTermsId | No pagination | ✅ |  ❌  |
| pricing schemes | pricingSchemeId | No pagination | ✅ |  ❌  |
| products | productId | No pagination | ✅ |  ❌  |
| product cost adjustments | productCostAdjustmentId | No pagination | ✅ |  ❌  |
| purchase orders | purchaseOrderId | No pagination | ✅ |  ❌  |
| sales orders | salesOrderId | No pagination | ✅ |  ❌  |
| stock adjustments | stockAdjustmentId | No pagination | ✅ |  ❌  |
| stock counts | stockCountId | No pagination | ✅ |  ❌  |
| stock transfers | stockTransferId | No pagination | ✅ |  ❌  |
| tax codes | taxCodeId | No pagination | ✅ |  ❌  |
| taxing schemes | taxingSchemeId | No pagination | ✅ |  ❌  |
| team members | teamMemberId | No pagination | ✅ |  ❌  |
| vendors | vendorId | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
