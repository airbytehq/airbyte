## Prerequisites
- Access to Slack via OAuth or API Token (via Slack App or Legacy API Key)


## Setup Guide

1. Enter a name for your connector
2. Select `Authenticate your Slack account` (preferred) and authorize into the Slack account. To use an API token instead, see the instructions below on creating one.
3. Toggle on **Join all channels** (recommended) to join all channels the user has access to or to sync data only from channels the app (if using API token) is already in. If false, you'll need to manually add all the channels from which you'd like to sync messages.
4. (Optional) Enter a **Threads Lookback Window (Days)** to set how far back to look for messages in threads from when each sync start.
5. (Optional) Enter a **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. Data created on and after this date will be replicated.
8. (Optional) Enter your `Channel name filter` to filter the list of channels Airbyte can access. If none are entered, Airbyte will sync all channels. It can be helpful to only sync required channels to avoid Slack's [requests limits](https://api.slack.com/docs/rate-limits).


9. Click **Set up source**.

### Creating an API token

You can no longer create "Legacy" API Keys, but if you already have one, you can use it with this source as the API key and skip setting up an application.

In order to pull data out of your Slack instance, you need to create a Slack App. This may sound daunting, but it is actually pretty straight forward. Slack supplies [documentation](https://api.slack.com/start) on how to build apps. Feel free to follow that if you want to do something fancy. We'll describe the steps we followed to creat the Slack App for this tutorial.

:::info
This tutorial assumes that you are an administrator on your slack instance. If you are not, you will need to coordinate with your administrator on the steps that require setting permissions for your app.
:::

1. Go to the [apps page](https://api.slack.com/apps)
2. Click "Create New App"
3. It will request a name and the slack instance you want to create the app for. Make sure you select the instance form which you want to pull data.
4. Completing that form will take you to the "Basic Information" page for your app.
5. Now we need to grant the correct permissions to the app. \(This is the part that requires you to be an administrator\). Go to "Permissions". Then under "Bot Token Scopes" click on "Add an OAuth Scope". We will now need to add the following scopes:

   ```text
    channels:history
    channels:join
    channels:read
    files:read
    groups:read
    links:read
    reactions:read
    remote_files:read
    team:read
    usergroups:read
    users.profile:read
    users:read
   ```

   This may look daunting, but the search functionality in the dropdown should make this part go pretty quick.

6. Scroll to the top of the page and click "Install to Workspace". This will generate a "Bot User OAuth Access Token". We will need this in a moment.
7. Now go to your slack instance. For any public channel go to info =&gt; more =&gt; add apps. In the search bar search for the name of your app. \(If using the desktop version of slack, you may need to restart Slack for it to pick up the new app\). Airbyte will only replicate messages from channels that the Slack bot has been added to.

   ![](../../.gitbook/assets/slack-add-apps.png)

8. In Airbyte, create a Slack source. The "Bot User OAuth Access Token" from the earlier should be used as the token.
9. You can now pull data from your slack instance!

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Slack](https://docs.airbyte.com/integrations/sources/slack).
