# Uptick

Extract data from Uptick, a field service management platform designed for the fire protection industry.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | Base URL eg https://demo-fire.onuptick.com (no trailing slash) |  |
| `client_id` | `string` | API Client ID |  |
| `client_secret` | `string` | API Client Secret  |  |
| `username` | `string` | API Account Email |  |
| `password` | `string` | API Account Password |  |

## Streams

The Uptick connector syncs data from the following streams, organized by functional area:

### Core business entities

- `tasks` - Work tasks and maintenance requests with scheduling, priority, and assignment details
- `taskcategories` - Categories for organizing tasks
- `tasksessions` - Time tracking entries for work performed on tasks
- `rounds` - Work rounds for technician scheduling and route management
- `projects` - Project management entities for larger initiatives
- `clients` - Customer organizations and contact information
- `clientgroups` - Client organization groupings
- `properties` - Physical locations where work is performed
- `contractors` - External service providers and subcontractors
- `users` - System users including technicians and staff
- `servicegroups` - Service categorization for organizing work types

### Financial and billing

- `invoices` - Customer invoices and billing information
- `invoicelineitems` - Individual line items within invoices
- `creditnotes` - Credit notes for refunds and adjustments
- `creditnotelineitems` - Line items within credit notes
- `billingcards` - Billing card information for cost allocation
- `costcentres` - Cost center assignments for financial tracking

### Purchasing and supply chain

- `purchaseorders` - Purchase orders for materials and services
- `purchaseorderlineitems` - Individual items within purchase orders
- `purchaseorderbills` - Bills received for purchase orders
- `purchaseorderbilllineitems` - Line items within purchase order bills
- `purchaseorderdockets` - Delivery dockets for purchase orders
- `suppliers` - Vendor and supplier information
- `products` - Products and materials catalog

### Asset management and inspections

- `assets` - Physical assets requiring maintenance and inspection
- `assettypes` - Categories and specifications for asset types
- `assettypevariants` - Variants and configurations of asset types
- `routines` - Scheduled maintenance and inspection routines
- `remarks` - Issues, defects, and observations during inspections

### Quality and compliance

- `accreditations` - Technician certifications and qualifications
- `accreditationtypes` - Types of certifications and accreditations

### Sales

- `servicequotes` - Quotes for service work
- `defectquotes` - Quotes for remedial work on identified defects

### Organization and location

- `branches` - Business locations and organizational units

