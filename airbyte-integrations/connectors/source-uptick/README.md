# Uptick

This directory contains the manifest-only connector for `source-uptick`.

Extract data from Uptick (field service management).

## Usage

There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Supported Streams

This connector syncs the following streams from Uptick:

### Core Business Entities

- **tasks** - Work tasks and maintenance requests with scheduling, priority, and assignment details
- **taskcategories** - Categories for organizing tasks
- **tasksessions** - Time tracking entries for work performed on tasks
- **rounds** - Work rounds for technician scheduling and route management
- **projects** - Project management entities for larger initiatives
- **clients** - Customer organizations and contact information
- **clientgroups** - Client organization groupings
- **properties** - Physical locations where work is performed
- **contractors** - External service providers and subcontractors
- **users** - System users including technicians and staff
- **servicegroups** - Service categorization for organizing work types

### Financial & Billing

- **invoices** - Customer invoices and billing information
- **invoicelineitems** - Individual line items within invoices
- **creditnotes** - Credit notes for refunds and adjustments
- **creditnotelineitems** - Line items within credit notes
- **billingcards** - Billing card information for cost allocation
- **costcentres** - Cost center assignments for financial tracking

### Purchasing & Supply Chain

- **purchaseorders** - Purchase orders for materials and services
- **purchaseorderlineitems** - Individual items within purchase orders
- **purchaseorderbills** - Bills received for purchase orders
- **purchaseorderbilllineitems** - Line items within purchase order bills
- **purchaseorderdockets** - Delivery dockets for purchase orders
- **suppliers** - Vendor and supplier information
- **products** - Products and materials catalog

### Asset Management & Inspections

- **assets** - Physical assets requiring maintenance and inspection
- **assettypes** - Categories and specifications for asset types
- **assettypevariants** - Variants and configurations of asset types
- **routines** - Scheduled maintenance and inspection routines
- **remarks** - Issues, defects, and observations during inspections

### Quality & Compliance

- **accreditations** - Technician certifications and qualifications
- **accreditationtypes** - Types of certifications and accreditations

### Sales

- **servicequotes** - Quotes for service work
- **defectquotes** - Quotes for remedial work on identified defects

### Organization & Location

- **branches** - Business locations and organizational units

## Local Development

We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup

You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build

This will create a dev image (`source-uptick:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-uptick build
```

### Test

This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-uptick test
```

