---
dockerRepository: airbyte/source-sharepoint-lists-enterprise
enterprise-connector: true
---

# SharePoint Lists Enterprise

<HideInUI>

This page contains the setup guide and reference information for the [SharePoint Lists Enterprise](https://portal.azure.com) source connector.

</HideInUI>

## Prerequisites

- Application (client) ID
- Directory (tenant) ID
- Client secret
- SharePoint Site ID

## Setup guide

### Step 1: Set up SharePoint application

The Microsoft Graph API uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app, they or in some cases an administrator are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested.

This source requires **Application permissions**. Follow these [instructions](https://docs.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0) for creating an app in the Azure portal. This process will produce the `client_id`, `client_secret`, and `tenant_id` needed for the connector configuration.

1. Login to [Azure Portal](https://portal.azure.com/#home)
2. Click upper-left menu icon and select **Azure Active Directory**
3. Select **App Registrations**
4. Click **New registration**
5. Register an application
   1. Name: SharePoint Lists Enterprise
   2. Supported account types: Accounts in this organizational directory only
   3. Register (button)
6. Record the client_id and tenant_id which will be used by the connector for authentication.
7. Select **Certificates & secrets**
8. Provide **Description and Expires**
   1. Description: SharePoint Lists Enterprise client secret
   2. Expires: 1-year
   3. Add
9. Copy the client secret value, this will be the client_secret
10. Select **API permissions**
    1. Click **Add a permission**
11. Select **Microsoft Graph**
12. Select **Application permissions**
13. Select the following permissions:
    - Sites.Read.All
14. Click **Add permissions**
15. Click **Grant admin consent**

### Step 2: Get the SharePoint Site ID

To get the Site ID, you can use the Microsoft Graph Explorer or make an API call:

```
GET https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}
```

The Site ID will be in the format: `hostname,site-guid,web-guid`

### Step 3: Set up the SharePoint Lists Enterprise connector in Airbyte

1. Navigate to the Airbyte dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up** the source page, select **SharePoint Lists Enterprise** from the Source type dropdown.
4. Enter the name for the SharePoint Lists Enterprise connector.
5. Enter **Client ID**, **Client Secret**, **Tenant ID**, and **Site ID**.
6. Optionally, enter a **List Name Filter** regex pattern to filter which lists to sync.
7. Optionally, toggle **Skip Document Libraries** to exclude document library lists.
8. Optionally, adjust the **Number of Workers** (1-20) to control concurrent processing. Higher values increase throughput but may hit rate limits. Default is 10.
9. Click **Set up source**

## Supported sync modes

The SharePoint Lists Enterprise source connector supports the following sync modes:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Supported Streams

This connector dynamically discovers all non-hidden lists in your SharePoint site and creates a stream for each list. Additionally, it provides the following static streams:

- **lists**: Metadata about all lists in the SharePoint site
- **user_information**: User lookup table for Author/Editor fields

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                      |
| :------ | :--------- | :----------- | :------------------------------------------- |
| 0.1.0   | 2025-01-07 | [337](https://github.com/airbytehq/airbyte-enterprise/pull/337) | Initial release of SharePoint Lists Enterprise connector with CDK 7 |

</details>
