# Manage notifications

This page provides guidance on how to manage notifications for Airbyte Cloud, allowing you to stay up-to-date on the activities in your workspace. 


## Configure Notification Settings

To set up Webhook notifications:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Notifications**.

3. Have a webhook URL ready if you plan to use webhook notifications. Using a Slack webook is recommended. [Create an Incoming Webhook for Slack](https://api.slack.com/messaging/webhooks).

4. Toggle the type of events you are interested to receive notifications for. 
	1. To enable webhook notifications, the webhook URL is required. For your convenience, we provide a 'test' function to send a test message to your webhook URL so you can make sure it's working as expected.

5. Click **Save changes**.

## Notification Event Types

1. Failed syncs and successful syncs: When a connection sync has finished, you can choose to be notified whether the sync has failed, succeeded or both. Note that if sync runs frequently or if there are many syncs in the workspace these types of events can be noisy.
1. Automated Connection Updates: when Airbyte detects that the connection's source schema has changed and can be updated automatically, Airbyte will update your connection and send you a notification message.
1. Connection Updates Requiring Action: When Airbyte detects some updates that requires your action to run syncs. Since this will affect your sync from running as scheduled, you cannot disable this type of email notification.
1. Sync Disabled and Sync Disabled Warning: If a sync has been failing for multiple days or many times consecutively, Airbyte will disable the connection to prevent it from running further. Airbyte will send a Sync Disabled Warning notification when we detect the trend, and once the failure counts hits a threshold Airbyte will send a Sync Disabled notification and will actually disable the connection. Again, because the sync will not continue to run as you have configured, the Sync Disabled notification cannot be disabled.

 

## Enable schema update notifications

To get notified when your source schema changes: 
1. Make sure you have `Automatic Connection Updates` and `Connection Updates Requiring Action` turned on for your desired notification channels; If these are off, even if you turned on schema update notifications in a connection's settings, Airbyte will *NOT* send out any notifications related to these types of events.

2. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection you want to receive notifications for.

3. Click the **Settings** tab on the Connection page.

4. Toggle **Schema update notifications**.
