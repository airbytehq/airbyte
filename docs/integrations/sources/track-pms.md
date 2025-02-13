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
| accounting_accounts | id | DefaultPaginator | ✅ |  ❌  |
| accounting_bills | id | DefaultPaginator | ✅ |  ❌  |
| accounting_charges | id | DefaultPaginator | ✅ |  ❌  |
| accounting_deposits | id | DefaultPaginator | ✅ |  ❌  |
| accounting_deposits_payments | id | DefaultPaginator | ✅ |  ❌  |
| accounting_items | id | DefaultPaginator | ✅ |  ❌  |
| accounting_transactions | id | DefaultPaginator | ✅ |  ❌  |
| charges | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ✅  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| contacts_companies | contactId.companyId | DefaultPaginator | ✅ |  ❌  |
| contacts_pii_redacted | id | DefaultPaginator | ✅ |  ✅  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| crm_company_attachment | company_id.id | DefaultPaginator | ✅ |  ❌  |
| crm_tasks | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| date_groups | id | DefaultPaginator | ✅ |  ❌  |
| documents | id | DefaultPaginator | ✅ |  ❌  |
| folios | id | DefaultPaginator | ✅ |  ❌  |
| folios_logs | folio_id.id | DefaultPaginator | ✅ |  ❌  |
| folios_master_rules | id | DefaultPaginator | ✅ |  ❌  |
| folios_rules | id | DefaultPaginator | ✅ |  ❌  |
| fractionals | id | DefaultPaginator | ✅ |  ❌  |
| fractionals_inventory | fraction_id.id | DefaultPaginator | ✅ |  ❌  |
| fractionals_owners | fraction_id.id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| groups_blocks | group_id.id | DefaultPaginator | ✅ |  ❌  |
| groups_breakdown | group_id | DefaultPaginator | ✅ |  ❌  |
| groups_tags | group_id.id | DefaultPaginator | ✅ |  ❌  |
| housekeeping_clean_types | id | DefaultPaginator | ✅ |  ❌  |
| housekeeping_task_list | id | DefaultPaginator | ✅ |  ❌  |
| housekeeping_work_orders | id | DefaultPaginator | ✅ |  ✅  |
| lodging_types | id | DefaultPaginator | ✅ |  ❌  |
| maintenance_problems | id | DefaultPaginator | ✅ |  ❌  |
| maintenance_work_orders | id | DefaultPaginator | ✅ |  ✅  |
| nodes | id | DefaultPaginator | ✅ |  ❌  |
| nodes_types | id | DefaultPaginator | ✅ |  ❌  |
| owners | id | DefaultPaginator | ✅ |  ✅  |
| owners_contracts | id | DefaultPaginator | ✅ |  ❌  |
| owners_pii_redacted | id | DefaultPaginator | ✅ |  ✅  |
| owners_statements | id | DefaultPaginator | ✅ |  ❌  |
| owners_statements_transactions | statement_id.id | DefaultPaginator | ✅ |  ❌  |
| owners_statements_transactions_pii_redacted | statement_id.id | DefaultPaginator | ✅ |  ❌  |
| owners_units | ownerId.id | DefaultPaginator | ✅ |  ❌  |
| promo_codes | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| rate_types | id | DefaultPaginator | ✅ |  ❌  |
| reservations | id | DefaultPaginator | ✅ |  ✅  |
| reservations_cancellation_policies | id | DefaultPaginator | ✅ |  ❌  |
| reservations_cancellation_reasons | id | DefaultPaginator | ✅ |  ❌  |
| reservations_discount_reasons | id | DefaultPaginator | ✅ |  ❌  |
| reservations_guarantee_policies | id | DefaultPaginator | ✅ |  ❌  |
| reservations_types | id | DefaultPaginator | ✅ |  ❌  |
| reservations_v2 | id | DefaultPaginator | ✅ |  ✅  |
| reviews | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| suspend_code_reasons | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| tax_districts | id | DefaultPaginator | ✅ |  ❌  |
| tax_policies | id | DefaultPaginator | ✅ |  ❌  |
| taxes | id | DefaultPaginator | ✅ |  ❌  |
| travel_insurance_products | id | DefaultPaginator | ✅ |  ❌  |
| units | id | DefaultPaginator | ✅ |  ✅  |
| units_amenities | id | DefaultPaginator | ✅ |  ❌  |
| units_amenity_groups | id | DefaultPaginator | ✅ |  ❌  |
| units_bed_types | id | DefaultPaginator | ✅ |  ❌  |
| units_blocks | id | DefaultPaginator | ✅ |  ❌  |
| units_channel | unit_id.id | DefaultPaginator | ✅ |  ❌  |
| units_charge_pricing_parent | id | DefaultPaginator | ✅ |  ❌  |
| units_daily_pricing_v2 | unit_id.rateTypeId | DefaultPaginator | ✅ |  ❌  |
| units_pricing_parent | id | DefaultPaginator | ✅ |  ✅  |
| units_taxes | unit_id.id | DefaultPaginator | ✅ |  ❌  |
| units_taxes_parent | id | DefaultPaginator | ✅ |  ✅  |
| units_type_daily_pricing_v2 | unit_type_id.rateTypeId | DefaultPaginator | ✅ |  ❌  |
| units_types | id | DefaultPaginator | ✅ |  ❌  |
| units_types_pricing_parent | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| users_pii_redacted | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 2.0.0 | 2025-02-13 | Rename and alphabetize folio_id stream |
| 1.0.0 | 2025-01-16 | Fix housekeeping_work_orders incremental field; add reservations endpoint |
| 0.1.0 | 2025-01-16 | Move kebab case streams to snake case; alphabetize streams |
| 0.0.1 | 2024-10-18 | Initial release by [@blakeflei](https://github.com/blakeflei) via Connector Builder|
</details>
