# Oracle NetSuite

NetSuite is Oracle's cloud business management suite, covering ERP and financials, CRM, and ecommerce.

This connector reads NetSuite record types through [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html). It discovers streams at runtime from the account's record metadata catalog, so the streams you see depend on the record types the connector's role can read.

## Prerequisites

- An Oracle NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US) with administrator access, so you can enable features and create integrations, roles, and access tokens.
- Token-based authentication credentials: realm (account ID), consumer key, consumer secret, token ID, and token secret.

The connector authenticates with [token-based authentication](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4247337262.html) (OAuth 1.0a, HMAC-SHA256). It doesn't support OAuth 2.0. Oracle has announced that as of NetSuite 2027.1 you can't create new token-based authentication integrations, although existing integrations keep working. See [Preparing for Token-based Authentication (TBA) End of Support](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_0525020842.html).

## Setup guide

### Step 1: Create NetSuite account

1. Create [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US) on Oracle NetSuite
2. Confirm your Email

### Step 2: Setup NetSuite account

#### Step 2.1: Obtain Realm info

1. Login into your NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
2. Go to **Setup** » **Company** » **Company Information**
3. Copy your Account ID (Realm). It should look like **1234567** for the `Production` env. or **1234567_SB2** - for a `Sandbox`

#### Step 2.2: Enable features

1. Go to **Setup** » **Company** » **Enable Features**
2. Click on **SuiteCloud** tab
3. Scroll down to **SuiteScript** section
4. Enable checkbox for `CLIENT SUITESCRIPT` and `SERVER SUITESCRIPT`
5. Scroll down to **Manage Authentication** section
6. Enable checkbox `TOKEN-BASED AUTHENTICATION`
7. Scroll down to **SuiteTalk (Web Services)**
8. Enable checkbox `REST WEB SERVICES`
9. Save the changes

#### Step 2.3: Create Integration (obtain Consumer Key and Consumer Secret)

1. Go to **Setup** » **Integration** » **Manage Integrations** » **New**
2. Fill the **Name** field (we recommend to put `airbyte-rest-integration` for a name)
3. Make sure the **State** is `enabled`
4. Enable checkbox `Token-Based Authentication` in **Authentication** section
5. Save changes
6. After that, **Consumer Key** and **Consumer Secret** will be showed once (copy them to the safe place)

#### Step 2.4: Setup Role

1. Go to **Setup** » **Users/Roles** » **Manage Roles** » **New**
2. Fill the **Name** field (we recommend to put `airbyte-integration-role` for a name)
3. Scroll down to **Permissions** tab
4. Click on **Setup** and add both `REST Web Services` and `Log in using Access Tokens`. REST web services rejects every request from a role that lacks these two permissions, whatever else the role can read. See [Prerequisites and Setup for REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_5085602973.html).
5. On the same **Setup** subtab, add the remaining dropdown entities with either `full` or `view` access level.
6. Click on **Transactions** and add all the dropdown entities with either `full` or `view` access level.
7. Click on **Reports** and add all the dropdown entities with either `full` or `view` access level.
8. Click on **Lists** and add all the dropdown entities with either `full` or `view` access level.

The connector only exposes record types this role can read. It logs a warning and skips any record type that returns an `INSUFFICIENT_PERMISSION` error, so a narrower role means fewer streams rather than a failed sync. Revisit these permissions when you rename or customize a record type in NetSuite.

#### Step 2.5: Setup User

1. Go to **Setup** » **Users/Roles** » **Manage Users**
2. In column `Name` click on the user’s name you want to give access to the `airbyte-integration-role`
3. Then click on **Edit** button under the user’s name
4. Scroll down to **Access** tab at the bottom
5. Select from dropdown list the `airbyte-integration-role` role which you created in step 2.4
6. Save changes

#### Step 2.6: Create Access Token for role

1. Go to **Setup** » **Users/Roles** » **Access Tokens** » **New**
2. Select an **Application Name**
3. Under **User** select the user you assigned the `airbyte-integration-role` in the step **2.4**
4. Inside **Role** select the one you gave to the user in the step **2.5**
5. Under **Token Name** you can give a descriptive name to the Token you are creating (we recommend to put `airbyte-rest-integration-token` for a name)
6. Save changes
7. After that, **Token ID** and **Token Secret** will be showed once (copy them to the safe place)

#### Step 2.7: Summary

You have copied next parameters

- Realm (Account ID)
- Consumer Key
- Consumer Secret
- Token ID
- Token Secret
  Also you have properly **Configured Account** with **Correct Permissions** and **Access Token** for User and Role you've created early.

