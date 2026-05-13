# source-uptick: Contributor notes

## Supported streams

This connector syncs these streams from Uptick.

Core business entities:

- `tasks`: work tasks and maintenance requests with scheduling, priority, and assignment details
- `taskcategories`: categories for organizing tasks
- `tasksessions`: time tracking entries for work performed on tasks
- `rounds`: work rounds for technician scheduling and route management
- `projects`: project management entities for larger initiatives
- `clients`: customer organizations and contact information
- `clientgroups`: client organization groupings
- `properties`: physical locations where work is performed
- `contractors`: external service providers and subcontractors
- `users`: system users, including technicians and staff
- `servicegroups`: service categorization for organizing work types

Financial and billing:

- `invoices`: customer invoices and billing information
- `invoicelineitems`: individual line items within invoices
- `creditnotes`: credit notes for refunds and adjustments
- `creditnotelineitems`: line items within credit notes
- `billingcards`: billing card information for cost allocation
- `costcentres`: cost center assignments for financial tracking

Purchasing and supply chain:

- `purchaseorders`: purchase orders for materials and services
- `purchaseorderlineitems`: individual items within purchase orders
- `purchaseorderbills`: bills received for purchase orders
- `purchaseorderbilllineitems`: line items within purchase order bills
- `purchaseorderdockets`: delivery dockets for purchase orders
- `suppliers`: vendor and supplier information
- `products`: products and materials catalog

Asset management and inspections:

- `assets`: physical assets requiring maintenance and inspection
- `assettypes`: categories and specifications for asset types
- `assettypevariants`: variants and configurations of asset types
- `routines`: scheduled maintenance and inspection routines
- `routineservices`: routine service configurations for properties and assets
- `routineservicelevels`: service level definitions for routine services
- `routineservicetypes`: types and categories of routine services
- `routineserviceleveltypes`: service level type classifications
- `servicetasks`: individual work activities on tasks
- `subtasks`: links programme maintenance routines to tasks
- `remarks`: issues, defects, and observations during inspections

Quality and compliance:

- `accreditations`: technician certifications and qualifications
- `accreditationtypes`: types of certifications and accreditations

Sales:

- `servicequotes`: quotes for service work
- `defectquotes`: quotes for remedial work on identified defects

Organization and location:

- `branches`: business locations and organizational units
