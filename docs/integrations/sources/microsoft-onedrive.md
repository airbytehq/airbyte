# Microsoft Teams

## Sync overview

This source can sync data for the Microsoft Graph API to work with [Microsoft OneDrive](https://docs.microsoft.com/en-us/graph).

This Source Connector is based on a [API v1.0](https://docs.microsoft.com/en-us/graph/api/resources/teams-api-overview?view=graph-rest-1.0).

### Data type mapping

| Integration Type | Airbyte Type | 
|:-----------------|:-------------|
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

### Features

| Feature                       | Supported?\(Yes/No\) |
|:------------------------------|:---------------------|
| Full Refresh Sync             | Yes                  |
| Incremental Sync              | Yes                  |

### Performance considerations

The connector is restricted by normal Microsoft Graph [requests limitation](https://docs.microsoft.com/en-us/graph/throttling).

## Getting started

### Requirements

* Application \(client\) ID 
* Directory \(tenant\) ID
* Client secrets 

### Setup guide

The Microsoft Graph API uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app they, or, in some cases, an administrator, are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested. For apps that don't take a signed-in user, permissions can be pre-consented to by an administrator when the app is installed.

Microsoft Graph has two types of permissions:

* **Delegated permissions** are used by apps that have a signed-in user present. For these apps, either the user or an administrator consents to the permissions that the app requests, and the app can act as the signed-in user when making calls to Microsoft Graph. Some delegated permissions can be consented by non-administrative users, but some higher-privileged permissions require administrator consent.
* **Application permissions** are used by apps that run without a signed-in user present; for example, apps that run as background services or daemons. Application permissions can only be consented by an administrator.

This source requires **Application permissions**. Follow these [instructions](https://docs.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0) for creating an app in the Azure portal. This process will produce the `client_id`, `client_secret`, and `tenant_id` needed for the tap configuration file.

1. Login to [Azure Portal](https://portal.azure.com/#home)
2. Click upper-left menu icon and select Azure Active Directory
3. Select App Registrations
4. Click New registration
5. Register an application
   1. Name: 
   2. Supported account types: Accounts in this organizational directory only
   3. Register \(button\)
6. Record the client\_id, tenant\_id, and which will be used by the tap for authentication and API integration.
7. Select Certificates & secrets
8. Provide Description and Expires
   1. Description: tap-microsoft-teams client secret
   2. Expires: 1-year
   3. Add
9. Copy the client secret value, this will be the client\_secret
10. Select API permissions
    1. Click Add a permission
11. Select Microsoft Graph
12. Select Application permissions
13. Select the following permissions:
    1. Files 
       * Files.Read.All
       * Files.ReadWrite.All
14. Click Add permissions

Token acquiring implemented by [instantiate](https://docs.microsoft.com/en-us/azure/active-directory/develop/scenario-daemon-app-configuration?tabs=python#instantiate-the-msal-application) the confidential client application with a client secret and [calling](https://docs.microsoft.com/en-us/azure/active-directory/develop/scenario-daemon-acquire-token?tabs=python) AcquireTokenForClient from [Microsoft Authentication Library \(MSAL\) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject            |
|:--------|:-----------|:---------------------------------------------------------|:-------------------|
| 0.1.0   | 2021-12-06 | [32655](https://github.com/airbytehq/airbyte/pull/32655) | Migrate to the CDK |
