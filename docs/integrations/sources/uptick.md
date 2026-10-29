# Uptick

Extract data from Uptick, a field service management platform designed for the fire protection industry.

## Prerequisites

- Your Uptick workspace URL, in the form `https://<workspace>.onuptick.com`. The connector only connects to `onuptick.com` workspace hosts. A Base URL on any other host fails the connection check for both authentication methods.
- Credentials for one of the two authentication methods below. OAuth 2.0 is recommended; the username and password method remains available for existing connections.

### OAuth 2.0 (recommended)

This method uses the OAuth 2.0 authorization-code flow with PKCE, and the connector requests only Uptick's read-only `read` scope. Enter the **Base URL** exactly as `https://<workspace>.onuptick.com`, in lowercase and without a path.

On Airbyte Cloud, the **Authenticate with Uptick** button uses Airbyte's Uptick app, so the Airbyte app must be enabled in your Uptick account before you authenticate. If it isn't enabled, ask your Uptick administrator to enable it. Then enter your **Base URL**, choose **Authenticate with Uptick** under **Authentication**, click **Authenticate**, and approve the consent page that Uptick shows. The connector stores the resulting tokens in your connection's `credentials` block.

On self-hosted Airbyte (OSS), first create an OAuth application in Uptick under **Control Panel > Uptick API > Create Application** with your Airbyte instance's redirect URI `https://<airbyte-host>/auth_flow`, using the authorization-code grant with PKCE (S256). Then enter your Base URL, choose **Authenticate with Uptick**, and complete the flow.

### Username & password

The connector authenticates with the Uptick API using OAuth 2.0 with the password grant, so you need both an OAuth application and an Uptick user account:

- An OAuth Client ID and Client Secret generated from your Uptick instance.
- The email address and password of an Uptick user account. The connector signs in as this user, so the account must have permission to view every resource you want to sync.

