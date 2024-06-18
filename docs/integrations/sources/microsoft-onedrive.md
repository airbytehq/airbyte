# Microsoft OneDrive

This page contains the setup guide and reference information for the Microsoft OneDrive source connector.

### Requirements

- Application \(client\) ID
- Directory \(tenant\) ID
- Drive name
- Folder Path
- Client secrets

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Microsoft OneDrive** from the Source type dropdown.
4. Enter the name for the Microsoft OneDrive connector.
5. Enter **Drive Name**. To find your drive name go to settings and at the top of setting menu you can find the name of your drive.
6. Select **Search Scope**. Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' to search in the selected OneDrive drive, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both. Default value is 'ALL'.
7. Enter **Folder Path**. Leave empty to search all folders of the drives. This does not apply to shared items.
8. The **OAuth2.0** authorization method is selected by default. Click **Authenticate your Microsoft OneDrive account**. Log in and authorize your Microsoft account.
9. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
10. Add a stream:
    1. Write the **File Type**
    2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported formats are **CSV**, **Parquet**, **Avro** and **JSONL**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
    3. Give a **Name** to the stream
    4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
    5. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
11. Click **Set up source**
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

### Step 1: Set up OneDrive application

The Microsoft Graph API uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app they, or, in some cases, an administrator, are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested. For apps that don't take a signed-in user, permissions can be pre-consented to by an administrator when the app is installed.

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
   1. Description: tap-microsoft-onedrive client secret
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

### Step 2: Set up the Microsoft OneDrive connector in Airbyte

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up** the source page, select **Microsoft OneDrive** from the Source type dropdown.
4. Enter the name for the Microsoft OneDrive connector.
5. Enter **Drive Name**. To find your drive name go to settings and at the top of setting menu you can find the name of your drive.
6. Select **Search Scope**. Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' to search in the selected OneDrive drive, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both. Default value is 'ALL'.
7. Enter **Folder Path**. Leave empty to search all folders of the drives. This does not apply to shared items.
8. Switch to **Service Key Authentication**
9. For **User Practical Name**, enter the [UPN](https://learn.microsoft.com/en-us/sharepoint/list-onedrive-urls) for your user.
10. Enter **Tenant ID**, **Client ID** and **Client secret**.
11. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
12. Add a stream:
    1. Write the **File Type**
    2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported formats are **CSV**, **Parquet**, **Avro** and **JSONL**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
    3. Give a **Name** to the stream
    4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
    5. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
13. Click **Set up source**

<!-- /env:oss -->

## Sync overview

### Data type mapping

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

### Features

| Feature           | Supported?\(Yes/No\) |
| :---------------- | :------------------- |
| Full Refresh Sync | Yes                  |
| Incremental Sync  | Yes                  |

### Performance considerations

The connector is restricted by normal Microsoft Graph [requests limitation](https://docs.microsoft.com/en-us/graph/throttling).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| 0.2.2 | 2024-06-06 | [39227](https://github.com/airbytehq/airbyte/pull/39227) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-29 | [38676](https://github.com/airbytehq/airbyte/pull/38676) | Avoid error on empty stream when running discover |
| 0.2.0 | 2024-03-12 | [35849](https://github.com/airbytehq/airbyte/pull/35849) | Add fetching shared items |
| 0.1.9 | 2024-03-11 | [35956](https://github.com/airbytehq/airbyte/pull/35956) | Pin `transformers` transitive dependency |
| 0.1.8 | 2024-03-06 | [35858](https://github.com/airbytehq/airbyte/pull/35858) | Bump poetry.lock to upgrade transitive dependency |
| 0.1.7 | 2024-03-04 | [35584](https://github.com/airbytehq/airbyte/pull/35584) | Enable in Cloud |
| 0.1.6 | 2024-02-06 | [34936](https://github.com/airbytehq/airbyte/pull/34936) | Bump CDK version to avoid missing SyncMode errors |
| 0.1.5 | 2024-01-30 | [34681](https://github.com/airbytehq/airbyte/pull/34681) | Unpin CDK version to make compatible with the Concurrent CDK |
| 0.1.4 | 2024-01-30 | [34661](https://github.com/airbytehq/airbyte/pull/34661) | Pin CDK version until upgrade for compatibility with the Concurrent CDK |
| 0.1.3 | 2024-01-24 | [34478](https://github.com/airbytehq/airbyte/pull/34478) | Fix OAuth |
| 0.1.2 | 2021-12-22 | [33745](https://github.com/airbytehq/airbyte/pull/33745) | Add ql and sl to metadata |
| 0.1.1 | 2021-12-15 | [33758](https://github.com/airbytehq/airbyte/pull/33758) | Fix for docs name |
| 0.1.0 | 2021-12-06 | [32655](https://github.com/airbytehq/airbyte/pull/32655) | New source |

</details>