### Stream details

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ✅  |
| taskcategories | id | DefaultPaginator | ✅ |  ✅  |
| clients | id | DefaultPaginator | ✅ |  ✅  |
| clientgroups | id | DefaultPaginator | ✅ |  ✅  |
| properties | id | DefaultPaginator | ✅ |  ✅  |
| invoices | id | DefaultPaginator | ✅ |  ✅  |
| projects | id | DefaultPaginator | ✅ |  ✅  |
| servicequotes | id | DefaultPaginator | ✅ |  ✅  |
| defectquotes | id | DefaultPaginator | ✅ |  ✅  |
| suppliers | id | DefaultPaginator | ✅ |  ✅  |
| purchaseorders | id | DefaultPaginator | ✅ |  ✅  |
| assets | id | DefaultPaginator | ✅ |  ✅  |
| routines | id | DefaultPaginator | ✅ |  ✅  |
| billingcards | id | DefaultPaginator | ✅ |  ✅  |
| purchaseorderbills | id | DefaultPaginator | ✅ |  ✅  |
| purchaseorderdockets | id | DefaultPaginator | ✅ |  ✅  |
| invoicelineitems | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| servicegroups | id | DefaultPaginator | ✅ |  ✅  |
| costcentres | id | DefaultPaginator | ✅ |  ✅  |
| purchaseorderlineitems | id | DefaultPaginator | ✅ |  ❌  |
| purchaseorderbilllineitems | id | DefaultPaginator | ✅ |  ❌  |
| accreditationtypes | id | DefaultPaginator | ✅ |  ✅  |
| accreditations | id | DefaultPaginator | ✅ |  ✅  |
| branches | id | DefaultPaginator | ✅ |  ✅  |
| creditnotes | id | DefaultPaginator | ✅ |  ✅  |
| creditnotelineitems | id | DefaultPaginator | ✅ |  ✅  |
| remarks | id | DefaultPaginator | ✅ |  ✅  |
| assettypes | id | DefaultPaginator | ✅ |  ✅  |
| assettypevariants | id | DefaultPaginator | ✅ |  ✅  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| rounds | id | DefaultPaginator | ✅ |  ✅  |
| tasksessions | id | DefaultPaginator | ✅ |  ✅  |
| contractors | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.3.10 | 2025-12-09 | [70713](https://github.com/airbytehq/airbyte/pull/70713) | Update dependencies |
| 0.3.9 | 2025-11-25 | [70176](https://github.com/airbytehq/airbyte/pull/70176) | Update dependencies |
| 0.3.8 | 2025-11-18 | [69684](https://github.com/airbytehq/airbyte/pull/69684) | Update dependencies |
| 0.3.7 | 2025-10-29 | [68880](https://github.com/airbytehq/airbyte/pull/68880) | Update dependencies |
| 0.3.6 | 2025-10-21 | [68365](https://github.com/airbytehq/airbyte/pull/68365) | Update dependencies |
| 0.3.5 | 2025-10-17 | [67585](https://github.com/airbytehq/airbyte/pull/67585) | Remove projectsectiontask and add more incremental sync streams |
| 0.3.4 | 2025-10-14 | [67855](https://github.com/airbytehq/airbyte/pull/67855) | Update dependencies |
| 0.3.3 | 2025-10-07 | [67515](https://github.com/airbytehq/airbyte/pull/67515) | Update dependencies |
| 0.3.2 | 2025-10-03 | [67020](https://github.com/airbytehq/airbyte/pull/67020) | Remove start_date, include more task fields |
| 0.3.1 | 2025-09-30 | [66839](https://github.com/airbytehq/airbyte/pull/66839) | Update dependencies |
| 0.3.0 | 2025-09-17 | [66410](https://github.com/airbytehq/airbyte/pull/66410) | Add more streams |
| 0.2.4 | 2025-09-23 | [66598](https://github.com/airbytehq/airbyte/pull/66598) | Update dependencies |
| 0.2.3 | 2025-09-09 | [65733](https://github.com/airbytehq/airbyte/pull/65733) | Update dependencies |
| 0.2.2 | 2025-08-26 | [65534](https://github.com/airbytehq/airbyte/pull/65534) | Add extra_fields to property stream |
| 0.2.1 | 2025-08-24 | [65445](https://github.com/airbytehq/airbyte/pull/65445) | Update dependencies |
| 0.2.0 | 2025-08-22 | | Update task profitability stream to use start_date parameter |
| 0.0.11 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/65061) | Add users and task profitability streams |
| 0.0.10 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.9 | 2025-08-13 | [64170](https://github.com/airbytehq/airbyte/pull/64170) | adds cursor pagination, incremental sync and rate limiting |
| 0.0.8 | 2025-08-09 | [64845](https://github.com/airbytehq/airbyte/pull/64845) | Update dependencies |
| 0.0.7 | 2025-08-02 | [64403](https://github.com/airbytehq/airbyte/pull/64403) | Update dependencies |
| 0.0.6 | 2025-07-26 | [64055](https://github.com/airbytehq/airbyte/pull/64055) | Update dependencies |
| 0.0.5 | 2025-07-20 | [63685](https://github.com/airbytehq/airbyte/pull/63685) | Update dependencies |
| 0.0.4 | 2025-07-12 | [63165](https://github.com/airbytehq/airbyte/pull/63165) | Update dependencies |
| 0.0.3 | 2025-07-05 | [62739](https://github.com/airbytehq/airbyte/pull/62739) | Update dependencies |
| 0.0.2 | 2025-06-28 | [62220](https://github.com/airbytehq/airbyte/pull/62220) | Update dependencies |
| 0.0.1 | 2025-06-10 | | Initial release by [@sajarin](https://github.com/sajarin) via Connector Builder |

</details>
