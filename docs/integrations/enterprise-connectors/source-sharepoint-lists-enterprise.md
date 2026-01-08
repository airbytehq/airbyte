---
dockerRepository: airbyte/source-sharepoint-lists-enterprise
enterprise-connector: true
---

# SharePoint Lists Enterprise

<HideInUI>

This page contains the setup guide and reference information for the [SharePoint Lists Enterprise](https://portal.azure.com) source connector.

</HideInUI>

The SharePoint Lists source connector allows you to sync data from Microsoft SharePoint Lists to your data warehouse or destination of choice. This connector uses the Microsoft Graph API to extract list data with full support for dynamic schema discovery, incremental syncs, and complex column types.

## Features

- **Dynamic List Discovery**: Automatically discovers all non-hidden lists in your SharePoint site
- **Dynamic Column Discovery**: Automatically detects and maps all column types for each list
- **Incremental Sync Support**: Efficiently syncs only new and modified records
- **Complex Column Type Support**: Handles Person/Group, Lookup, Managed Metadata, and Hyperlink columns
- **User Information Table**: Provides a lookup table for Author/Editor resolution

## Prerequisites

Before you begin, ensure you have:

1. **Azure AD app** with the following API permissions:
   - `Sites.Read.All` (Application permission)

2. **SharePoint Site ID** in the format: `hostname,site-guid,web-guid`
   - Example: `contoso.sharepoint.com,12345678-1234-1234-1234-123456789012,87654321-4321-4321-4321-210987654321`

3. **Azure AD credentials**:
   - Client ID (Application ID)
   - Client Secret
   - Tenant ID

## Setup guide

### Step 1: Set up SharePoint app

This connector requires an Azure AD application with **Application permissions** to access SharePoint data via the Microsoft Graph API.

To create and configure your Azure AD application:

1. [Register an application in Azure AD](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) and note the **Application (client) ID** and **Directory (tenant) ID**
2. [Create a client secret](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app#add-a-client-secret) and save the secret value
3. [Add the Microsoft Graph API permission](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-configure-app-access-web-apis#add-permissions-to-access-your-web-api) `Sites.Read.All` as an **Application permission** (not Delegated)
4. Grant admin consent for the permission

### Step 2: Get your SharePoint site ID

The Site ID is required to identify which SharePoint site to sync from. You can find it using Microsoft Graph Explorer:

1. Go to [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
2. Sign in with your Microsoft account
3. Run the following query: `GET https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{site-name}`
   - Replace `{hostname}` with your SharePoint hostname (for example, `contoso.sharepoint.com`)
   - Replace `{site-name}` with your site name
4. The response will contain the `id` field in the format: `hostname,site-guid,web-guid`

### Step 3: Set up the SharePoint Lists connector in Airbyte

1. Navigate to the Airbyte dashboard
2. Click **Sources** and then click **+ New source**
3. Search for **SharePoint Lists Enterprise** and select it
4. Enter a name for the connector
5. Enter your **Client ID** (Application ID from Azure AD)
6. Enter your **Client Secret**
7. Enter your **Tenant ID**
8. Enter your **Site ID** in the format: `hostname,site-guid,web-guid`
9. (Optional) Enter a **List Name Filter** regex pattern to filter which lists to sync
10. (Optional) Configure **Skip Document Libraries** (default: true)
11. (Optional) Set **Number of Workers** for parallel processing (default: 10, range: 1-20)
12. Click **Set up source**

## Configuration

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| `client_id` | Yes | Azure AD Application (client) ID |
| `client_secret` | Yes | Azure AD Application client secret |
| `tenant_id` | Yes | Azure AD Tenant ID |
| `site_id` | Yes | SharePoint Site ID in format: `hostname,site-guid,web-guid` |
| `list_name_filter` | No | Regular expression pattern to filter which lists to sync (for example, `Perdue.*` to match lists starting with "Perdue") |
| `skip_document_libraries` | No | Skip document library lists (default: `true`) |
| `num_workers` | No | Number of concurrent workers for parallel processing (default: `10`, range: 1-20) |

## Streams

### Static streams

#### `lists`

Metadata about all SharePoint lists in the site.

| Property | Type | Description |
| -------- | ---- | ----------- |
| `id` | string | Unique list identifier |
| `name` | string | Internal list name |
| `displayName` | string | Display name of the list |
| `description` | string | List description |
| `webUrl` | string | URL to the list |
| `createdDateTime` | string | ISO 8601 timestamp of creation |
| `lastModifiedDateTime` | string | ISO 8601 timestamp of last modification |
| `template` | string | List template type |
| `hidden` | boolean | Whether the list is hidden |

**Sync Mode**: Full Refresh, Incremental  
**Primary Key**: `id`  
**Cursor Field**: `lastModifiedDateTime`

#### `user_information`

Lookup table for SharePoint users (useful for resolving Author/Editor lookup IDs).

| Property | Type | Description |
| -------- | ---- | ----------- |
| `user_lookup_id` | string | User lookup ID (matches AuthorLookupId/EditorLookupId) |
| `user_title` | string | User display name |
| `user_email` | string | User email address |
| `user_login_name` | string | User login name |
| `is_site_admin` | boolean | Whether user is a site admin |
| `department` | string | User's department |
| `job_title` | string | User's job title |

**Sync Mode**: Full Refresh only  
**Primary Key**: `user_lookup_id`

### Dynamic streams (list items)

For each non-hidden SharePoint list discovered, the connector creates a dynamic stream. The stream name is derived from the list's display name (normalized to lowercase with underscores).

#### Standard fields (all list item streams)

| Property | Type | Description |
| -------- | ---- | ----------- |
| `_sharepoint_list_name` | string | Name of the source list |
| `_sharepoint_id` | string | Unique item ID within the list |
| `_sharepoint_deleted` | boolean | Whether the item is deleted |
| `_sharepoint_modified` | string | ISO 8601 timestamp of last modification |
| `_sharepoint_etag` | string | Entity tag for concurrency |
| `title` | string | Item title |
| `author` | string | Creator's display name |
| `authoremail` | string | Creator's email |
| `authorlookupid` | string | Creator's lookup ID |
| `editor` | string | Last modifier's display name |
| `editoremail` | string | Last modifier's email |
| `editorlookupid` | string | Last modifier's lookup ID |
| `created` | string | ISO 8601 timestamp of creation |
| `modified` | string | ISO 8601 timestamp of last modification |
| `version` | string | Item version |
| `contenttype` | string | Content type name |

**Plus**: All custom columns defined in the list (dynamically discovered)

**Sync Mode**: Full Refresh, Incremental  
**Primary Key**: `_sharepoint_id`  
**Cursor Field**: `_sharepoint_modified`

## Supported column types

The connector automatically handles the following SharePoint column types:

| SharePoint Type | Output Type | Notes |
| --------------- | ----------- | ----- |
| Text (Single/Multi-line) | string | |
| Number | number | |
| Currency | number | |
| Date and Time | string | ISO 8601 format |
| Yes/No | boolean | |
| Choice | string | Single or multi-select |
| Person or Group | string | Returns display name |
| Lookup | string | Returns display value from referenced list |
| Managed Metadata (Term) | string | Returns the term label |
| Hyperlink or Picture | string | URL stored in main field, description in `{field}_description` |
| Calculated | string | |
| Geolocation | object | |

### Complex column type handling

#### Person/Group columns

- Returns the user's display name as a string
- Multi-select person columns return semicolon-separated display names
- Use the `user_information` stream to get additional user details via `authorlookupid`/`editorlookupid`

#### Lookup columns

- Returns the display value from the referenced list
- Multi-value lookup columns return semicolon-separated values

#### Managed Metadata (Term) columns

- Returns the term label as a string
- Multi-value term columns return semicolon-separated labels

#### Hyperlink/Picture columns

- Main field contains the URL
- Additional `{fieldname}_description` field contains the link description

## Incremental sync behavior

### `lists` stream

- Uses client-side filtering based on `lastModifiedDateTime`
- Microsoft Graph API doesn't support server-side `$filter` on this endpoint
- All lists are fetched, but only those modified after the cursor are emitted

### List item streams

- Uses client-side filtering based on `lastModifiedDateTime`
- Only items modified after the stored cursor value are emitted
- Cursor is updated to the most recent `_sharepoint_modified` value

## Rate limiting and performance

- The connector respects Microsoft Graph API rate limits
- Default page size is determined by the API (typically 200 items per page)
- Use `num_workers` to control parallelization (higher values increase throughput but may hit rate limits)

## Known limitations

1. **12 Lookup Column Limit**: SharePoint limits the number of lookup-type columns (Person, Lookup, Managed Metadata) to 12 when listing multiple items. If a list has more than 12 lookup columns, some may not return values. The connector logs a warning when this is detected.

2. **Document Libraries**: By default, document libraries are skipped. Set `skip_document_libraries: false` to include them.

3. **Schema Changes**: New columns added to lists aren't automatically detected during syncs. A schema refresh is required to detect new columns or new lists.

4. **Deleted Items**: The connector doesn't currently support delta queries for detecting deleted items. Deleted items aren't synced.

## Troubleshooting

### Authentication errors

- Verify your Azure AD app has the required API permissions
- Ensure the client secret hasn't expired
- Check that the tenant ID is correct

### Site not found

- Verify the Site ID format: `hostname,site-guid,web-guid`
- Use Graph Explorer to validate your site ID: `GET https://graph.microsoft.com/v1.0/sites/{site_id}`

### Missing columns

- Refresh the schema in Airbyte to detect new columns
- Check if the list has more than 12 lookup-type columns (SharePoint limitation)

### Rate limiting

- Reduce `num_workers` if experiencing throttling
- Microsoft Graph API has per-tenant and per-app rate limits

## Changelog

<details>
<summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                                               |
| ------- | ---------- | ------------ | ----------------------------------------------------------------------------------------------------- |
| 0.1.0   | 2025-01-07 | 338          | Initial release with dynamic list/column discovery, incremental sync, and complex column type support |

</details>