### Step 3: Set up the source connector in Airbyte

1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
2. On the source setup page, select **NetSuite** from the Source type dropdown and enter a name for this connector.
3. Enter your **Realm (Account Id)**, **Consumer Key**, **Consumer Secret**, **Token Key (Token Id)**, and **Token Secret**.
4. Enter a **Start Date** as `YYYY-MM-DDTHH:mm:ssZ`, for example `2017-01-25T00:00:00Z`. Incremental streams read from this point on their first sync.
5. Optionally set **Object Types** to the API names of the record types you want, such as `customer` or `salesorder`. Leave it empty to sync every record type the role can read.
6. Optionally set **Window in Days**. The default is 30.
7. Click **Set up source**.

### Object Types

When **Object Types** is empty, the connector lists the account's whole metadata catalog and fetches a schema for every record type in it. Large accounts can expose hundreds of record types, and each one costs a schema request during discovery. Naming the record types you actually need keeps setup and schema refreshes short.

Use the API name of the record type, in lowercase, as it appears in the [REST API browser](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html), not the label shown in the NetSuite UI. Setup fails with a `Duplicate record type` message if the same name appears twice in the list.

### Window in Days

**Window in Days** controls how many days of history each incremental request covers. The connector walks from the cursor date to today in windows of this size, so a smaller window means more requests, each returning fewer records. Lower it if a stream holds a lot of changes per day and requests time out or return too much data at once. NetSuite [times out any request that runs longer than 15 minutes](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/subsect_1559222360.html).

## Supported sync modes

The NetSuite source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

The connector generates one stream per record type, so the stream list depends on the account rather than on a fixed catalog. Two things determine what you get:

- The record types the token's role can read. See **Setup guide** » **Step 2.4** and **Step 2.5**.
- The **Object Types** field, if you set it.

Schemas come from the account's metadata catalog, which means custom fields and customized record types are included. Every field is typed as nullable because NetSuite schemas don't declare nullability. If a record type's schema comes back without a `properties` key three times in a row, the connector logs a warning and skips that stream.

Sync mode support is per stream and depends on the record type's own fields:

| Record type has | Cursor field | Sync modes |
| --------------- | ------------ | ---------- |
| `lastModifiedDate` | `lastModifiedDate` | Full refresh, incremental |
| `lastmodified` (typical of custom records) | `lastmodified` | Full refresh, incremental |
| Neither field | None | Full refresh only |

### How incremental syncs work

NetSuite can't sort records in a response, so the connector filters each request to a date range instead of paging through an ordered result set. Two consequences are worth knowing before you plan downstream pipelines:

- **Incremental syncs are accurate to the day, not to the second.** NetSuite's record query filter accepts bare dates only, and it resolves them in the account's own time zone. To avoid missing records on accounts behind UTC, the connector opens each sync's first window 12 hours before the stored cursor and then truncates to a date. Expect a sync to re-request records it has already read near the cursor. Records older than the cursor are dropped before they're emitted, so this overlap doesn't duplicate data.
- **The connector detects your account's date format.** NetSuite expects date literals in the format the account prefers. The connector tries `MM/DD/YYYY`, `YYYY-MM-DD`, `DD/MM/YYYY`, and `DD.MM.YYYY` in that order, and reissues the same request under the next format when NetSuite rejects one. You don't need to configure this, but the first sync of a stream logs a warning for each rejected format.

## Performance considerations

The connector reads each record individually: it lists record IDs for a date window, then requests each record with `expandSubResources=true` to get its sublists. A sync therefore costs roughly one API call per record, plus one call per page of IDs. Streams with many records are slow for that reason, not because of rate limiting.

NetSuite governs REST concurrency at the account level, and that limit is shared with SOAP web services and RESTlets. Syncing several NetSuite streams or connections at once competes with your other integrations for the same threads. See [Web Services and RESTlet Concurrency Governance](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_1500275531.html).

## Troubleshooting

### A record type is missing from the stream list

The connector skips record types it can't read or describe. Check the sync logs for the record type's name:

- `INSUFFICIENT_PERMISSION`: the token's role lacks access to that record type. Add it under **Setup** » **Users/Roles** » **Manage Roles**, then refresh the schema.
- `USER_ERROR`: the record type is readable by administrators only.
- `schema is not available`: the metadata catalog returned no fields for that record type after three attempts. Retry discovery later.

If you set **Object Types**, only those record types are considered, so remove the field or add the record type to the list.

### Setup fails right after you enter credentials

