# Track PMS
An Airbyte source for the Track Property Management System (PMS)
Enterprise-class property management solutions for vacation rental companies

Website: https://tnsinc.com/
API Docs: hhttps://developer.trackhs.com
Authentication Docs: https://developer.trackhs.com/docs/authentication#authentication

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `customer_domain` | `string` | Customer Domain.  |  |
| `api_key` | `string` | API Key.  |  |
| `api_secret` | `string` | API Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| units | id | DefaultPaginator | ✅ |  ✅  |
| owners | id | DefaultPaginator | ✅ |  ✅  |
| fractionals | id | DefaultPaginator | ✅ |  ❌  |
| unit-blocks | id | DefaultPaginator | ✅ |  ❌  |
| folios | id | DefaultPaginator | ✅ |  ❌  |
| nodes | id | DefaultPaginator | ✅ |  ❌  |
| units-amenities | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| reservations_v2 | id | DefaultPaginator | ✅ |  ✅  |
| reservation-types | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| unit-types | id | DefaultPaginator | ✅ |  ❌  |
| lodging-types | id | DefaultPaginator | ✅ |  ❌  |
| tax-districts | id | DefaultPaginator | ✅ |  ❌  |
| tax-policies | id | DefaultPaginator | ✅ |  ❌  |
| taxes | id | DefaultPaginator | ✅ |  ❌  |
| travel-insurance-products | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ✅  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| fractional_inventory | fraction_id.id | DefaultPaginator | ✅ |  ❌  |
| fractional_owners | fraction_id.id | DefaultPaginator | ✅ |  ❌  |
| unit_type_daily_pricing_v2 | unit_type_id.rateTypeId | DefaultPaginator | ✅ |  ❌  |
| unit_daily_pricing_v2 | unit_id.rateTypeId | DefaultPaginator | ✅ |  ❌  |
| unit_taxes | unit_id.id | DefaultPaginator | ✅ |  ❌  |
| accounting-items | id | DefaultPaginator | ✅ |  ❌  |
| accounting-accounts | id | DefaultPaginator | ✅ |  ❌  |
| accounting-transactions | id | DefaultPaginator | ✅ |  ❌  |
| accounting-bills | id | DefaultPaginator | ✅ |  ❌  |
| accounting-charges | id | DefaultPaginator | ✅ |  ❌  |
| maintenance-work-orders | id | DefaultPaginator | ✅ |  ✅  |
| unit_taxes_parent | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| crm_company_attachment |  | DefaultPaginator | ✅ |  ❌  |
| crm-tasks | id | DefaultPaginator | ✅ |  ❌  |
| units-amenity-groups | id | DefaultPaginator | ✅ |  ❌  |
| nodes-types | id | DefaultPaginator | ✅ |  ❌  |
| charges | id | DefaultPaginator | ✅ |  ❌  |
| date-groups | id | DefaultPaginator | ✅ |  ❌  |
| documents | id | DefaultPaginator | ✅ |  ❌  |
| folios-rules | id | DefaultPaginator | ✅ |  ❌  |
| folio_logs | id | DefaultPaginator | ✅ |  ❌  |
| maintenance-problems | id | DefaultPaginator | ✅ |  ❌  |
| owners_units | ownerId.id | DefaultPaginator | ✅ |  ❌  |
| owners-contracts | id | DefaultPaginator | ✅ |  ❌  |
| owner-statements | id | DefaultPaginator | ✅ |  ❌  |
| owner_statment_transactions | id | DefaultPaginator | ✅ |  ❌  |
| promo-codes | id | DefaultPaginator | ✅ |  ❌  |
| reservations-cancellation-policies | id | DefaultPaginator | ✅ |  ❌  |
| reservations-guarantee-policies | id | DefaultPaginator | ✅ |  ❌  |
| reservation-cancellation-reasons | id | DefaultPaginator | ✅ |  ❌  |
| reservation-discount-reasons | id | DefaultPaginator | ✅ |  ❌  |
| units-bed-types | id | DefaultPaginator | ✅ |  ❌  |
| custom-fields | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| rate-types | id | DefaultPaginator | ✅ |  ❌  |
| group_blocks | group_id.id | DefaultPaginator | ✅ |  ❌  |
| group_tags | group_id.id | DefaultPaginator | ✅ |  ❌  |
| group_breakdown | group_id | DefaultPaginator | ✅ |  ❌  |
| suspend-code-reasons | id | DefaultPaginator | ✅ |  ❌  |
| units_channel | unit_id.id | DefaultPaginator | ✅ |  ❌  |
| housekeeping-work-orders | id | DefaultPaginator | ✅ |  ✅  |
| housekeeping-clean-types | id | DefaultPaginator | ✅ |  ❌  |
| housekeeping-task-list | id | DefaultPaginator | ✅ |  ❌  |
| folios_master_rules | id | DefaultPaginator | ✅ |  ❌  |
| contact_companies | contactId.companyId | DefaultPaginator | ✅ |  ❌  |
| reviews | id | DefaultPaginator | ✅ |  ❌  |
| accounting-deposits | id | DefaultPaginator | ✅ |  ❌  |
| accounting-deposits-payments | id | DefaultPaginator | ✅ |  ❌  |
| units_pricing_parent | id | DefaultPaginator | ✅ |  ✅  |
| unit_types_pricing_parent | id | DefaultPaginator | ✅ |  ❌  |
| unit_charge_pricing_parent | id | DefaultPaginator | ✅ |  ❌  |
| owners-pii-redacted | id | DefaultPaginator | ✅ |  ✅  |
| contacts-pii-redacted | id | DefaultPaginator | ✅ |  ✅  |
| owner_statement_transactions_pii_redacted | id | DefaultPaginator | ✅ |  ❌  |
| users-pii-redacted | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-10-18 | Initial release by [@blakeflei](https://github.com/blakeflei) via Connector Builder|

</details>