To generate the OAuth credentials, go to **Control Panel > Uptick API** in your Uptick instance, select **Create Application**, provide a name, and save. Uptick generates the Client ID and Client Secret for you. For step-by-step instructions, see [Uptick API - Getting started](https://support.uptickhq.com/en/articles/6728442-uptick-api-getting-started). Existing connections that use the top-level `client_id`, `client_secret`, `username`, and `password` fields continue to work; on the first run after upgrading to 2.1.0, the connector copies them under Authentication (`credentials`) and saves the migrated config — the original fields are kept, so pinning back to 2.0.x keeps working.

The Uptick user account needs read access to each module you want to sync; in practice `task_profitability` has required the Intelligence reports permission.

## Setup guide

### Set up the Uptick source in Airbyte

1. In Airbyte, go to **Sources** and select **+ New source**.
2. Search for and select **Uptick** as the source type.
3. Enter your **Base URL** and choose an **Authentication** method, then fill in the fields from the configuration table below. For **Authenticate with Uptick**, click **Authenticate** and approve the consent page; for **Username & password**, fill in `client_id`, `client_secret`, `username`, and `password`. Consider creating a dedicated Uptick service user for the connector: the API token inherits that user's permissions, so a service user keeps access scoped to exactly what you sync.
4. Select **Set up source** to test the connection.

| Input | Type | Description | Default Value |
| ------- | ------ | ------------- | --------------- |
| `base_url` | `string` | Root URL of your Uptick workspace, for example `https://yourcompany.onuptick.com`. Required for both authentication methods. The connector strips any scheme, path, or trailing slash and always connects over HTTPS. The host must be `<workspace>.onuptick.com`, or the connection check fails. For **Authenticate with Uptick**, enter the host in lowercase. | |
| `credentials.auth_type` | `string` | `oauth2.0` for the OAuth flow, `password` for the legacy username and password method. | |
| `credentials.client_id` | `string` | OAuth Client ID generated from **Control Panel > Uptick API**. Filled automatically by the OAuth flow on Airbyte Cloud. | |
| `credentials.client_secret` | `string` | OAuth Client Secret generated from **Control Panel > Uptick API**. Filled automatically by the OAuth flow on Airbyte Cloud. | |
| `credentials.refresh_token` | `string` | Refresh token obtained by authenticating with Uptick. Required for `oauth2.0`; filled automatically by the OAuth flow. | |
| `credentials.username` | `string` | Email address for an Uptick user account with API access. Required for `password`. Synced data is limited to what this user can see in Uptick. | |
| `credentials.password` | `string` | Password for the Uptick user account. Required for `password`. | |
| `num_workers` | `integer` | Number of concurrent requests. Higher values speed up syncs but increase the chance of Uptick rate limiting. Allowed range 1–10. | `3` |
| `max_requests_per_minute` | `integer` | Global request budget shared by all streams and threads. Uptick publishes no numeric limit; 60 is a conservative default. Allowed range 1–600. | `60` |

## Supported sync modes

| Sync mode | Supported |
| --------- | --------- |
| Full Refresh Sync | ✅ |
| Incremental Sync | ✅ |

Every stream except `majorservices` supports both full refresh and incremental sync on the `updated` cursor; `majorservices` has no `updated` timestamp and is full refresh only. Among the JSON:API streams, only those marked ✅ in the **Reports deletions** column below expose a `deleted` timestamp; on the streams marked ❌ there, an incremental sync retains rows in your destination after they're deleted in Uptick, so use full refresh for those. `task_profitability` is a generated report with no deleted state and is safe to sync incrementally.

## Supported Streams

The Uptick connector syncs data from the following streams, organized by functional area:

### Core business entities

- `tasks` - Work tasks and maintenance requests with scheduling, priority, and assignment details
- `taskcategories` - Categories for organizing tasks
- `tasksessions` - Time tracking entries for work performed on tasks
- `rounds` - Work rounds for technician scheduling and route management
- `projects` - Project management entities for larger initiatives
- `clients` - Customer organizations and contact information
- `clientgroups` - Client organization groupings
- `clientcontacts` - Contact people associated with clients
- `properties` - Physical locations where work is performed
- `propertycontacts` - Contact people associated with properties
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
- `majorservices` - Major service records for assets
- `servicetasks` - Individual work activities on tasks
- `subtasks` - Links programme maintenance routines to tasks
- `remarks` - Issues, defects, and observations during inspections
- `remarkevents` - Events and actions taken on remarks
- `promptquestions` - Prompt questions asked during service report completion
- `promptanswergroups` - Groupings of prompt answers per service task and section
- `promptanswers` - Individual answers to prompt questions
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

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental | Reports deletions |
| ------------- | ------------- | ------------ | --------------------- | ---------------------- | ------------------- |
| `tasks` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `taskcategories` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `clients` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `clientgroups` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `properties` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `invoices` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `projects` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `servicequotes` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `defectquotes` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `suppliers` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `purchaseorders` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `purchaseorderlineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `assets` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `routines` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `billingcards` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `purchaseorderbills` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `purchaseorderbilllineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `purchaseorderdockets` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `invoicelineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `users` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `servicegroups` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `costcentres` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `accreditationtypes` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `accreditations` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `branches` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `creditnotes` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `creditnotelineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `remarks` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `assettypes` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `assettypevariants` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `products` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `rounds` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `tasksessions` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `contractors` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `appointments` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `billingcontracts` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `billingcontractlineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `defectquotelineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `servicequotefixedlineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `servicequotedoandchargelineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `servicequoteproductlineitems` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `remarkevents` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `routineservices` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `routineservicelevels` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `routineservicetypes` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `routineserviceleveltypes` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `servicetasks` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `subtasks` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `task_profitability` | `task_id` | `DefaultPaginator` | ✅ | ✅ | n/a (generated report) |
| `clientcontacts` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `propertycontacts` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `promptquestions` | `id` | `DefaultPaginator` | ✅ | ✅ | ✅ |
| `promptanswergroups` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `promptanswers` | `id` | `DefaultPaginator` | ✅ | ✅ | ❌ |
| `majorservices` | `id` | `DefaultPaginator` | ✅ | ❌ (no `updated` timestamp) | n/a (full refresh only) |

### API version and fields

Every stream except `task_profitability` reads a pinned Uptick endpoint under `/api/v2.16/`. The `task_profitability` stream reads the intelligence report at `/api/v2/intelligencereports/profitability_by_task/`, which resolves to whichever minor version Uptick currently treats as the latest.

Each stream requests a fixed list of fields using Uptick's sparse fieldsets, so a stream carries a curated subset of what the endpoint can return rather than every field. Fields that Uptick adds later show up only after the connector is updated. Uptick keeps roughly three minor API versions live at a time and retires the oldest, so connector releases that move to a newer minor version can add, rename, or remove fields. The [Uptick API patch notes](https://support.uptickhq.com/en/articles/6728314-uptick-api-overview-and-patch-notes) list what changed in each version.

### Attribute values

Uptick returns each record as a JSON:API object with an `attributes` block. The connector copies every attribute to the top level of the record without changing its value, and also keeps the original `attributes` object, the `relationships` object, and the resource `type`. From version 2.1.2, every JSON:API stream declares `attributes` and `relationships` as nullable objects in its schema, and every one of those streams except `accreditationtypes`, `billingcontracts`, `billingcontractlineitems`, `products`, and `promptquestions` also declares `type`, so destinations that create typed columns add these columns. Monetary and other decimal fields arrive as strings with the precision Uptick sends, such as `"10.00"`. The exception is `servicequotes.product_subtotal`, which Uptick returns as a JSON number and the connector declares as a number from version 2.0.0. Attributes that Uptick returns as `null` land as `null` in your destination. Uptick returns an empty string (`""`) instead of `null` for unset email fields, such as `users.email` and `clients.contact_email`, and for `tasks.workorder_url`, so filter on both values when you look for missing emails or URLs.

Before version 1.2.0, the connector re-rendered each attribute through a template, which reformatted decimal strings (`"10.00"` became `"10.0"`) and turned `null` into the string `"None"`. If you filter or join on those fields downstream, check for both representations in data synced before you upgraded.

### Relationship fields

Uptick returns related records in a JSON:API `relationships` object. The connector flattens each relationship into a scalar `<relationship>_id` column, such as `client_id` on `clientcontacts` or `property_id` on `propertycontacts`. Use these columns to join streams in your destination.

Prompt data spans three streams, and Uptick reworked its prompt model in API v2.15, so those joins are worth spelling out:

- `promptanswers.answergroup_id` joins `promptanswergroups.id`, and `promptanswers.question_id` joins `promptquestions.id`.
- `promptanswergroups.servicetask_id` and `promptanswergroups.task_id` tie a group of answers back to the service task or task the answers were recorded against.
- `promptquestions.section_id` and `promptanswergroups.section_id` reference Uptick prompt sections. The connector doesn't sync prompt sections, so you can't resolve these IDs to section names from synced data alone.

### Incremental sync

For streams that support incremental sync, the connector uses each record's `updated` timestamp as the cursor and fetches only records changed since the last sync through the Uptick API's `updatedsince` filter. Streams that support only full refresh are re-read in full on every sync.

Before version 2.0.0, the `servicegroups` and `accreditationtypes` endpoints ignored the `updatedsince` filter, so the connector read both tables in full on every sync and filtered on the cursor itself. Uptick now applies the filter on these endpoints, and from version 2.0.0 incremental syncs of these streams fetch only changed rows.

The `majorservices` endpoint has no `updated` timestamp, so there is no cursor to sync from. From version 2.0.0 the connector offers this stream in full refresh mode only.

Airbyte still offers incremental sync in the UI for the streams marked ❌ under **Reports deletions**, because the connector defines the `updated` cursor for every stream except `majorservices`. Avoid it for those streams: their Uptick endpoints don't report deletions, so an incremental sync keeps records in your destination after they're deleted in Uptick. Sync them with **Full Refresh | Overwrite** instead.

## Data type map

| Connector schema type | Airbyte type |
| --------------------- | ------------ |
| string | string |
| integer | integer |
| number | number |
| decimal | string (airbyte_type `decimal`) |
| boolean | boolean |
| date | string (format `date`) |
| datetime | string (format `date-time`, airbyte_type `timestamp_with_timezone`) |
| object | object |
| array | array |

## Limitations & Troubleshooting

### Permission errors (403)

If the Uptick user account lacks permission for an endpoint, the sync fails with `HTTP 403: Uptick user lacks permission for the requested endpoint.` Uptick doesn't publish a per-endpoint permission list; in production this has been seen on `task_profitability` (resolved by granting the Intelligence reports permission) and on `billingcontractlineitems`. The connector fails with a configuration error instead of retrying. Grant the missing module permission in Uptick or deselect the stream.

**`403 Access denied … required licenses (FIELD, DESK, CONTRACTOR)` after logging in during "Authenticate with Uptick".** The Uptick user you signed in with has no licence in that workspace. Ask your Uptick administrator to grant one (for example, DESK), or use username/password authentication instead.

### Authentication errors

Uptick rejects a wrong username or password with `invalid_grant`, and a wrong client ID or client secret with `invalid_client`. The connector reports these as a configuration error without retrying: `Refresh token was rejected by the OAuth provider (invalid, expired, or already used). Re-authenticate this source's credentials in its connection settings. Provider error: invalid_grant` (or `invalid_client`). For connections that use **Authenticate with Uptick**, re-authenticate so the stored tokens are refreshed. For username and password connections, check the four credential fields in the source configuration, and confirm that the OAuth application still exists under **Control Panel > Uptick API**.

Uptick access tokens can also expire or be revoked during a long sync. If a stream request returns 401 mid-sync, the connector refreshes the token once and retries the request; if the refresh is rejected (for example because the password changed during the sync) the sync fails with the same configuration error, and if the retried request is still 401 it fails with the configuration error `Refreshed OAuth access token is rejected by the API.` Update the credentials and run the sync again.

### Base URL errors

From version 2.1.2, the connection check rejects a Base URL whose host isn't `<workspace>.onuptick.com` before it sends any request, for both authentication methods. The check fails with a `JSON schema validation error` that says the URL `does not match` the `onuptick.com` pattern. Earlier versions didn't restrict the host for **Username & password**, so connections that use that method with another host, such as a tunnel or `localhost`, now fail. Set the Base URL to your `https://<workspace>.onuptick.com` address.

For **Authenticate with Uptick**, the host is also case-sensitive. A Base URL with uppercase letters, such as `https://MyCompany.onuptick.com`, fails the check with a message that contains `base_url-must-be-https-workspace.onuptick.com`, and the connector doesn't send your OAuth credentials to that host. Enter the host in lowercase.

A misspelled workspace name, such as `https://typo.onuptick.com`, passes this check but fails with a DNS or connection error.

### Deleted records

Streams marked ❌ under **Reports deletions** in the table above don't report deletions, so records deleted in Uptick stay in your destination until you run a **Full Refresh | Overwrite** sync (Full Refresh | Append doesn't remove rows). The 12 JSON:API streams marked ✅ there expose a `deleted` timestamp on deleted records; `task_profitability` is a generated report and has no deleted state.

