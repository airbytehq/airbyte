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
| 0.0.10 | 2025-02-08 | [53296](https://github.com/airbytehq/airbyte/pull/53296) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52746](https://github.com/airbytehq/airbyte/pull/52746) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52288](https://github.com/airbytehq/airbyte/pull/52288) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51823](https://github.com/airbytehq/airbyte/pull/51823) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51200](https://github.com/airbytehq/airbyte/pull/51200) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50660](https://github.com/airbytehq/airbyte/pull/50660) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50082](https://github.com/airbytehq/airbyte/pull/50082) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49633](https://github.com/airbytehq/airbyte/pull/49633) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48961](https://github.com/airbytehq/airbyte/pull/48961) | Update dependencies |
| 0.0.1 | 2024-10-29 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
