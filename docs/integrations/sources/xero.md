# Xero

This page contains the setup guide and reference information for the Xero source connector.

## Prerequisites

- Tenant ID
- Start Date

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

<!-- env:cloud -->

**For Airbyte Cloud:**

- OAuth 2.0
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

There is two currently supported ways to authenticate with Xero:

For the bearer token strategy, please follow [instruction](https://developer.xero.com/documentation/guides/oauth2/pkce-flow/) to obtain all requirements:
- Client ID

For the OAuth client credentials, please follow [instructions](https://developer.xero.com/documentation/guides/oauth2/custom-connections) to obtain all requirements:
- Client ID
- Client Secret

<!-- /env:oss -->

## Setup guide

### Step 1: Set up Xero

<!-- env:cloud -->

### Step 2: Set up the Xero connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Xero** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your Xero account`.
5. Log in and `Allow access`.
6. **Tenant ID** - Enter your Xero Organisation's [Tenant ID](https://developer.xero.com/documentation/guides/oauth2/auth-flow/#xero-tenants)
7. **Start Date** - UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ` from which you'd like to replicate data.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Create an application in [Xero development center](https://developer.xero.com/app/manage/).

For the client credentials, make sure you set the list of scopes mentioned above.

You can optionally use postman to generate the required `access_token` needed for the source setup.

<!-- /env:oss -->

## Supported sync modes

The Xero source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

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

As Xero uses .NET, some date fields in records could be in [.NET JSON date format](https://developer.xero.com/documentation/api/accounting/requests-and-responses). These dates are transformed into ISO 8601.

### Performance considerations

The connector is restricted by Xero [API rate limits](https://developer.xero.com/documentation/guides/oauth2/limits/#api-rate-limits).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                   |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------|
| 2.0.1   | 2025-01-10 | [51034](https://github.com/airbytehq/airbyte/pull/51034) | Fix for time part being removed from all datetimes fields |
| 2.0.0   | 2024-06-06 | [39316](https://github.com/airbytehq/airbyte/pull/39316) | Add OAuth and Bearer strategies                           |
| 1.0.1   | 2024-06-06 | [39264](https://github.com/airbytehq/airbyte/pull/39264) | [autopull] Upgrade base image to v1.2.2                   |
| 1.0.0   | 2024-04-30 | [36878](https://github.com/airbytehq/airbyte/pull/36878) | Migrate to low code                                       |
| 0.2.6   | 2024-05-17 | [38330](https://github.com/airbytehq/airbyte/pull/38330) | Updating python dependencies                              |
| 0.2.5   | 2024-01-11 | [34154](https://github.com/airbytehq/airbyte/pull/34154) | prepare for airbyte-lib                                   |
| 0.2.4   | 2023-11-24 | [32837](https://github.com/airbytehq/airbyte/pull/32837) | Handle 403 error                                          |
| 0.2.3   | 2023-06-19 | [27471](https://github.com/airbytehq/airbyte/pull/27471) | Update CDK to 0.40                                        |
| 0.2.2   | 2023-06-06 | [27007](https://github.com/airbytehq/airbyte/pull/27007) | Update CDK                                                |
| 0.2.1   | 2023-03-20 | [24217](https://github.com/airbytehq/airbyte/pull/24217) | Certify to Beta                                           |
| 0.2.0   | 2023-03-14 | [24005](https://github.com/airbytehq/airbyte/pull/24005) | Enable in Cloud                                           |
| 0.1.0   | 2021-11-11 | [18666](https://github.com/airbytehq/airbyte/pull/18666) | 🎉 New Source - Xero [python cdk]                         |

</details>
