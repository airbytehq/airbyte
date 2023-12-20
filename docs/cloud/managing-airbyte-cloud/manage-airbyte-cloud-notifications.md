---
products: all
---

# Manage notifications

This page provides guidance on how to manage notifications for Airbyte, allowing you to stay up-to-date on the activities in your workspace. 

## Notification Event Types

| Type of Notification   | Description                                                                                                         |
|------------------------|---------------------------------------------------------------------------------------------------------------------|
| Failed Syncs                          | A sync from any of your connections fails. Note that if sync runs frequently or if there are many syncs in the workspace these types of events can be noisy            |
| Successful Syncs                      | A sync from any of your connections succeeds. Note that if sync runs frequently or if there are many syncs in the workspace these types of events can be noisy
| Automated Connection Updates          | A connection is updated automatically (ex. a source schema is automatically updated)              |
| Connection Updates Requiring Action   | A connection update requires you to take action (ex. a breaking schema change is detected)                |
| Warning - Repeated Failures                 | A connection will be disabled soon due to repeated failures. It has failed 50 times consecutively or there were only failed jobs in the past 7 days               |
| Sync Disabled - Repeated Failures                         | A connection was automatically disabled due to repeated failures. It will be disabled when it has failed 100 times consecutively or has been failing for 14 days in a row               |
| Warning - Upgrade Required (Cloud only)                         |       A new connector version is available and requires manual upgrade       |
| Sync Disabled - Upgrade Required (Cloud only)                         |   One or more connections were automatically disabled due to a connector upgrade deadline passing

## Configure Email Notification Settings

<AppliesTo cloud />

To set up email notifications:

1. In the Airbyte UI, click **Settings** and navigate to **Notifications**.

2. Toggle which messages you'd like to receive from Airbyte. All email notifications will be sent by default to the creator of the workspace. To change the recipient, edit and save the **notification email recipient**. If you would like to send email notifications to more than one recipient, you can enter an email distribution list (ie Google Group) as the recipient.

3. Click **Save changes**.

:::note
All email notifications except for Successful Syncs are enabled by default. 
:::

## Configure Slack Notification settings

To set up Slack notifications:

If you're more of a visual learner, just head over to [this video](https://www.youtube.com/watch?v=NjYm8F-KiFc&ab_channel=Airbyte) to learn how to do this. You can also refer to the Slack documentation on how to [create an incoming webhook for Slack](https://api.slack.com/messaging/webhooks).

### Create a Slack app

1. **Create a Slack App**: Navigate to https://api.slack.com/apps/. Select `Create an App`. 

![](../../.gitbook/assets/notifications_create_slack_app.png)   

2. Select `From Scratch`. Enter your App Name (e.g. Airbyte Sync Notifications) and pick your desired Slack workspace. 

3. **Set up the webhook URL.**: in the left sidebar, click on `Incoming Webhooks`.  Click the slider button in the top right to turn the feature on. Then click `Add New Webhook to Workspace`.

![](../../.gitbook/assets/notifications_add_new_webhook.png)

4. Pick the channel that you want to receive Airbyte notifications in (ideally a dedicated one), and click `Allow` to give it permissions to access the channel. You should see the bot show up in the selected channel now. You will see an active webhook right above the `Add New Webhook to Workspace` button.

![](../../.gitbook/assets/notifications_webhook_url.png) 

5. Click `Copy.` to copy the link to your clipboard, which you will need to enter into Airbyte.

Your Webhook URL should look something like this:

![](../../.gitbook/assets/notifications_airbyte_notification_settings.png)


### Enable the Slack notification in Airbyte

1. In the Airbyte UI, click **Settings** and navigate to **Notifications**.

2. Paste the copied webhook URL to `Webhook URL`. Using a Slack webook is recommended. On this page, you can toggle each slider decide whether you want notifications on each notification type. 

3. **Test it out.**: you can click `Test` to send a test message to the channel. Or, just run a sync now and try it out! If all goes well, you should receive a notification in your selected channel that looks like this:

![](../../.gitbook/assets/notifications_slack_message.png)

You're done!

4. Click **Save changes**.

## Enable schema update notifications

To be notified of any source schema changes: 
1. Make sure you have enabled `Automatic Connection Updates` and `Connection Updates Requiring Action` notifications. If these are off, even if you turned on schema update notifications in a connection's settings, Airbyte will *NOT* send out any notifications related to these types of events.

2. In the Airbyte UI, click **Connections** and select the connection you want to receive notifications for.

3. Click the **Settings** tab on the Connection page.

4. Toggle **Schema update notifications**.
