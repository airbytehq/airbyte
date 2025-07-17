# Xero

This page contains the setup guide and reference information for the Xero source connector.

## Prerequisites

- **Tenant ID** - The ID of your Xero organization (required)
- **Start Date** - The date from which you want to start replicating data (UTC format)

For multi-tenant Xero accounts, you'll need to select which organization to connect with using the Tenant ID. You can find your Tenant IDs by following the [Xero documentation](https://developer.xero.com/documentation/guides/oauth2/auth-flow/#xero-tenants).

**Required list of scopes to sync all streams:**

- accounting.attachments.read
- accounting.budgets.read
- accounting.contacts.read
- accounting.journals.read
- accounting.reports.read
- accounting.reports.tenninetynine.read
- accounting.settings.read
- accounting.transactions.read
- assets.read
- offline_access

## Authentication

There are two currently supported ways to authenticate with Xero:

For the bearer token strategy, please follow [instructions](https://developer.xero.com/documentation/guides/oauth2/pkce-flow/) to obtain all requirements:
- Client ID

For the OAuth client credentials, please follow [instructions](https://developer.xero.com/documentation/guides/oauth2/custom-connections) to obtain all requirements:
- Client ID
- Client Secret

## Setup guide

1. Create an application in [Xero development center](https://developer.xero.com/app/manage/).
2. Select the appropriate authentication method (bearer token or OAuth client credentials).
3. Configure the required scopes mentioned in the Prerequisites section.
4. For bearer token authentication:
   - Follow the [PKCE flow](https://developer.xero.com/documentation/guides/oauth2/pkce-flow/) to obtain an access token.
   - You can use Postman as described in the [migration guide](./xero-migrations.md#using-postman-to-get-access-token).
5. For OAuth client credentials:
   - Ensure you have both Client ID and Client Secret from your Xero application.
6. Enter your Xero Organisation's [Tenant ID](https://developer.xero.com/documentation/guides/oauth2/auth-flow/#xero-tenants).
7. Enter a Start Date in UTC format `YYYY-MM-DDTHH:mm:ssZ` from which you'd like to replicate data.

## Supported sync modes

The Xero source connector supports the following [sync modes](https://docs.airbyte.com/understanding-airbyte/connections/connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported streams

- [Accounts](https://developer.xero.com/documentation/api/accounting/accounts)
- [BankTransactions](https://developer.xero.com/documentation/api/accounting/banktransactions)
- [BankTransfers](https://developer.xero.com/documentation/api/accounting/banktransfers)
- [BrandingThemes](https://developer.xero.com/documentation/api/accounting/brandingthemes)
- [ContactGroups](https://developer.xero.com/documentation/api/accounting/contactgroups)
- [Contacts](https://developer.xero.com/documentation/api/accounting/contacts)
- [CreditNotes](https://developer.xero.com/documentation/api/accounting/creditnotes)
- [Currencies](https://developer.xero.com/documentation/api/accounting/currencies)
- [Employees](https://developer.xero.com/documentation/api/accounting/employees)
- [Invoices](https://developer.xero.com/documentation/api/accounting/invoices)
- [Items](https://developer.xero.com/documentation/api/accounting/items)
- [ManualJournals](https://developer.xero.com/documentation/api/accounting/manualjournals)
- [Organisation](https://developer.xero.com/documentation/api/accounting/organisation)
- [Overpayments](https://developer.xero.com/documentation/api/accounting/overpayments)
- [Payments](https://developer.xero.com/documentation/api/accounting/payments)
- [Prepayments](https://developer.xero.com/documentation/api/accounting/prepayments)
- [PurchaseOrders](https://developer.xero.com/documentation/api/accounting/purchaseorders)
- [RepeatingInvoices](https://developer.xero.com/documentation/api/accounting/repeatinginvoices)
- [TaxRates](https://developer.xero.com/documentation/api/accounting/taxrates)
- [TrackingCategories](https://developer.xero.com/documentation/api/accounting/trackingcategories)
- [Users](https://developer.xero.com/documentation/api/accounting/users)

### Dates transformation

As Xero uses .NET, some date fields in records could be in [.NET JSON date format](https://developer.xero.com/documentation/api/accounting/requests-and-responses) which look like `/Date(1419937200000+0000)/`. The connector automatically detects and transforms these dates into ISO 8601 format for consistency and easier data processing.

The connector also handles ISO 8601 formatted dates and ensures all datetime fields use a consistent format with UTC timezone.

### Incremental Sync

This connector supports incremental sync for all streams. The connector uses the `UpdatedDateUTC` field as the cursor field to track which records to sync incrementally. During the first sync, the connector will fetch all data from the start date you specify. In subsequent syncs, it will only fetch records that have been updated since the last sync.

### Error Handling

The connector implements automatic handling for common API errors:
- **401 Unauthorized**: The connector will attempt to refresh the access token and retry the request.
- **403 Forbidden**: The connector will log the error and skip the affected record.
- **429 Rate Limit Exceeded**: The connector will respect the Retry-After header and automatically retry after waiting the specified time.

### Performance considerations

The connector is restricted by Xero [API rate limits](https://developer.xero.com/documentation/guides/oauth2/limits/#api-rate-limits):

- **Concurrent Limit**: 5 calls in progress at one time
- **Minute Limit**: 60 calls per minute per tenant
- **Daily Limit**: 5000 calls per day per tenant
- **App Minute Limit**: 10,000 calls per minute across all tenants

When rate limits are exceeded, the API returns a 429 HTTP status code with a Retry-After header indicating how many seconds to wait before retrying.

### Pagination

The connector automatically handles pagination for all streams, using a page size of 100 records per request.

## Migration Guide

If you are upgrading from a previous version of the connector, please refer to the [migration guide](./xero-migrations.md) for important information about changes between versions.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                   |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------|
| 2.1.4 | 2025-03-01 | [55142](https://github.com/airbytehq/airbyte/pull/55142) | Update dependencies |
| 2.1.3 | 2025-02-22 | [54526](https://github.com/airbytehq/airbyte/pull/54526) | Update dependencies |
| 2.1.2 | 2025-02-15 | [54042](https://github.com/airbytehq/airbyte/pull/54042) | Update dependencies |
| 2.1.1 | 2025-02-08 | [43841](https://github.com/airbytehq/airbyte/pull/43841) | Update dependencies |
| 2.1.0 | 2024-10-23 | [47264](https://github.com/airbytehq/airbyte/pull/47264) | Migrate to Manifest-only |
| 2.0.1 | 2025-01-10 | [51034](https://github.com/airbytehq/airbyte/pull/51034) | Fix for time part being removed from all datetimes fields |
| 2.0.0 | 2024-06-06 | [39316](https://github.com/airbytehq/airbyte/pull/39316) | Add OAuth and Bearer strategies |
| 1.0.1 | 2024-06-06 | [39264](https://github.com/airbytehq/airbyte/pull/39264) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.0 | 2024-04-30 | [36878](https://github.com/airbytehq/airbyte/pull/36878) | Migrate to low code |
| 0.2.6 | 2024-05-17 | [38330](https://github.com/airbytehq/airbyte/pull/38330) | Updating python dependencies |
| 0.2.5 | 2024-01-11 | [34154](https://github.com/airbytehq/airbyte/pull/34154) | prepare for airbyte-lib |
| 0.2.4 | 2023-11-24 | [32837](https://github.com/airbytehq/airbyte/pull/32837) | Handle 403 error |
| 0.2.3 | 2023-06-19 | [27471](https://github.com/airbytehq/airbyte/pull/27471) | Update CDK to 0.40 |
| 0.2.2 | 2023-06-06 | [27007](https://github.com/airbytehq/airbyte/pull/27007) | Update CDK |
| 0.2.1 | 2023-03-20 | [24217](https://github.com/airbytehq/airbyte/pull/24217) | Certify to Beta |
| 0.2.0 | 2023-03-14 | [24005](https://github.com/airbytehq/airbyte/pull/24005) | Enable in Cloud |
| 0.1.0 | 2021-11-11 | [18666](https://github.com/airbytehq/airbyte/pull/18666) | 🎉 New Source - Xero [python cdk] |

</details>
