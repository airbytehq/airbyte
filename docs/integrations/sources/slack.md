# Slack

## Sync overview

This source can sync data for the [Slack API](https://api.slack.com/). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Singer Tap](https://github.com/singer-io/tap-slack).

### Output schema

This Source is capable of syncing the following core Streams:

* [Channels \(Conversations\)](https://api.slack.com/methods/conversations.list)
* [Channel Members \(Conversation Members\)](https://api.slack.com/methods/conversations.members)
* [Messages \(Conversation History\)](https://api.slack.com/methods/conversations.history) It will only replicate messages from non-archive, public channels that the Slack App is a member of.
* [Users](https://api.slack.com/methods/users.list)
* [Threads \(Conversation Replies\)](https://api.slack.com/methods/conversations.replies)
* [User Groups](https://api.slack.com/methods/usergroups.list)
* [Files](https://api.slack.com/methods/files.list)
* [Remote Files](https://api.slack.com/methods/files.remote.list)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |

### Performance considerations

The connector is restricted by normal Slack [requests limitation](https://api.slack.com/docs/rate-limits).

The Slack connector should not run into Slack API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Slack API Token 

### Setup guide

{% hint style="info" %}
If you are using an "legacy" Slack API, skip to the Legacy API Key section below.
{% endhint %}

In order to pull data out of your Slack instance, you need to create a Slack App. This may sound daunting, but it is actually pretty straight forward. Slack supplies [documentation](https://api.slack.com/start) on how to build apps. Feel free to follow that if you want to do something fancy. We'll describe the steps we followed to creat the Slack App for this tutorial.

{% hint style="info" %}
This tutorial assumes that you are an administrator on your slack instance. If you are not, you will need to coordinate with your administrator on the steps that require setting permissions for your app.
{% endhint %}

1. Go to the [apps page](https://api.slack.com/apps)
1. Click "Create New App"
1. It will request a name and the slack instance you want to create the app for. Make sure you select the instance form which you want to pull data.
1. Completing that form will take you to the "Basic Information" page for your app.
1. Now we need to grant the correct permissions to the app. (This is the part that requires you to be an administrator). Go to "Permissions". Then under "Bot Token Scopes" click on "Add an OAuth Scope". We will now need to add the following scopes:
    ```
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
1. Scroll to the top of the page and click "Install to Workspace". This will generate a "Bot User OAuth Access Token". We will need this in a moment.
1. Now go to your slack instance. For any public channel go to info => more => add apps. In the search bar search for the name of your app. (If using the desktop version of slack, you may need to restart Slack for it to pick up the new app).
![](../../.gitbook/assets/slack-add-apps.png)
1. In airbyte, create a Slack source. The "Bot User OAuth Access Token" from the earlier should be used as the token.
1. You can now pull data from your slack instance!

### Setup guide (Legacy API Key)

You can no longer create "Legacy" API Keys, but if you already have one, you can use it with this source. Fill it into the API key section.

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.
