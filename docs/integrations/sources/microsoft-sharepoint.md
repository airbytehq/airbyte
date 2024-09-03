# Microsoft SharePoint

<HideInUI>

This page contains the setup guide and reference information for the [Microsoft SharePoint](https://portal.azure.com) source connector.

</HideInUI>

### Prerequisites

- Application \(client\) ID
- Directory \(tenant\) ID
- Drive name
- Folder Path
- Client secrets

## Setup guide

### Set up Microsoft SharePoint

<!-- env:cloud -->

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Microsoft SharePoint from the Source type dropdown.
4. Enter a name for the Microsoft SharePoint connector.
5. Select **Search Scope**. Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' for all SharePoint drives the user can access, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both. Default value is 'ALL'.
6. Enter **Folder Path**. Leave empty to search all folders of the drives. This does not apply to shared items.
7. The **OAuth2.0** authorization method is selected by default. Click **Authenticate your Microsoft SharePoint account**. Log in and authorize your Microsoft account.
8. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
9. Add a stream:
   1. Write the **File Type**
   2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported formats are **CSV**, **Parquet**, **Avro** and **JSONL**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format.  For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
   3. Give a **Name** to the stream
   4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
   5. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
10. Click **Set up source**
<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Microsoft SharePoint from the Source type dropdown.
4. Enter a name for the Microsoft SharePoint connector.

### Step 1: Set up SharePoint application

The Microsoft Graph API uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app, they or in some cases an administrator are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested. For apps that don't take a signed-in user, permissions can be pre-consented to by an administrator when the app is installed.

Microsoft Graph has two types of permissions:

- **Delegated permissions** are used by apps that have a signed-in user present. For these apps, either the user or an administrator consents to the permissions that the app requests, and the app can act as the signed-in user when making calls to Microsoft Graph. Some delegated permissions can be consented by non-administrative users, but some higher-privileged permissions require administrator consent.
- **Application permissions** are used by apps that run without a signed-in user present; for example, apps that run as background services or daemons. Application permissions can only be consented by an administrator.

This source requires **Application permissions**. Follow these [instructions](https://docs.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0) for creating an app in the Azure portal. This process will produce the `client_id`, `client_secret`, and `tenant_id` needed for the tap configuration file.

1. Login to [Azure Portal](https://portal.azure.com/#home)
2. Click upper-left menu icon and select **Azure Active Directory**
3. Select **App Registrations**
4. Click **New registration**
5. Register an application
   1. Name:
   2. Supported account types: Accounts in this organizational directory only
   3. Register \(button\)
6. Record the client_id and tenant_id which will be used by the tap for authentication and API integration.
7. Select **Certificates & secrets**
8. Provide **Description and Expires**
   1. Description: tap-microsoft-teams client secret
   2. Expires: 1-year
   3. Add
9. Copy the client secret value, this will be the client_secret
10. Select **API permissions**
    1. Click **Add a permission**
11. Select **Microsoft Graph**
12. Select **Application permissions**
13. Select the following permissions:
    1. Files
       - Files.Read.All
14. Click **Add permissions**
15. Click **Grant admin consent**

### Step 2: Set up the Microsoft SharePoint connector in Airbyte

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up** the source page, select **Microsoft SharePoint** from the Source type dropdown.
4. Enter the name for the Microsoft SharePoint connector.
5. Select **Search Scope**. Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' for all SharePoint drives the user can access, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both. Default value is 'ALL'.
6. Enter **Folder Path**. Leave empty to search all folders of the drives. This does not apply to shared items.
7. Switch to **Service Key Authentication**
8. For **User Practical Name**, enter the [UPN](https://learn.microsoft.com/en-us/sharepoint/list-onedrive-urls) for your user.
9. Enter **Tenant ID**, **Client ID** and **Client secret**.
10. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
11. Add a stream:
    1. Write the **File Type**
    2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported formats are **CSV**, **Parquet**, **Avro** and **JSONL**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
    3. Give a **Name** to the stream
    4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
    5. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
12. Click **Set up source**

<!-- /env:oss -->

<HideInUI>

### Supported sync modes

The Microsoft SharePoint source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature           | Supported?\(Yes/No\) |
|:------------------|:---------------------|
| Full Refresh Sync | Yes                  |
| Incremental Sync  | Yes                  |

### Supported Streams

There is no predefined streams. The streams are based on content of files were added on the Set up page.

### Performance considerations

The connector is restricted by normal Microsoft Graph [requests limitation](https://docs.microsoft.com/en-us/graph/throttling).

### Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------|
| 0.5.1 | 2024-08-24 | [44660](https://github.com/airbytehq/airbyte/pull/44660) | Update dependencies |
| 0.5.0 | 2024-08-19 | [42983](https://github.com/airbytehq/airbyte/pull/42983) | Migrate to CDK v4.5.1 |
| 0.4.5 | 2024-08-19 | [44382](https://github.com/airbytehq/airbyte/pull/44382) | Update dependencies |
| 0.4.4 | 2024-08-12 | [43743](https://github.com/airbytehq/airbyte/pull/43743) | Update dependencies |
| 0.4.3 | 2024-08-10 | [43565](https://github.com/airbytehq/airbyte/pull/43565) | Update dependencies |
| 0.4.2 | 2024-08-03 | [43235](https://github.com/airbytehq/airbyte/pull/43235) | Update dependencies |
| 0.4.1 | 2024-07-27 | [42704](https://github.com/airbytehq/airbyte/pull/42704) | Update dependencies |
| 0.4.0 | 2024-07-25 | [42008](https://github.com/airbytehq/airbyte/pull/42008) | Migrate to CDK v3.5.3 |
| 0.3.1 | 2024-07-20 | [42143](https://github.com/airbytehq/airbyte/pull/42143) | Update dependencies |
| 0.3.0 | 2024-07-16 | [42007](https://github.com/airbytehq/airbyte/pull/42007) | Migrate to CDK v2.4.0 |
| 0.2.11 | 2024-07-13 | [41688](https://github.com/airbytehq/airbyte/pull/41688) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41589](https://github.com/airbytehq/airbyte/pull/41589) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40917](https://github.com/airbytehq/airbyte/pull/40917) | Update dependencies |
| 0.2.8 | 2024-06-26 | [40539](https://github.com/airbytehq/airbyte/pull/40539) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40357](https://github.com/airbytehq/airbyte/pull/40357) | Update dependencies |
| 0.2.6 | 2024-06-24 | [40233](https://github.com/airbytehq/airbyte/pull/40233) | Update dependencies |
| 0.2.5 | 2024-06-22 | [39987](https://github.com/airbytehq/airbyte/pull/39987) | Update dependencies |
| 0.2.4 | 2024-05-29 | [38675](https://github.com/airbytehq/airbyte/pull/38675) | Avoid error on empty stream when running discover |
| 0.2.3 | 2024-04-17 | [37372](https://github.com/airbytehq/airbyte/pull/37372) | Make refresh token optional |
| 0.2.2 | 2024-03-28 | [36573](https://github.com/airbytehq/airbyte/pull/36573) | Update QL to 400 |
| 0.2.1 | 2024-03-22 | [36381](https://github.com/airbytehq/airbyte/pull/36381) | Unpin CDK |
| 0.2.0 | 2024-03-06 | [35830](https://github.com/airbytehq/airbyte/pull/35830) | Add fetching shared items |
| 0.1.0 | 2024-01-25 | [33537](https://github.com/airbytehq/airbyte/pull/33537) | New source |

</details>

</HideInUI>
