# Microsoft Teams

This page contains the setup guide and reference information for Microsoft Teams.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| SSL connection | Yes |
| Namespaces | No |

## Prerequisites

* An Azure account that has an active subscription
* Application (client) ID
* Directory (tenant) ID
* Client secrets

The [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/overview) uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app they, or, in some cases, an administrator, are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested. For apps that don't take a signed-in user, permissions can be pre-consented to by an administrator when the app is installed.

Microsoft Graph has two types of permissions:

* **Delegated permissions** are used by apps that have a signed-in user present. For these apps, either the user or an administrator consents to the permissions that the app requests, and the app can act as the signed-in user when making calls to Microsoft Graph. Some delegated permissions can be consented by non-administrative users, but some higher-privileged permissions require administrator consent.

* **Application permissions** are used by apps that run without a signed-in user present; for example, apps that run as background services or daemons. Application permissions can only be consented by an administrator. This source requires **Application permissions**.

## Setup guide

### Step 1: Obtain Microsoft Teams crendentials

Follow these [instructions](https://docs.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0) or the below steps for creating an app in the Azure portal. This process will produce the `client_id`, `client_secret`, and `tenant_id` needed to set up the source in Daspire.

1. Login to [Azure Portal](https://portal.azure.com/#home).

2. Select **Microsoft Entra ID** from list Azure services, or search for it in the search bar.
![Microsoft Entra ID](/docs/setup-guide/assets/images/teams-entra-id.jpg "Microsoft Entra ID")

3. On the left side nav bar, click **App registrations**, and click click the **New registration** tab.
![Microsoft App Registration](/docs/setup-guide/assets/images/teams-app-registration.jpg "Microsoft App Registration")

4. Register an application. Enter a name for your app, and in Supported account types, select **Accounts in this organizational directory only**. Cick the Register button.
![Microsoft Register an App](/docs/setup-guide/assets/images/teams-register-app.jpg "Microsoft Register an App")

5. You will be directed to your App's Overview page. From there, copy the **Application (client) ID** and **Directory (tenant) ID**. You will use them later for authentication in Daspire.
![Microsoft App Details](/docs/setup-guide/assets/images/teams-app-details.jpg "Microsoft App Details")

6. Click **Add a certificate or secret**, which will open the Certificates & secrets page.
![Microsoft App Client Secret](/docs/setup-guide/assets/images/teams-app-client-secret.jpg "Microsoft App Client Secret")

7. Click **+ New client secret**. In the opened pop up, provide a description for the client secret and select the expirary duration that suits your need. Then click Add.

8. Copy the client secret **Value**. You will use it later for authentication in Daspire.
![Microsoft Client Secret](/docs/setup-guide/assets/images/teams-client-secret.jpg "Microsoft Client Secret")

9. On the left side nav bar, click **API permissions**, then **Add a permission**.
![Microsoft API Permissions](/docs/setup-guide/assets/images/teams-app-permissions.jpg "Microsoft API Permissions")

10. Select **Microsoft Graph**, then select **Application permissions**.
![Microsoft Graph](/docs/setup-guide/assets/images/teams-ms-graph-api.jpg "Microsoft Graph")

11. Select the following permissions:
  * Channels
    * Channel.ReadBasic.All

  * ChannelMembers
    * ChannelMember.Read.All
    * ChannelMember.ReadWrite.All

  * ChannelMessage
    * ChannelMessage.Read.All

  * Chat
    * Chat.Read.All
    * Chat.ReadBasic.All
    * Chat.ReadWrite.All

  * ChatMember
    * ChatMember.Read.All
    * ChatMember.ReadWrite.All

  * ChatMessage
    * ChatMessage.Read.All

  * Files
    * Files.Read.All
    * Files.ReadWrite.All

  * Groups
    * Group.Read.All
    * Group.ReadWrite.All

  * GroupMembers
    * GroupMember.Read.All
    * GroupMember.ReadWrite.All

  * TeamsActivity
    * TeamsActivity.Read.All

  * TeamMember
    * TeamMember.Read.All
    * TeamMember.ReadWrite.All

  * TeamTabs
    * TeamsTab.Read.All
    * TeamsTab.ReadWrite.All
    * TeamsTab.ReadWriteForTeam.All

  * Team
    * Team.ReadBasic.All

  * TeamworkDevice
    * TeamworkDevice.Read.All
    * TeamworkDevice.ReadWrite.All

  * Users
    * User.Read.All
    * User.ReadWrite.All

12. Once you're done, click **Add permissions**.
![Microsoft Graph App Permissions](/docs/setup-guide/assets/images/teams-ms-graph-app-permissions.jpg "Microsoft Graph App Permissions")

### Step 2: Set up Microsoft Teams  in Daspire

1. Select **Microsoft Teams** from the Source list.

2. Enter a **Source Name**.

3. Enter **Application (client) ID**, **Directory (tenant) ID**, and **Client secrets** you obtained in Step 1.

4. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [channels](https://docs.microsoft.com/en-us/graph/api/channel-list?view=graph-rest-1.0&tabs=http)
* [channel_members](https://docs.microsoft.com/en-us/graph/api/channel-list-members?view=graph-rest-1.0&tabs=http)
* [channel_tabs](https://docs.microsoft.com/en-us/graph/api/channel-list-tabs?view=graph-rest-1.0&tabs=http)
* [conversations](https://docs.microsoft.com/en-us/graph/api/group-list-conversations?view=graph-rest-beta&tabs=http)
* [conversation_threads](https://docs.microsoft.com/en-us/graph/api/conversation-list-threads?view=graph-rest-beta&tabs=http)
* [conversation_posts](https://docs.microsoft.com/en-us/graph/api/conversationthread-list-posts?view=graph-rest-beta&tabs=http)
* [groups](https://docs.microsoft.com/en-us/graph/teams-list-all-teams?context=graph%2Fapi%2F1.0&view=graph-rest-1.0)
* [group_members](https://docs.microsoft.com/en-us/graph/api/group-list-members?view=graph-rest-1.0&tabs=http)
* [group_owners](https://docs.microsoft.com/en-us/graph/api/group-list-owners?view=graph-rest-1.0&tabs=http)
* [team_drives](https://docs.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-beta&tabs=http#get-the-document-library-associated-with-a-group)
* [team_device_usage_report](https://docs.microsoft.com/en-us/graph/api/reportroot-getteamsdeviceusageuserdetail?view=graph-rest-1.0)
* [users](https://docs.microsoft.com/en-us/graph/api/user-list?view=graph-rest-beta&tabs=http)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Troubleshooting

1. Rate limit: This integration is restricted by normal [Microsoft Graph requests limitation](https://docs.microsoft.com/en-us/graph/throttling).

2. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
