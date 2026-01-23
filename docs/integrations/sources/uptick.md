# Uptick

Extract data from Uptick, a field service management platform designed for the fire protection industry.

## Prerequisites

To use the Uptick connector, you need:

- An Uptick account with API access enabled
- OAuth credentials (Client ID and Client Secret) generated from your Uptick instance
- Your Uptick instance URL (for example, `https://yourcompany.onuptick.com`)

To generate OAuth credentials, go to **Control Panel > Uptick API** in your Uptick instance and select **Create Application**. For more information, see the [Uptick API documentation](https://support.uptickhq.com/en/collections/9129536-uptick-api).

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | Your Uptick instance URL, for example `https://yourcompany.onuptick.com`. Do not include a trailing slash. |  |
| `client_id` | `string` | OAuth Client ID generated from Control Panel > Uptick API. |  |
| `client_secret` | `string` | OAuth Client Secret generated from Control Panel > Uptick API. |  |
| `username` | `string` | Email address for an Uptick user account with API access. |  |
| `password` | `string` | Password for the Uptick user account. |  |

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
- `billingcontracts` - Recurring billing contracts for ongoing services
- `billingcontractlineitems` - Line items within billing contracts
- `costcentres` - Cost center assignments for financial tracking
- `task_profitability` - Profitability metrics and financial performance data for tasks

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
- `routineservices` - Routine service configurations for properties and assets
- `routineservicelevels` - Service level definitions for routine services
- `routineservicetypes` - Types and categories of routine services
- `routineserviceleveltypes` - Service level type classifications
- `servicetasks` - Individual work activities on tasks
- `subtasks` - Links programme maintenance routines to tasks
- `remarks` - Issues, defects, and observations during inspections
- `remarkevents` - Events and actions taken on remarks
- `appointments` - Scheduled appointments for work and inspections

### Quality and compliance

- `accreditations` - Technician certifications and qualifications
- `accreditationtypes` - Types of certifications and accreditations

### Sales

- `servicequotes` - Quotes for service work
- `servicequotefixedlineitems` - Fixed price line items within service quotes
- `servicequotedoandchargelineitems` - Do-and-charge line items within service quotes
- `servicequoteproductlineitems` - Product line items within service quotes
- `defectquotes` - Quotes for remedial work on identified defects
- `defectquotelineitems` - Line items within defect quotes

### Organization and location

- `branches` - Business locations and organizational units

### Stream details

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ | ✅ |
| taskcategories | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| clients | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| clientgroups | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| properties | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| invoices | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| projects | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| servicequotes | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| defectquotes | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| suppliers | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| purchaseorders | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| purchaseorderlineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| assets | id | DefaultPaginator | ✅ | ✅ |
| routines | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| billingcards | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| purchaseorderbills | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| purchaseorderbilllineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| purchaseorderdockets | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| invoicelineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| users | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| servicegroups | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| costcentres | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| accreditationtypes | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| accreditations | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| branches | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| creditnotes | id | DefaultPaginator | ✅ | ✅ |
| creditnotelineitems | id | DefaultPaginator | ✅ | ✅ |
| remarks | id | DefaultPaginator | ✅ | ✅ |
| assettypes | id | DefaultPaginator | ✅ | ✅ |
| assettypevariants | id | DefaultPaginator | ✅ | ✅ |
| products | id | DefaultPaginator | ✅ | ✅ |
| rounds | id | DefaultPaginator | ✅ | ✅ |
| tasksessions | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| contractors | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| appointments | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| billingcontracts | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| billingcontractlineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| defectquotelineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| servicequotefixedlineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| servicequotedoandchargelineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| servicequoteproductlineitems | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| remarkevents | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| routineservices | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| routineservicelevels | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| routineservicetypes | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| routineserviceleveltypes | id | DefaultPaginator | ✅ | ❌ (no soft delete) |
| servicetasks | id | DefaultPaginator | ✅ | ✅ |
| subtasks | id | DefaultPaginator | ✅ | ✅ |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.5.1 | 2026-01-23 | [72302](https://github.com/airbytehq/airbyte/pull/72302) | Add branch, client, property, author, and salesperson fields to defectquotes |
| 0.5.0 | 2026-01-13 | [71122](https://github.com/airbytehq/airbyte/pull/71122) | Add invoice_id to invoicelineitems, and add 6 new streams: servicetasks, routineservices, routineservicelevels, routineservicetypes, routineserviceleveltypes, subtasks |
| 0.4.3 | 2026-01-20 | [72056](https://github.com/airbytehq/airbyte/pull/72056) | Update dependencies |
| 0.4.2 | 2026-01-14 | [71437](https://github.com/airbytehq/airbyte/pull/71437) | Update dependencies |
| 0.4.1 | 2025-12-18 | [70713](https://github.com/airbytehq/airbyte/pull/70713) | Update dependencies |
| 0.4.0 | 2025-12-10 | [68194](https://github.com/airbytehq/airbyte/pull/68194) | Remove expensive calculation fields from tasksessions, add more streams, including task profitability |
| 0.3.9 | 2025-11-25 | [70176](https://github.com/airbytehq/airbyte/pull/70176) | Update dependencies |
| 0.3.8 | 2025-11-18 | [69684](https://github.com/airbytehq/airbyte/pull/69684) | Update dependencies |
| 0.3.7 | 2025-10-29 | [68880](https://github.com/airbytehq/airbyte/pull/68880) | Update dependencies |
| 0.3.6 | 2025-10-21 | [68365](https://github.com/airbytehq/airbyte/pull/68365) | Update dependencies |
| 0.3.5 | 2025-10-17 | [67585](https://github.com/airbytehq/airbyte/pull/67585) | Remove projectsectiontask and add more incremental sync streams |
| 0.3.4 | 2025-10-14 | [67855](https://github.com/airbytehq/airbyte/pull/67855) | Update dependencies |
| 0.3.3 | 2025-10-07 | [67515](https://github.com/airbytehq/airbyte/pull/67515) | Update dependencies |
| 0.3.2 | 2025-10-03 | [67020](https://github.com/airbytehq/airbyte/pull/67020) | Remove start_date, include more task fields |
| 0.3.1 | 2025-09-30 | [66839](https://github.com/airbytehq/airbyte/pull/66839) | Update dependencies |
| 0.3.0 | 2025-09-25 | [66410](https://github.com/airbytehq/airbyte/pull/66410) | Add more streams |
| 0.2.4 | 2025-09-24 | [66598](https://github.com/airbytehq/airbyte/pull/66598) | Update dependencies |
| 0.2.3 | 2025-09-09 | [65733](https://github.com/airbytehq/airbyte/pull/65733) | Update dependencies |
| 0.2.2 | 2025-09-07 | [65534](https://github.com/airbytehq/airbyte/pull/65534) | Add extra_fields to property stream |
| 0.2.1 | 2025-08-24 | [65445](https://github.com/airbytehq/airbyte/pull/65445) | Update dependencies |
| 0.2.0 | 2025-08-22 | | Update task profitability stream to use start_date parameter |
| 0.0.11 | 2025-08-21 | [65061](https://github.com/airbytehq/airbyte/pull/65061) | Add users and task profitability streams |
| 0.0.10 | 2025-08-15 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.9 | 2025-08-14 | [64170](https://github.com/airbytehq/airbyte/pull/64170) | adds cursor pagination, incremental sync and rate limiting |
| 0.0.8 | 2025-08-10 | [64845](https://github.com/airbytehq/airbyte/pull/64845) | Update dependencies |
| 0.0.7 | 2025-08-02 | [64403](https://github.com/airbytehq/airbyte/pull/64403) | Update dependencies |
| 0.0.6 | 2025-07-26 | [64055](https://github.com/airbytehq/airbyte/pull/64055) | Update dependencies |
| 0.0.5 | 2025-07-20 | [63685](https://github.com/airbytehq/airbyte/pull/63685) | Update dependencies |
| 0.0.4 | 2025-07-12 | [63165](https://github.com/airbytehq/airbyte/pull/63165) | Update dependencies |
| 0.0.3 | 2025-07-05 | [62739](https://github.com/airbytehq/airbyte/pull/62739) | Update dependencies |
| 0.0.2 | 2025-06-28 | [62220](https://github.com/airbytehq/airbyte/pull/62220) | Update dependencies |
| 0.0.1 | 2025-06-10 | | Initial release by [@sajarin](https://github.com/sajarin) via Connector Builder |

</details>
