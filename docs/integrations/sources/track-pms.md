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
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental | API Docs |
|-------------|-------------|------------|---------------------|----------------------|----------------------|
| accounting_accounts | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getledgeraccounts) |
| accounting_bills | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getbillscollection) |
| accounting_charges | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getaccountingchargescollection) |
| accounting_deposits | id | DefaultPaginator | ✅ |  ❌  | Undocumented |
| accounting_deposits_payments | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getdepositpayments) |
| accounting_items | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getitemscollection) |
| accounting_transactions | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getowneridtransactionscollection) |
| charges | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getchargescollection) |
| companies | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getcompanies) |
| contacts | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getcontacts) |
| contacts_companies | contactId.companyId | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getcontactcompanies) |
| contacts_pii_redacted | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getcontacts) |
| contracts | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getownercontractcollection) |
| crm_company_attachment | company_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getcompanyattachments) |
| crm_tasks | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/gettasks) |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getcustomfields) |
| date_groups | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getdategroupcollection) |
| documents | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getalldocuments) |
| folios | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getfolioscollection) |
| folios_logs | folio_id.id | DefaultPaginator | ✅ |  ❌  | Undocumented |
| folios_rules | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getfoliorulescollection) |
| fractionals | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/get-pms-fractionals) |
| fractionals_inventory | fraction_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/get-pms-fractionals-fractionalid-invetories) |
| fractionals_owners | fraction_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/get-pms-fractionals-owners) |
| groups | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getgroupscollection) |
| groups_blocks | group_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getgroupblockmappingcollection) |
| groups_breakdown | group_id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getgroupbreakdown) |
| groups_tags | group_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getgrouptagmappingcollection) |
| housekeeping_clean_types | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getcleantypes) |
| housekeeping_task_list | id | DefaultPaginator | ✅ |  ❌  | Undocumented |
| housekeeping_work_orders | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getworkorders) |
| lodging_types | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getlodgingtypescollection) |
| maintenance_problems | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getmaintenanceproblemscollection) |
| maintenance_work_orders | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getmaintworkorders) |
| nodes | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getnodes) |
| nodes_types | id | DefaultPaginator | ✅ |  ❌  | Undocumented |
| owners | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getownercollection) |
| owners_contracts | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getownercontractcollection) |
| owners_pii_redacted | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getownercollection) |
| owners_statements | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/get-pms-statements) |
| owners_statements_transactions | statement_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getstatementtransactionscollection) |
| owners_units | ownerId.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getownerunitscollection) |
| promo_codes | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getpromocodes) |
| quotes | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getquotescollectionv2) |
| rate_types | id | DefaultPaginator | ✅ |  ❌  | Undocumented |
| reservations | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getreservations) |
| reservations_cancellation_policies | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getcancellationpolicies) |
| reservations_cancellation_reasons | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getcancellationreasons) |
| reservations_discount_reasons | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getdiscountreasons) |
| reservations_guarantee_policies | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/get-pms-reservations-policies-guaranties) |
| reservations_types | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getreservationtypes) |
| reservations_v2 | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getreservations-1) |
| reviews | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getreviewscollection) |
| roles | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunitrolescollection) |
| suspend_code_reasons | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getsuspendcodereasons) |
| tags | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/gettagscollection) |
| tax_districts | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/gettaxdistrictscollection) |
| tax_policies | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/gettaxpolicycollection) |
| taxes | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/gettaxcollection) |
| travel_insurance_products | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/gettravelinsuranceproducts) |
| units | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getchannelunits) |
| units_amenities | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunitamenities) |
| units_amenity_groups | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunitamenitygroups) |
| units_bed_types | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getbedtypescollection) |
| units_blocks | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunitblockscollection) |
| units_channel | unit_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunitchannelunitcollection) |
| units_charge_pricing_parent | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getchargescollection) |
| units_daily_pricing_v2 | unit_id.rateTypeId | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunittypedailypricing) |
| units_pricing_parent | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getchannelunits) |
| units_taxes | unit_id.id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunitchanneltaxcollection) |
| units_taxes_parent | id | DefaultPaginator | ✅ |  ✅  | [Link](https://developer.trackhs.com/reference/getchannelunits) |
| units_type_daily_pricing_v2 | unit_type_id.rateTypeId | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getv2unittypedailypricing) |
| units_types | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunittypes-2) |
| units_types_pricing_parent | id | DefaultPaginator | ✅ |  ❌  | [Link](https://developer.trackhs.com/reference/getunittypes-2) |
| users | id | DefaultPaginator | ✅ |  ❌  | Undocumented |
| users_pii_redacted | id | DefaultPaginator | ✅ |  ❌  | Undocumented |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 3.0.0 | 2025-02-26 | Drop redundant streams & omit unneeded sensitive fields from accounting_* streams |
| 2.0.0 | 2025-02-13 | Rename and alphabetize folio_id stream |
| 1.0.0 | 2025-01-16 | Fix housekeeping_work_orders incremental field; add reservations endpoint |
| 0.1.0 | 2025-01-16 | Move kebab case streams to snake case; alphabetize streams |
| 0.0.1 | 2024-10-18 | Initial release by [@blakeflei](https://github.com/blakeflei) via Connector Builder|
</details>
