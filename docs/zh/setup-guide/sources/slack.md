# Slack

This page contains the setup guide and reference information for Slack.

## Prerequisites

* Slack instance Administrator access
* Slack Bot User OAuth Access Token

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Create a Slack app

1. Go to the [Slack apps page](https://api.slack.com/apps).

2. Click **Create New App**.
![Slack Create New App](/docs/setup-guide/assets/images/slack-create-app.jpg "Slack Create New App")

3. Enter a name and the select the Slack workspace you want to create the app for. Make sure you select the workspace form which you want to pull data.
![Slack Choose Woekspace](/docs/setup-guide/assets/images/slack-choose-workspace.jpg "Slack Choose Woekspace")

  Completing that form will take you to the **Basic Information** page for your app.

4. Inside your add, go to **OAuth & Permissions**.
![Slack OAuth & Permissions](/docs/setup-guide/assets/images/slack-permissions.jpg "Slack OAuth & Permissions")

5. Under **Bot Token Scopes** click on **Add an OAuth Scope**.
![Slack OAuth Scopes](/docs/setup-guide/assets/images/slack-oauth-scopes.jpg "Slack OAuth Scopes")

  We will now need to add the following scopes:

  > * channels:history
  > * channels:join
  > * channels:read
  > * files:read
  > * groups:read
  > * links:read
  > * reactions:read
  > * remote_files:read
  > * team:read
  > * usergroups:read
  > * users.profile:read
  > * users:read
![Slack Scope](/docs/setup-guide/assets/images/slack-scopes.jpg "Slack Scopes")

6. On the left sidebar, click **Install to Workspace**.
![Slack Install App](/docs/setup-guide/assets/images/slack-install-app.jpg "Slack Install App")

  This will generate a **Bot User OAuth Access Token**. Write it down.
  ![Slack OAuth Token](/docs/setup-guide/assets/images/slack-oauth-token.jpg "Slack OAuth Token")

7. Go to your slack workspace. For any public channel, click the channel name dropdown, then go to the **Integrations** tab. Click **Add an App**.
![Slack Add App](/docs/setup-guide/assets/images/slack-add-app.jpg "Slack Add App")

8. In the search bar search for the name of the app you created earlier. And add the app.
![Slack Add App to Channel](/docs/setup-guide/assets/images/slack-add-app-to-channel.jpg "Slack Add App to Channel")

Daspire will only replicate messages from channels that the Slack app has been added to.

You can read more on how to create a Slack app on its [official document](https://api.slack.com/start/quickstart).

### Step 2: Set up Slack in Daspire

1. Select **Slack** from the Source list.

2. Enter a **Source Name**.

3. Enter the **start_date** you want to start replicating data.

4. Enter **lookback_window** - the amount of days in the past from which you want to sync data.

5. Toggle **join_channels**, if you want to join all channels or to sync data only from channels the app is already added to. If not set, you'll need to manually add the bot to all the channels from which you'd like to sync messages.

6. Enter your **channel_filter**, this should be list of channel names (without leading `#` char) that limits the channels from which you'd like to sync. If no channels are specified, Daspire will replicate all data.

7. Enter your **Slack Bot User OAuth Access Token**.

8. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Channels (Conversations)](https://api.slack.com/methods/conversations.list)
* [Channel Members (Conversation Members)](https://api.slack.com/methods/conversations.members)
* [Messages (Conversation History)](https://api.slack.com/methods/conversations.history) -  It will only replicate messages from non-archive, public channels that the Slack App is a member of.
* [Users](https://api.slack.com/methods/users.list)
* [Threads (Conversation Replies)](https://api.slack.com/methods/conversations.replies)
* [User Groups](https://api.slack.com/methods/usergroups.list)
* [Files](https://api.slack.com/methods/files.list)
* [Remote Files](https://api.slack.com/methods/files.remote.list)

## Troubleshooting

1. The integration is restricted by [Slack requests limitation](https://api.slack.com/docs/rate-limits).

2. It is recommended to sync required channels only, this can be done by specifying config variable **channel_filter** in settings.

3. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