The connection check reads a single record. With **Object Types** set, it reads the first record type in your list; otherwise it reads `contact`. A failure here usually means the role is missing the `REST Web Services` or `Log in using Access Tokens` permission, the realm doesn't match the account, or the token belongs to a different user or role than the one you granted access to.

Use the realm exactly as NetSuite shows it, for example `1234567` for production or `1234567_SB2` for a sandbox. Sandbox refreshes invalidate tokens, so create new ones after each refresh.

### Incremental syncs re-read the same records

This is expected. See [How incremental syncs work](#how-incremental-syncs-work).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                   |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------|
| 0.1.28 | 2026-08-20 | [79654](https://github.com/airbytehq/airbyte/pull/79654) | Fix incremental sync permanently dropping records modified between the sync time and account-local midnight; retry a rejected date format on the same slice instead of skipping it |
| 0.1.27 | 2025-10-14 | [67787](https://github.com/airbytehq/airbyte/pull/67787) | Update dependencies |
| 0.1.26 | 2025-10-07 | [67429](https://github.com/airbytehq/airbyte/pull/67429) | Update dependencies |
| 0.1.25 | 2025-09-30 | [66934](https://github.com/airbytehq/airbyte/pull/66934) | Update dependencies |
| 0.1.24 | 2025-09-24 | [66623](https://github.com/airbytehq/airbyte/pull/66623) | Update dependencies |
| 0.1.23 | 2025-09-09 | [65813](https://github.com/airbytehq/airbyte/pull/65813) | Update dependencies |
| 0.1.22 | 2025-08-23 | [65215](https://github.com/airbytehq/airbyte/pull/65215) | Update dependencies |
| 0.1.21 | 2025-08-16 | [61055](https://github.com/airbytehq/airbyte/pull/61055) | Update dependencies |
| 0.1.20 | 2025-08-12 | [63698](https://github.com/airbytehq/airbyte/pull/63698) | Add support for german date format in NetSuite input |
| 0.1.19 | 2025-05-24 | [60581](https://github.com/airbytehq/airbyte/pull/60581) | Update dependencies |
| 0.1.18 | 2025-05-10 | [60086](https://github.com/airbytehq/airbyte/pull/60086) | Update dependencies |
| 0.1.17 | 2025-05-03 | [59481](https://github.com/airbytehq/airbyte/pull/59481) | Update dependencies |
| 0.1.16 | 2025-04-27 | [59091](https://github.com/airbytehq/airbyte/pull/59091) | Update dependencies |
| 0.1.15 | 2025-04-19 | [58531](https://github.com/airbytehq/airbyte/pull/58531) | Update dependencies |
| 0.1.14 | 2025-04-12 | [57860](https://github.com/airbytehq/airbyte/pull/57860) | Update dependencies |
| 0.1.13 | 2025-04-05 | [57301](https://github.com/airbytehq/airbyte/pull/57301) | Update dependencies |
| 0.1.12 | 2025-03-29 | [56692](https://github.com/airbytehq/airbyte/pull/56692) | Update dependencies |
| 0.1.11 | 2025-03-22 | [56060](https://github.com/airbytehq/airbyte/pull/56060) | Update dependencies |
| 0.1.10 | 2025-03-08 | [55455](https://github.com/airbytehq/airbyte/pull/55455) | Update dependencies |
| 0.1.9 | 2025-03-05 | [55207](https://github.com/airbytehq/airbyte/pull/55207) | Add support for additional date format in Netsuite input |
| 0.1.8 | 2025-03-01 | [54821](https://github.com/airbytehq/airbyte/pull/54821) | Update dependencies |
| 0.1.7 | 2025-02-22 | [54363](https://github.com/airbytehq/airbyte/pull/54363) | Update dependencies |
| 0.1.6 | 2025-02-15 | [53853](https://github.com/airbytehq/airbyte/pull/53853) | Update dependencies |
| 0.1.5 | 2025-02-08 | [53243](https://github.com/airbytehq/airbyte/pull/53243) | Update dependencies |
| 0.1.4 | 2024-07-29 | [42857](https://github.com/airbytehq/airbyte/pull/42857) | Migrate connector to Poetry |
| 0.1.3 | 2023-01-20 | [21645](https://github.com/airbytehq/airbyte/pull/21645) | Minor issues fix, Setup Guide corrections for public docs |
| 0.1.1 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state |
| 0.1.0 | 2022-09-15 | [16093](https://github.com/airbytehq/airbyte/pull/16093) | Initial Alpha release |

</details>
