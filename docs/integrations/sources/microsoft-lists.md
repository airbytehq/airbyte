# Microsoft Lists

<HideInUI>

This page contains the setup guide and reference information for the [Microsoft Lists](https://www.microsoft.com/en-us/microsoft-365/microsoft-lists) source connector.

</HideInUI>

## Prerequisites

- A Microsoft 365 account with access to Microsoft Lists
- A SharePoint site containing the lists you want to sync
- An Azure AD (Microsoft Entra ID) application registration with the `Sites.Read.All` Microsoft Graph application permission
- Admin consent granted for the application permission
- The SharePoint site ID for the site containing your lists

## Setup guide

### Step 1: Register an Azure AD application

If you don't already have an Azure AD application registered, create one:

1. Go to the [Azure Portal](https://portal.azure.com).
2. Navigate to **Microsoft Entra ID** > **App registrations** > **New registration**.
3. Enter a name for your app, such as `Airbyte Microsoft Lists Connector`.
4. For **Supported account types**, select **Accounts in this organizational directory only** (single tenant).
5. Leave **Redirect URI** blank. This connector uses client credentials authentication and does not require a redirect URI.
6. Click **Register**.

### Step 2: Configure API permissions

1. In your app registration, go to **API Permissions** > **Add a permission**.
2. Select **Microsoft Graph**.
3. Select **Application permissions**.
4. Search for and select `Sites.Read.All`.
5. Click **Add permissions**.
6. Click **Grant admin consent** to authorize the permission. An Azure AD admin must perform this step.

:::note
The `Sites.Read.All` permission grants read access to all SharePoint sites in your tenant. This is the minimum permission required by the connector. You do not need `Sites.ReadWrite.All` because this connector only reads data.
:::

### Step 3: Create a client secret

1. In your app registration, go to **Certificates & secrets** > **New client secret**.
2. Enter a description and select an expiration period.
3. Click **Add** and copy the secret value immediately. You cannot retrieve it later.

### Step 4: Collect your credentials

From the **Overview** page of your app registration, copy:

- **Application (client) ID** — this is the `client_id`.
- **Directory (tenant) ID** — this is the `tenant_id`.

### Step 5: Find your SharePoint site ID

The `site_id` identifies which SharePoint site contains the lists you want to sync. To find it, call the Microsoft Graph API:

```text
GET https://graph.microsoft.com/v1.0/sites/{hostname}:/{server-relative-path}
```

For example, if your SharePoint site URL is `https://contoso.sharepoint.com/sites/TeamSite`, the request is:

```text
GET https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/TeamSite
```

The `id` field in the response is your site ID. You can also find the site ID by appending `/_api/site/id` to your SharePoint site URL in a browser.

### Step 6: Determine the Application ID URI

The `application_id_uri` is the OAuth scope used when requesting an access token. For Microsoft Graph API, use:

```text
https://graph.microsoft.com/.default
```

### Step 7: Set up the connector in Airbyte

1. In Airbyte, go to **Sources** > **New source** > **Microsoft Lists**.
2. Enter the following configuration values:

| Field | Description |
|-------|-------------|
| **Site ID** | The SharePoint site ID from Step 5. |
| **Client ID** | The Application (client) ID from Step 4. |
| **Client Secret** | The client secret value from Step 3. |
| **Application ID URI** | The OAuth scope. Use `https://graph.microsoft.com/.default`. |
| **Tenant ID** | The Directory (tenant) ID from Step 4. |
| **Domain** | Your SharePoint domain, such as `contoso.sharepoint.com`. |

3. Click **Set up source**.

<HideInUI>

## Supported sync modes

The Microsoft Lists source connector supports the following sync mode:

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite)

This connector does not support incremental syncs.

## Supported streams

The Microsoft Lists source connector supports the following streams. All streams read from the [Microsoft Graph API v1.0](https://learn.microsoft.com/en-us/graph/api/resources/list?view=graph-rest-1.0).

| Stream | Description | Primary Key |
|--------|-------------|-------------|
| [lists](https://learn.microsoft.com/en-us/graph/api/list-list?view=graph-rest-1.0) | All lists in the configured SharePoint site. | `id` |
| [listcontenttypes](https://learn.microsoft.com/en-us/graph/api/resources/contenttype?view=graph-rest-1.0) | Content types defined for each list. A substream of `lists`. | `id` |
| [items](https://learn.microsoft.com/en-us/graph/api/listitem-list?view=graph-rest-1.0) | Items (rows) in each list. A substream of `lists`. | — |
| [listitems](https://learn.microsoft.com/en-us/graph/api/listitem-get?view=graph-rest-1.0) | Detailed metadata for each individual list item, including fields data. A substream of `items`. | — |
| [columnvalues](https://learn.microsoft.com/en-us/graph/api/listitem-get?view=graph-rest-1.0) | Column field values for each list item, retrieved with the `?expand=fields` query parameter. A substream of `items`. | `id` |

### Stream relationships

The connector uses parent-child stream relationships:

- **lists** is the top-level stream.
- **listcontenttypes** and **items** are child streams of **lists**, fetching data for each list.
- **listitems** and **columnvalues** are child streams of **items**, fetching detailed data for each item.

## Limitations

- This connector only supports **full refresh** syncs. Every sync fetches all data from the configured site.
- The connector reads from a single SharePoint site. To sync lists from multiple sites, create a separate source for each site.
- This connector is in **alpha** release stage and has **community** support level.

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.53 | 2026-03-24 | [75009](https://github.com/airbytehq/airbyte/pull/75009) | Update dependencies |
| 0.0.52 | 2026-03-10 | [74534](https://github.com/airbytehq/airbyte/pull/74534) | Update dependencies |
| 0.0.51 | 2026-02-24 | [73221](https://github.com/airbytehq/airbyte/pull/73221) | Update dependencies |
| 0.0.50 | 2026-02-03 | [72718](https://github.com/airbytehq/airbyte/pull/72718) | Update dependencies |
| 0.0.49 | 2026-01-20 | [72014](https://github.com/airbytehq/airbyte/pull/72014) | Update dependencies |
| 0.0.48 | 2026-01-14 | [71512](https://github.com/airbytehq/airbyte/pull/71512) | Update dependencies |
| 0.0.47 | 2025-12-18 | [70767](https://github.com/airbytehq/airbyte/pull/70767) | Update dependencies |
| 0.0.46 | 2025-11-25 | [70112](https://github.com/airbytehq/airbyte/pull/70112) | Update dependencies |
| 0.0.45 | 2025-11-18 | [69573](https://github.com/airbytehq/airbyte/pull/69573) | Update dependencies |
| 0.0.44 | 2025-10-29 | [69045](https://github.com/airbytehq/airbyte/pull/69045) | Update dependencies |
| 0.0.43 | 2025-10-21 | [68470](https://github.com/airbytehq/airbyte/pull/68470) | Update dependencies |
| 0.0.42 | 2025-10-14 | [67851](https://github.com/airbytehq/airbyte/pull/67851) | Update dependencies |
| 0.0.41 | 2025-10-07 | [67391](https://github.com/airbytehq/airbyte/pull/67391) | Update dependencies |
| 0.0.40 | 2025-09-30 | [66347](https://github.com/airbytehq/airbyte/pull/66347) | Update dependencies |
| 0.0.39 | 2025-09-09 | [65757](https://github.com/airbytehq/airbyte/pull/65757) | Update dependencies |
| 0.0.38 | 2025-08-23 | [65208](https://github.com/airbytehq/airbyte/pull/65208) | Update dependencies |
| 0.0.37 | 2025-08-09 | [64789](https://github.com/airbytehq/airbyte/pull/64789) | Update dependencies |
| 0.0.36 | 2025-08-02 | [64240](https://github.com/airbytehq/airbyte/pull/64240) | Update dependencies |
| 0.0.35 | 2025-07-26 | [63896](https://github.com/airbytehq/airbyte/pull/63896) | Update dependencies |
| 0.0.34 | 2025-07-19 | [63444](https://github.com/airbytehq/airbyte/pull/63444) | Update dependencies |
| 0.0.33 | 2025-07-12 | [63217](https://github.com/airbytehq/airbyte/pull/63217) | Update dependencies |
| 0.0.32 | 2025-07-05 | [62657](https://github.com/airbytehq/airbyte/pull/62657) | Update dependencies |
| 0.0.31 | 2025-06-28 | [62382](https://github.com/airbytehq/airbyte/pull/62382) | Update dependencies |
| 0.0.30 | 2025-06-21 | [61930](https://github.com/airbytehq/airbyte/pull/61930) | Update dependencies |
| 0.0.29 | 2025-06-14 | [61065](https://github.com/airbytehq/airbyte/pull/61065) | Update dependencies |
| 0.0.28 | 2025-05-24 | [60444](https://github.com/airbytehq/airbyte/pull/60444) | Update dependencies |
| 0.0.27 | 2025-05-10 | [60125](https://github.com/airbytehq/airbyte/pull/60125) | Update dependencies |
| 0.0.26 | 2025-05-04 | [59520](https://github.com/airbytehq/airbyte/pull/59520) | Update dependencies |
| 0.0.25 | 2025-04-26 | [58756](https://github.com/airbytehq/airbyte/pull/58756) | Update dependencies |
| 0.0.24 | 2025-04-30 | [58575](https://github.com/airbytehq/airbyte/pull/58575) | Fix ListItems and ColumnValues streams |
| 0.0.23 | 2025-04-19 | [58521](https://github.com/airbytehq/airbyte/pull/58521) | Update dependencies |
| 0.0.22 | 2025-04-12 | [57861](https://github.com/airbytehq/airbyte/pull/57861) | Update dependencies |
| 0.0.21 | 2025-04-05 | [57042](https://github.com/airbytehq/airbyte/pull/57042) | Update dependencies |
| 0.0.20 | 2025-03-29 | [56713](https://github.com/airbytehq/airbyte/pull/56713) | Update dependencies |
| 0.0.19 | 2025-03-22 | [56074](https://github.com/airbytehq/airbyte/pull/56074) | Update dependencies |
| 0.0.18 | 2025-03-08 | [55445](https://github.com/airbytehq/airbyte/pull/55445) | Update dependencies |
| 0.0.17 | 2025-03-01 | [54817](https://github.com/airbytehq/airbyte/pull/54817) | Update dependencies |
| 0.0.16 | 2025-02-22 | [54329](https://github.com/airbytehq/airbyte/pull/54329) | Update dependencies |
| 0.0.15 | 2025-02-15 | [53848](https://github.com/airbytehq/airbyte/pull/53848) | Update dependencies |
| 0.0.14 | 2025-02-08 | [53285](https://github.com/airbytehq/airbyte/pull/53285) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52753](https://github.com/airbytehq/airbyte/pull/52753) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52249](https://github.com/airbytehq/airbyte/pull/52249) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51824](https://github.com/airbytehq/airbyte/pull/51824) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51148](https://github.com/airbytehq/airbyte/pull/51148) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50613](https://github.com/airbytehq/airbyte/pull/50613) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50117](https://github.com/airbytehq/airbyte/pull/50117) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49598](https://github.com/airbytehq/airbyte/pull/49598) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49229](https://github.com/airbytehq/airbyte/pull/49229) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48952](https://github.com/airbytehq/airbyte/pull/48952) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48202](https://github.com/airbytehq/airbyte/pull/48202) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47925](https://github.com/airbytehq/airbyte/pull/47925) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47544](https://github.com/airbytehq/airbyte/pull/47544) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
