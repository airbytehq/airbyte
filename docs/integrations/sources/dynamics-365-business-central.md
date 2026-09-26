# Dynamics 365 Business Central

The Dynamics 365 Business Central connector for Airbyte enables syncing financial and business data from Microsoft Dynamics 365 Business Central via the OData v4 REST API (v2.0). It supports general ledger entries, chart of accounts, customers, vendors, invoices, and journals.

## Prerequisites

- A Microsoft Dynamics 365 Business Central environment (cloud/SaaS)
- An Azure AD (Entra ID) app registration with API permissions for Business Central
- Client credentials (client ID and client secret) for OAuth 2.0 service-to-service authentication

## Setup Guide

1. Register an application in the [Azure portal](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).
2. Grant the application the **API permissions** for Dynamics 365 Business Central (e.g., `Financials.ReadWrite.All` or `API.ReadWrite.All`).
3. Create a **client secret** for the application.
4. Note the **Tenant ID**, **Client ID**, and **Client Secret**.
5. Ensure the application is authorized in your Business Central environment under **Azure Active Directory Applications**.

For detailed steps, see [Using Service-to-Service (S2S) Authentication](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/automation-apis-using-s2s-authentication).

## Configuration

| Input              | Type     | Description                                                                 | Default Value |
| ------------------ | -------- | --------------------------------------------------------------------------- | ------------- |
| `tenant_id`        | `string` | Azure AD tenant ID.                                                         |               |
| `client_id`        | `string` | OAuth 2.0 client (application) ID.                                          |               |
| `client_secret`    | `string` | OAuth 2.0 client secret.                                                    |               |
| `environment_name` | `string` | Business Central environment name.                                          | production    |
| `company_id`       | `string` | Optional GUID of a specific company to sync. Omit to sync all companies.    |               |
| `start_date`       | `string` | Earliest date for incremental sync (ISO 8601, e.g. `2017-01-01T00:00:00Z`). |               |

## Streams

| Stream Name            | Primary Key | Pagination       | Supports Full Sync | Supports Incremental |
| ---------------------- | ----------- | ---------------- | ------------------ | -------------------- |
| companies              | id          | DefaultPaginator | ✅                  | ❌                    |
| general_ledger_entries | id          | DefaultPaginator | ✅                  | ✅                    |
| accounts               | id          | DefaultPaginator | ✅                  | ✅                    |
| customers              | id          | DefaultPaginator | ✅                  | ✅                    |
| vendors                | id          | DefaultPaginator | ✅                  | ✅                    |
| sales_invoices         | id          | DefaultPaginator | ✅                  | ✅                    |
| purchase_invoices      | id          | DefaultPaginator | ✅                  | ✅                    |
| journals               | id          | DefaultPaginator | ✅                  | ✅                    |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
| ------- | ---------- | -------------------------------------------------------- | --------------- |
| 0.0.1   | 2026-02-26 | [74070](https://github.com/airbytehq/airbyte/pull/74070) | Initial release |

</details>
