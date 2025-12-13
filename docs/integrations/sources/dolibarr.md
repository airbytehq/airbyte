# Dolibarr

Connector for the Dolibarr ERP/CRM REST API focused on GET operations

## Pre-requisites
- A Dolibarr Installation in Cloud SaaS, On-premises, Web Hosting or cPanel Server.
- Identify your public Dolibarr URL that will be required to configure the conector.
- Configure your company data in the Setup menu - Configure your company/organization: [Dolibarr documentation Wiki](https://wiki.dolibarr.org/index.php?title=First_setup#Company.2FOrganization)
- In the module setup menu enable the Module Web Services API REST (developer) and configure it.
- Enable the ERP/CRM modules of Dolibarr from you want to GET data with the REST API end points
- For the API Key access create a Dolibarr user in your installation with the permissions to "read" modules corresponding to the REST API end points you will use with the streams. (some streams or end points, like GET company information, will require that your user be administrator or have read/write permissions to works fine with the GET end point)
- In the setup/modify menu of the user created in the previous step, generate the API Key (different to the user password) that will be required for the setup of the connector.
- Now your are ready to work with this connector.
- For additional information about the use and configuration of your Dolibarr connection please review this guide: [Integration of Dolibarr to the Airbyte data integration platform](https://wiki.dolibarr.org/index.php?title=Integration_of_Dolibarr_to_the_Airbyte_data_integration_platform)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `my_dolibarr_domain_url` | `string` | `my_dolibarr_domain/url`. Enter your `domain/dolibarr_url` without `https://` Example: `mydomain.com/dolibarr` |  |
| `start_date` | `date` | Earliest start date of synchronization in source data in format `YYYY-MM-DDTHH:mm:ssZ` Enter the earliest modification date of data you want to incrementally synchronize |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Products list | product_id | DefaultPaginator | ✅ |  ✅  |
| Products category id list |  | No pagination | ✅ |  ❌  |
| Product categories list | category_id | DefaultPaginator | ✅ |  ✅  |
| Customer invoices list | invoice_id | DefaultPaginator | ✅ |  ✅  |
| Customer invoices lines list |  | No pagination | ✅ |  ❌  |
| Customers list | customer_id | DefaultPaginator | ✅ |  ✅  |
| Supplier invoices list | supp_invoice_id | DefaultPaginator | ✅ |  ✅  |
| Supplier invoices lines list |  | No pagination | ✅ |  ❌  |
| Suppliers list | supplier_id | DefaultPaginator | ✅ |  ✅  |
| Internal Users | user_id | DefaultPaginator | ✅ |  ✅  |
| Company profile data |  | No pagination | ✅ |  ❌  |
| Customer invoices payments list | ref | No pagination | ✅ |  ❌  |
| Supplier invoices payments list | ref | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 1.0.13 | 2025-10-07 | [67155](https://github.com/airbytehq/airbyte/pull/67155) | Update dependencies |
| 1.0.12 | 2025-09-30 | [65758](https://github.com/airbytehq/airbyte/pull/65758) | Update dependencies |
| 1.0.11 | 2025-08-23 | [65305](https://github.com/airbytehq/airbyte/pull/65305) | Update dependencies |
| 1.0.10 | 2025-08-09 | [64715](https://github.com/airbytehq/airbyte/pull/64715) | Update dependencies |
| 1.0.9 | 2025-08-02 | [64362](https://github.com/airbytehq/airbyte/pull/64362) | Update dependencies |
| 1.0.8 | 2025-07-26 | [63981](https://github.com/airbytehq/airbyte/pull/63981) | Update dependencies |
| 1.0.7 | 2025-07-19 | [63581](https://github.com/airbytehq/airbyte/pull/63581) | Update dependencies |
| 1.0.6 | 2025-07-12 | [62976](https://github.com/airbytehq/airbyte/pull/62976) | Update dependencies |
| 1.0.5 | 2025-07-09 | [62869](https://github.com/airbytehq/airbyte/pull/62869) | Enabled "incremental Parent" switch for the child streams that have parent streams with incremental sync. |
| 1.0.4 | 2025-07-05 | [62779](https://github.com/airbytehq/airbyte/pull/62779) | Update dependencies |
| 1.0.3 | 2025-06-28 | [62306](https://github.com/airbytehq/airbyte/pull/62306) | Update dependencies |
| 1.0.2 | 2025-06-22 | [61992](https://github.com/airbytehq/airbyte/pull/61992) | Update dependencies |
| 1.0.1 | 2025-06-14 | [61174](https://github.com/airbytehq/airbyte/pull/61174) | Update dependencies |
| 1.0.0 | 2025-06-05 | [61388](https://github.com/airbytehq/airbyte/pull/61388) | Implements incremental sync in all applicable parent streams, improves the performance and efficiency of data extraction, compatible with Dolibarr 21.0.0 or higher versions |
| 0.0.1 | 2025-05-20 | [60320](https://github.com/airbytehq/airbyte/pull/60320) | Initial release by [@leonmm2](https://github.com/leonmm2) via Connector Builder |

</details>
