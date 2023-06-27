# Manage notifications

This page provides guidance on how to manage notifications for Airbyte Cloud, allowing you to stay up-to-date on the activities in your workspace. 


## Configure Notification Settings

To set up Webhook notifications:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Notifications**.

3. Have a Slack Webhook ready if you plan to use Slack Webhook notifications. [Create an Incoming Webhook for Slack](https://api.slack.com/messaging/webhooks).

4. Toggle type of events you are interested to receive notifications. 
	1. If using slack webhooks, the webhook URL is required. For your convenience, we provide a 'test' function to send a test message to your slack channel so you can make sure it's working as expected.

5. Click **Save changes**.

## Notification Event Types

1. Failed syncs and Successful syncs: When a connection sync has finished, you can choose to be notified with if the sync has failed, successful or both. Note if sync runs frequently or if there are many syncs in the workspace these types of events can be noisy.
1. Automated Connection Updates: when a connection detects source schema has changed and can be updated automatically, Airbyte will update you connection and send you a notification message.
1. Connection Updates Requiring Action: When a connection detects some updates that requires action to run syncs. Since this will affect your sync from running as scheduled, you cannot disable the email notification for this type of event.
1. Sync Disabled and Sync disabled Warning: If a sync has been failing for multiple days or many times consecutively, we will disable the connection to prevent it run further. We will send a sync disabled warning notification when we detects the trend, and once the failure counts hits our threshold we will send a sync disabled notification and will actually disable the connection. Again, because the sync will not continue to run as you have configured, we made the decision that you cannot disable the email notification for 'Sync Disabled' event so you will always get notified.

 

## Enable schema update notifications

To get notified when your source schema changes: 
1. Make sure you have `Automatic Connection Updates` and `Connection Updates Requiring Action` turned up for desired notification channels; If these are off, even if you turned up the settings on connection settings, Airbyte Cloud will *NOT* send out any notifications related to these types of events.

2. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection you want to receive notifications for.

3. Click the **Settings** tab on the Connection page.

4. Toggle **Schema update notifications**.
