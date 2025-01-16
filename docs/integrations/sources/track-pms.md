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
| unit_blocks | id | DefaultPaginator | ✅ |  ❌  |
| folios | id | DefaultPaginator | ✅ |  ❌  |
| nodes | id | DefaultPaginator | ✅ |  ❌  |
| units_amenities | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| reservations_v2 | id | DefaultPaginator | ✅ |  ✅  |
| reservation_types | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| unit_types | id | DefaultPaginator | ✅ |  ❌  |
| lodging_types | id | DefaultPaginator | ✅ |  ❌  |
| tax_districts | id | DefaultPaginator | ✅ |  ❌  |
| tax_policies | id | DefaultPaginator | ✅ |  ❌  |
| taxes | id | DefaultPaginator | ✅ |  ❌  |
| travel_insurance_products | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ✅  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| fractional_inventory | fraction_id.id | DefaultPaginator | ✅ |  ❌  |
| fractional_owners | fraction_id.id | DefaultPaginator | ✅ |  ❌  |
| unit_type_daily_pricing_v2 | unit_type_id.rateTypeId | DefaultPaginator | ✅ |  ❌  |
| unit_daily_pricing_v2 | unit_id.rateTypeId | DefaultPaginator | ✅ |  ❌  |
| unit_taxes | unit_id.id | DefaultPaginator | ✅ |  ❌  |
| accounting_items | id | DefaultPaginator | ✅ |  ❌  |
| accounting_accounts | id | DefaultPaginator | ✅ |  ❌  |
| accounting_transactions | id | DefaultPaginator | ✅ |  ❌  |
| accounting_bills | id | DefaultPaginator | ✅ |  ❌  |
| accounting_charges | id | DefaultPaginator | ✅ |  ❌  |
| maintenance_work_orders | id | DefaultPaginator | ✅ |  ✅  |
| unit_taxes_parent | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| crm_company_attachment |  | DefaultPaginator | ✅ |  ❌  |
| crm_tasks | id | DefaultPaginator | ✅ |  ❌  |
| units_amenity_groups | id | DefaultPaginator | ✅ |  ❌  |
| nodes_types | id | DefaultPaginator | ✅ |  ❌  |
| charges | id | DefaultPaginator | ✅ |  ❌  |
| date_groups | id | DefaultPaginator | ✅ |  ❌  |
| documents | id | DefaultPaginator | ✅ |  ❌  |
| folios_rules | id | DefaultPaginator | ✅ |  ❌  |
| folio_logs | id | DefaultPaginator | ✅ |  ❌  |
| maintenance_problems | id | DefaultPaginator | ✅ |  ❌  |
| owners_units | ownerId.id | DefaultPaginator | ✅ |  ❌  |
| owners_contracts | id | DefaultPaginator | ✅ |  ❌  |
| owner_statements | id | DefaultPaginator | ✅ |  ❌  |
| owner_statment_transactions | id | DefaultPaginator | ✅ |  ❌  |
| promo_codes | id | DefaultPaginator | ✅ |  ❌  |
| reservations_cancellation_policies | id | DefaultPaginator | ✅ |  ❌  |
| reservations_guarantee_policies | id | DefaultPaginator | ✅ |  ❌  |
| reservation_cancellation_reasons | id | DefaultPaginator | ✅ |  ❌  |
| reservation_discount_reasons | id | DefaultPaginator | ✅ |  ❌  |
| units_bed_types | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| rate_types | id | DefaultPaginator | ✅ |  ❌  |
| group_blocks | group_id.id | DefaultPaginator | ✅ |  ❌  |
| group_tags | group_id.id | DefaultPaginator | ✅ |  ❌  |
| group_breakdown | group_id | DefaultPaginator | ✅ |  ❌  |
| suspend_code_reasons | id | DefaultPaginator | ✅ |  ❌  |
| units_channel | unit_id.id | DefaultPaginator | ✅ |  ❌  |
| housekeeping_work_orders | id | DefaultPaginator | ✅ |  ✅  |
| housekeeping_clean_types | id | DefaultPaginator | ✅ |  ❌  |
| housekeeping_task_list | id | DefaultPaginator | ✅ |  ❌  |
| folios_master_rules | id | DefaultPaginator | ✅ |  ❌  |
| contact_companies | contactId.companyId | DefaultPaginator | ✅ |  ❌  |
| reviews | id | DefaultPaginator | ✅ |  ❌  |
| accounting_deposits | id | DefaultPaginator | ✅ |  ❌  |
| accounting_deposits_payments | id | DefaultPaginator | ✅ |  ❌  |
| units_pricing_parent | id | DefaultPaginator | ✅ |  ✅  |
| unit_types_pricing_parent | id | DefaultPaginator | ✅ |  ❌  |
| unit_charge_pricing_parent | id | DefaultPaginator | ✅ |  ❌  |
| owners_pii_redacted | id | DefaultPaginator | ✅ |  ✅  |
| contacts_pii_redacted | id | DefaultPaginator | ✅ |  ✅  |
| owner_statement_transactions_pii_redacted | id | DefaultPaginator | ✅ |  ❌  |
| users_pii_redacted | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-10-18 | Initial release by [@blakeflei](https://github.com/blakeflei) via Connector Builder|
| 0.1.0 | 2025-01-16 | move kebab case streams to snake case; alphabetize streams |
</details>