### Rate limits

Uptick enforces rate limits and reasonable-use guidelines on its API but doesn't publish a numeric limit. Uptick states that it can revoke API access without notice for applications that violate these limits, so raise the connector's request rate cautiously.

Every stream except `task_profitability` uses Uptick's cursor pagination and requests 1,000 records per page, so the number of requests a stream needs is roughly its record count divided by 1,000. At the default budget of 60 requests per minute, a sync reads up to about 60,000 records per minute across all streams.

Two settings control how fast the connector reads from Uptick:

- `max_requests_per_minute` sets a single request budget that all streams and threads share (allowed range 1–600). The default of 60 requests per minute is a conservative value that Airbyte chose, and it's the throughput ceiling for the whole sync. Large workspaces with millions of records can sync more slowly than they did before version 1.3.0. If Uptick confirms your workspace tolerates more traffic, raise this value. If Uptick returns HTTP 429 responses, lower it.
- `num_workers` sets how many requests run at the same time. The default is 3 and the maximum is 10. Because every request still counts against `max_requests_per_minute`, adding workers only speeds up a sync when slow API responses keep the connector from using its full per-minute budget.

When Uptick throttles a request and returns a `Retry-After` header, the connector waits the indicated time before retrying. If the header asks for a wait of 30 minutes or longer, the connector fails the stream with a rate-limit error instead of waiting. Without a `Retry-After` header, the connector backs off exponentially. The connector retries a failed request up to five times.

