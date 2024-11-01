# Microsoft Teams

## Sync overview

This source can sync data for the Microsoft Graph API to work with [Microsoft Teams](https://docs.microsoft.com/en-us/graph/teams-concept-overview).

There are currently 2 versions of [Microsoft Graph REST APIs](https://docs.microsoft.com/en-us/graph/versioning-and-support) - v1.0 and beta. Beta version contains new or enhanced APIs that are still in preview status. But APIs in preview status are subject to change, and may break existing scenarios without notice. It isn't recommended taking a production dependency on APIs in the beta endpoint. This Source Connector is based on a [API v1.0](https://docs.microsoft.com/en-us/graph/api/resources/teams-api-overview?view=graph-rest-1.0).

### Output schema

This Source is capable of syncing the following core Streams:

- [users](https://docs.microsoft.com/en-us/graph/api/user-list?view=graph-rest-beta&tabs=http)
- [groups](https://docs.microsoft.com/en-us/graph/teams-list-all-teams?context=graph%2Fapi%2F1.0&view=graph-rest-1.0)
- [group_members](https://docs.microsoft.com/en-us/graph/api/group-list-members?view=graph-rest-1.0&tabs=http)
- [group_owners](https://docs.microsoft.com/en-us/graph/api/group-list-owners?view=graph-rest-1.0&tabs=http)
- [channels](https://docs.microsoft.com/en-us/graph/api/channel-list?view=graph-rest-1.0&tabs=http)
- [channel_members](https://docs.microsoft.com/en-us/graph/api/channel-list-members?view=graph-rest-1.0&tabs=http)
- [channel_tabs](https://docs.microsoft.com/en-us/graph/api/channel-list-tabs?view=graph-rest-1.0&tabs=http)
- [conversations](https://docs.microsoft.com/en-us/graph/api/group-list-conversations?view=graph-rest-beta&tabs=http)
- [conversation_threads](https://docs.microsoft.com/en-us/graph/api/conversation-list-threads?view=graph-rest-beta&tabs=http)
- [conversation_posts](https://docs.microsoft.com/en-us/graph/api/conversationthread-list-posts?view=graph-rest-beta&tabs=http)
- [team_drives](https://docs.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-beta&tabs=http#get-the-document-library-associated-with-a-group)
- [team_device_usage_report](https://docs.microsoft.com/en-us/graph/api/reportroot-getteamsdeviceusageuserdetail?view=graph-rest-1.0)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

Some APIs aren't supported in v1.0, e.g. channel messages and channel messages replies.

### Data type mapping

| Integration Type | Airbyte Type                 |
| :--------------- | :--------------------------- |
| `string`         | `string`                     |
| `number`         | `number`                     |
| `date`           | `date`                       |
| `datetime`       | `timestamp_without_timezone` |
| `array`          | `array`                      |
| `object`         | `object`                     |

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

### Performance considerations

The connector is restricted by normal Microsoft Graph [requests limitation](https://docs.microsoft.com/en-us/graph/throttling).

## Getting started

### Requirements

- Application \(client\) ID
- Directory \(tenant\) ID
- Client secrets

### Setup guide

The Microsoft Graph API uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app they, or, in some cases, an administrator, are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested. For apps that don't take a signed-in user, permissions can be pre-consented to by an administrator when the app is installed.

Microsoft Graph has two types of permissions:

- **Delegated permissions** are used by apps that have a signed-in user present. For these apps, either the user or an administrator consents to the permissions that the app requests, and the app can act as the signed-in user when making calls to Microsoft Graph. Some delegated permissions can be consented by non-administrative users, but some higher-privileged permissions require administrator consent.
- **Application permissions** are used by apps that run without a signed-in user present; for example, apps that run as background services or daemons. Application permissions can only be consented by an administrator.

This source requires **Application permissions**. Follow these [instructions](https://docs.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0) for creating an app in the Azure portal. This process will produce the `client_id`, `client_secret`, and `tenant_id` needed for the tap configuration file.

1. Login to [Azure Portal](https://portal.azure.com/#home)
2. Click upper-left menu icon and select Azure Active Directory
3. Select App Registrations
4. Click New registration
5. Register an application
   1. Name:
   2. Supported account types: Accounts in this organizational directory only
   3. Register \(button\)
6. Record the client_id, tenant_id, and which will be used by the tap for authentication and API integration.
7. Select Certificates & secrets
8. Provide Description and Expires
   1. Description: tap-microsoft-teams client secret
   2. Expires: 1-year
   3. Add
9. Copy the client secret value, this will be the client_secret
10. Select API permissions
    1. Click Add a permission
11. Select Microsoft Graph
12. Select Application permissions
13. Select the following permissions:
    1. Users
       - User.Read.All
       - User.ReadWrite.All
       - Directory.Read.All
       - Directory.ReadWrite.All
    2. Groups
       - GroupMember.Read.All
       - Group.Read.All
       - Directory.Read.All
       - Group.ReadWrite.All
       - Directory.ReadWrite.All
    3. Group members
       - GroupMember.Read.All
       - Group.Read.All
       - Directory.Read.All
    4. Group owners
       - Group.Read.All
       - User.Read.All
       - Group.Read.All
       - User.ReadWrite.All
       - Group.Read.All
       - User.Read.All
       - Application.Read.All
    5. Channels
       - ChannelSettings.Read.Group
       - ChannelSettings.ReadWrite.Group
       - Channel.ReadBasic.All
       - ChannelSettings.Read.All
       - ChannelSettings.ReadWrite.All
       - Group.Read.All
       - Group.ReadWrite.All
       - Directory.Read.All
       - Directory.ReadWrite.All
    6. Channel members
       - ChannelMember.Read.All
       - ChannelMember.ReadWrite.All
    7. Channel tabs
       - TeamsTab.Read.Group
       - TeamsTab.ReadWrite.Group
       - TeamsTab.Read.All
       - TeamsTab.ReadWriteForTeam.All
       - TeamsTab.ReadWrite.All
       - Group.Read.All
       - Group.ReadWrite.All
       - Directory.Read.All
       - Directory.ReadWrite.All
    8. Conversations
       - Group.Read.All
       - Group.ReadWrite.All
    9. Conversation threads
       - Group.Read.All
       - Group.ReadWrite.All
    10. Conversation posts
        - Group.Read.All
        - Group.ReadWrite.All
    11. Team drives
        - Files.Read.All
        - Files.ReadWrite.All
        - Sites.Read.All
        - Sites.ReadWrite.All
    12. Team device usage report
        - Reports.Read.All
14. Click Add permissions

Token acquiring implemented by [instantiate](https://docs.microsoft.com/en-us/azure/active-directory/develop/scenario-daemon-app-configuration?tabs=python#instantiate-the-msal-application) the confidential client application with a client secret and [calling](https://docs.microsoft.com/en-us/azure/active-directory/develop/scenario-daemon-acquire-token?tabs=python) AcquireTokenForClient from [Microsoft Authentication Library \(MSAL\) for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 1.2.3 | 2024-10-29 | [47758](https://github.com/airbytehq/airbyte/pull/47758) | Update dependencies |
| 1.2.2 | 2024-10-28 | [47453](https://github.com/airbytehq/airbyte/pull/47453) | Update dependencies |
| 1.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.2.0 | 2024-08-15 | [44116](https://github.com/airbytehq/airbyte/pull/44116) | Refactor connector to manifest-only format |
| 1.1.11 | 2024-08-12 | [43772](https://github.com/airbytehq/airbyte/pull/43772) | Update dependencies |
| 1.1.10 | 2024-08-10 | [43547](https://github.com/airbytehq/airbyte/pull/43547) | Update dependencies |
| 1.1.9 | 2024-08-03 | [43251](https://github.com/airbytehq/airbyte/pull/43251) | Update dependencies |
| 1.1.8 | 2024-07-27 | [42691](https://github.com/airbytehq/airbyte/pull/42691) | Update dependencies |
| 1.1.7 | 2024-07-20 | [41853](https://github.com/airbytehq/airbyte/pull/41853) | Update dependencies |
| 1.1.6 | 2024-07-10 | [41382](https://github.com/airbytehq/airbyte/pull/41382) | Update dependencies |
| 1.1.5 | 2024-07-09 | [41318](https://github.com/airbytehq/airbyte/pull/41318) | Update dependencies |
| 1.1.4 | 2024-07-06 | [40913](https://github.com/airbytehq/airbyte/pull/40913) | Update dependencies |
| 1.1.3 | 2024-06-25 | [40366](https://github.com/airbytehq/airbyte/pull/40366) | Update dependencies |
| 1.1.2 | 2024-06-22 | [40026](https://github.com/airbytehq/airbyte/pull/40026) | Update dependencies |
| 1.1.1 | 2024-06-04 | [39046](https://github.com/airbytehq/airbyte/pull/39046) | [autopull] Upgrade base image to v1.2.1 |
| 1.1.0 | 2024-03-24 | [36223](https://github.com/airbytehq/airbyte/pull/36223) | Migration to low code |
| 1.0.0 | 2024-01-04 | [33959](https://github.com/airbytehq/airbyte/pull/33959) | Schema updates |
| 0.2.5 | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Update titles and descriptions |
| 0.2.4 | 2021-12-07 | [7807](https://github.com/airbytehq/airbyte/pull/7807) | Implement OAuth support |
| 0.2.3 | 2021-12-06 | [8469](https://github.com/airbytehq/airbyte/pull/8469) | Migrate to the CDK |

</details>