To reduce API usage, sync only the streams you need and schedule syncs no more often than your reporting requires.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------------- | -------------- | ---------------- |
| 2.1.4 | 2026-10-27 | [90093](https://github.com/airbytehq/airbyte/pull/90093) | Update dependencies |
| 2.1.3 | 2026-10-22 | [89668](https://github.com/airbytehq/airbyte/pull/89668) | Promote connector to certified support level. |
| 2.1.2 | 2026-10-22 | [89616](https://github.com/airbytehq/airbyte/pull/89616) | Request 1,000 records per page; declare `attributes`, `relationships`, `type`, `invoicelineitems.subtotal`, and `properties.address.place_id` in stream schemas; accept date-only cursor state; reject a Base URL outside `onuptick.com` on check; stop validating email fields and `tasks.workorder_url` as `email` and `uri` formats because Uptick returns `""` when they're unset; update the base image and vendor docs links |
| 2.1.1 | 2026-10-21 | [89505](https://github.com/airbytehq/airbyte/pull/89505) | Reject an empty or whitespace-only `base_url` and remove unused legacy config fields |
| 2.1.0 | 2026-10-20 | [87436](https://github.com/airbytehq/airbyte/pull/87436) | Add OAuth 2.0 authorization-code (PKCE) authentication with the read-only scope |
| 2.0.1 | 2026-10-20 | [89415](https://github.com/airbytehq/airbyte/pull/89415) | Update dependencies |
| 2.0.0 | 2026-10-16 | [88925](https://github.com/airbytehq/airbyte/pull/88925) | Upgrade the Uptick API to v2.16, correct the types of object and numeric fields, make majorservices full refresh only, filter servicegroups and accreditationtypes server-side, and add product_id to invoicelineitems |
| 1.3.3 | 2026-10-13 | [88821](https://github.com/airbytehq/airbyte/pull/88821) | Update dependencies |
| 1.3.2 | 2026-10-06 | [88063](https://github.com/airbytehq/airbyte/pull/88063) | Update dependencies |
| 1.3.1 | 2026-09-29 | [87373](https://github.com/airbytehq/airbyte/pull/87373) | Update dependencies |
| 1.3.0 | 2026-09-28 | [86356](https://github.com/airbytehq/airbyte/pull/86356) | Add a configurable request budget (default 60/min), refresh expired tokens mid-sync, and normalize base_url |
| 1.2.1 | 2026-09-22 | [86843](https://github.com/airbytehq/airbyte/pull/86843) | Update dependencies |
| 1.2.0 | 2026-09-21 | [86363](https://github.com/airbytehq/airbyte/pull/86363) | Emit attribute values verbatim and filter servicegroups and accreditationtypes incrementally |
| 1.1.3 | 2026-09-15 | [86280](https://github.com/airbytehq/airbyte/pull/86280) | Update dependencies |
| 1.1.2 | 2026-09-08 | [85702](https://github.com/airbytehq/airbyte/pull/85702) | Update dependencies |
| 1.1.1 | 2026-08-18 | [84790](https://github.com/airbytehq/airbyte/pull/84790) | Update dependencies |
| 1.1.0 | 2026-08-12 | [83710](https://github.com/airbytehq/airbyte/pull/83710) | Add 6 new streams (clientcontacts, propertycontacts, promptquestions, promptanswergroups, promptanswers, majorservices), add fields to the clients, properties, invoices, defectquotes, servicequotes, users, and purchaseorders streams, and make relationship field extraction null-safe |
| 1.0.3 | 2026-08-11 | [84162](https://github.com/airbytehq/airbyte/pull/84162) | Update dependencies |
| 1.0.2 | 2026-08-04 | [83652](https://github.com/airbytehq/airbyte/pull/83652) | Update dependencies |
| 1.0.1 | 2026-07-28 | [83098](https://github.com/airbytehq/airbyte/pull/83098) | Update dependencies |
| 1.0.0 | 2026-07-21 | [73740](https://github.com/airbytehq/airbyte/pull/73740) | Upgrade the Uptick API to v2.15 and remove deprecated fields from the branches, defectquotelineitems, servicetasks, and tasksessions streams |
| 0.5.16 | 2026-07-21 | [82628](https://github.com/airbytehq/airbyte/pull/82628) | Update dependencies |
| 0.5.15 | 2026-07-14 | [81991](https://github.com/airbytehq/airbyte/pull/81991) | Update dependencies |
| 0.5.14 | 2026-06-30 | [81268](https://github.com/airbytehq/airbyte/pull/81268) | Update dependencies |
| 0.5.13 | 2026-06-23 | [80682](https://github.com/airbytehq/airbyte/pull/80682) | Update dependencies |
| 0.5.12 | 2026-06-16 | [80076](https://github.com/airbytehq/airbyte/pull/80076) | Update dependencies |
| 0.5.11 | 2026-06-09 | [79539](https://github.com/airbytehq/airbyte/pull/79539) | Update dependencies |
| 0.5.10 | 2026-06-02 | [79025](https://github.com/airbytehq/airbyte/pull/79025) | Update dependencies |
| 0.5.9 | 2026-04-28 | [77504](https://github.com/airbytehq/airbyte/pull/77504) | Update dependencies |
| 0.5.8 | 2026-04-21 | [76809](https://github.com/airbytehq/airbyte/pull/76809) | Update dependencies |
| 0.5.7 | 2026-03-31 | [75703](https://github.com/airbytehq/airbyte/pull/75703) | Update dependencies |
| 0.5.6 | 2026-03-17 | [75044](https://github.com/airbytehq/airbyte/pull/75044) | Update dependencies |
| 0.5.5 | 2026-03-10 | [74493](https://github.com/airbytehq/airbyte/pull/74493) | Update dependencies |
| 0.5.4 | 2026-02-24 | [73926](https://github.com/airbytehq/airbyte/pull/73926) | Update dependencies |
| 0.5.3 | 2026-02-23 | [72302](https://github.com/airbytehq/airbyte/pull/72302) | Add fields to defectquotes and projects streams |
| 0.5.2 | 2026-02-17 | [73433](https://github.com/airbytehq/airbyte/pull/73433) | Update dependencies |
| 0.5.1 | 2026-02-10 | [73007](https://github.com/airbytehq/airbyte/pull/73007) | Update dependencies |
| 0.5.0 | 2026-01-22 | [71122](https://github.com/airbytehq/airbyte/pull/71122) | Add invoice_id to invoicelineitems, and add 6 new streams: servicetasks, routineservices, routineservicelevels, routineservicetypes, routineserviceleveltypes, subtasks |
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
