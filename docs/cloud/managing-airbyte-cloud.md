# Managing Airbyte Cloud

This page will help you manage your Airbyte Cloud workspaces and understand Airbyte Cloud limitations.

## Manage your Airbyte Cloud workspace

An Airbyte workspace allows you to collaborate with other users and manage connections under a shared billing account.

:::info
Airbyte [credits](https://airbyte.com/pricing) are assigned per workspace and cannot be transferred between workspaces.
:::

### Add users to your workspace

To add a user to your workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **Access Management**.

3. Click **+ New user**.

4. On the **Add new users** dialog, enter the email address of the user you want to invite to your workspace. 

5. Click **Send invitation**.

    :::info
    The user will have access to only the workspace you invited them to. They will be added as a workspace admin by default.
    :::

### Remove users from your workspace​

To remove a user from your workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **Access Management**.

3. Click **Remove** next to the user’s email.

4. The **Remove user** dialog displays. Click **Remove**.

### Rename a workspace

To rename a workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **General Settings**.

3. In the **Workspace name** field, enter the new name for your workspace. 

4. Click **Save changes**.

### Delete a workspace

To delete a workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **General Settings**.

3. In the **Delete your workspace** section, click **Delete**.

### Single workspace vs. multiple workspaces
 
You can use one or multiple workspaces with Airbyte Cloud. 
 
#### Access
| Number of workspaces | Benefits                                                                      | Considerations                                                                                                                              |
|----------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Single               | All users in a workspace have access to the same data.                        | If you add a user to a workspace, you cannot limit their access to specific data within that workspace.                                     |
| Multiple             | You can create multiple workspaces to allow certain users to access the data. | Since you have to manage user access for each workspace individually, it can get complicated if you have many users in multiple workspaces. | 
 
#### Billing
| Number of workspaces | Benefits                                                                      | Considerations                                                                                                                              |
|----------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Single               | You can use the same payment method for all purchases.                        | Credits pay for the use of resources in a workspace when you run a sync. Resource usage cannot be divided and paid for separately (for example, you cannot bill different departments in your organization for the usage of some credits in one workspace).                                     |
| Multiple             | Workspaces are independent of each other, so you can use a different payment method card for each workspace (for example, different credit cards per department in your organization). | You can use the same payment method for different workspaces, but each workspace is billed separately. Managing billing for each workspace can become complicated if you have many workspaces. |

### Switch between multiple workspaces

To switch between workspaces:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click the current workspace name under the Airbyte logo in the navigation bar.

2. Click **View all workspaces**.

3. Click the name of the workspace you want to switch to.

### Choose your default data residency

Default data residency allows you to choose where your data is processed.

:::note 

Configuring default data residency only applies to new connections and does not affect existing connections.   

:::

For individual connections, you can choose a data residency that is different from the default through [connection settings](#choose-the-data-residency-for-a-connection) or when you create a [new connection](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#set-up-a-connection).

:::note 

While the data is processed in a data plane in the chosen residency, the cursor and primary key data is stored in the US control plane. If you have data that cannot be stored in the US, do not use it as a cursor or primary key.

:::

To choose your default data residency:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **Data Residency**.

3. Click the dropdown and choose the location for your default data residency.

4. Click **Save changes**. 

:::info 

Depending on your network configuration, you may need to add [IP addresses](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud/#allowlist-ip-addresses) to your allowlist.   

:::

## Manage Airbyte Cloud notifications

To set up Slack notifications:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **Notifications**.

3. [Create an Incoming Webhook for Slack](https://api.slack.com/messaging/webhooks).

4. Navigate back to the Airbyte Cloud dashboard > Settings > Notifications and enter the Webhook URL.

5. Toggle the **When sync fails** and **When sync succeeds** buttons as required.

6. Click **Save changes**.

## Understand Airbyte Cloud limits

Understanding the following limitations will help you better manage Airbyte Cloud:

* Max number of workspaces per user: 100
* Max number of sources in a workspace: 100
* Max number of destinations in a workspace: 100
* Max number of connections in a workspace: 100
* Max number of streams that can be returned by a source in a discover call: 1K
* Max number of streams that can be configured to sync in a single connection: 1K
* Size of a single record: 100MB
* Shortest sync schedule: Every 60 min
* Schedule accuracy: +/- 30 min

## View the sync summary
The sync summary displays information about the data moved during a sync.
 
To view the sync summary:
1. On the [Airbyte Cloud](http://cloud.airbyte.io/) dashboard, click **Connections**.   

2. Click a connection in the list to view its sync history.

    Sync History displays the sync status or [reset](https://docs.airbyte.com/operator-guides/reset/) status (Succeeded, Partial Success, Failed, Cancelled, or Running) and the [sync summary](#sync-summary).  

    :::note 
    
    Airbyte will try to sync your data three times. After a third failure, it will stop attempting to sync.
    
    :::
    
3. To view the full sync log, click the sync summary dropdown.
 
### Sync summary

| Data                            | Description                                                                                                                                             |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| x GB (also measured in KB, MB) | Amount of data moved during the sync. If basic normalization is on, the amount of data would not change since normalization occurs in the destination.  |
| x emitted records              | Number of records read from the source during the sync.                                                                                                 |
| x committed records            | Number of records the destination confirmed it received.                                                                                                |
| xh xm xs                   | Total time (hours, minutes, seconds) for the sync and basic normalization, if enabled, to complete.                                                     | 

:::note

In a successful sync, the number of emitted records and committed records should be the same.

::: 

## Edit stream configuration

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Connections** and then click the connection you want to change.   

2. Click the **Replication** tab.

The **Transfer** and **Streams** settings include the following parameters:

| Parameter                            | Description                                                                         |
|--------------------------------------|-------------------------------------------------------------------------------------|
| Replication frequency                | How often the data syncs                                                            |
| [Non-breaking schema updates](#review-non-breaking-schema-changes) detected | How Airbyte handles syncs when it detects non-breaking schema changes in the source |
| Destination Namespace                | Where the replicated data is written                                                |
| Destination Stream Prefix            | Helps you identify streams from different connectors                                |

:::note 
    
These parameters apply to all streams in the connection.

:::

If you need to use [cron scheduling](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html):
1. In the **Replication Frequency** dropdown, click **Cron**. 
2. Enter a cron expression and choose a time zone to create a sync schedule.

:::note

* Only one sync per connection can run at a time. 
* If cron schedules a sync to run before the last one finishes, the scheduled sync will start after the last sync completes.
* Airbyte Cloud does not allow schedules that sync more than once per hour. 

:::

In the **Activate the streams you want to sync section**, you can make changes to any stream you choose.

To search for a stream:

1. Click the **Search stream name** search box. 

2. Type the name of the stream you want to find.

3. Streams matching your search are displayed in the list.

To change individual stream configuration:

![Single Edit Gif 7](https://user-images.githubusercontent.com/106352739/187313088-85c61a6d-1025-45fa-b14e-a7fe86defea4.gif)

1. In the **Sync** column of the stream, toggle the sync on or off. 

2. Click the dropdown arrow in the **Sync mode** column and select the sync mode you want to apply.

:::note 
    
Depending on the sync mode you select, you may need to choose a cursor or primary key.

:::

3. If there is a dropdown arrow in the **Cursor** or **Primary key** fields, click the dropdown arrow and choose the cursor or primary key. 

To change multiple stream configurations:

![Batch Edit gif 5](https://user-images.githubusercontent.com/106352739/187312110-d16b4f9a-9d43-4b23-b644-b64004f33b58.gif)

1. Click the first checkbox in the table header to select all streams in the connection.
    
2. Deselect the checkboxes of streams you do not want to apply these changes to.

3. In the highlighted header of the table, toggle the sync on or off. 

4. Click the dropdown arrow in the **Sync mode** column and select the sync mode you want to apply to these streams.

5. If there is a dropdown arrow in the **Cursor** or **Primary key** fields of the highlighted table header, click the dropdown arrow and choose the cursor or primary key.

6. Click **Apply** to apply these changes to the streams you selected, or click **Cancel** to discard the changes.

To save the changes:
1. Click **Save changes**, or click **Cancel** to discard the changes.

2. The **Stream configuration changed** dialog displays. This gives you the option to reset streams when you save the changes.

:::caution

Airbyte recommends that you reset streams. A reset will delete data in the destination of the affected streams and then re-sync that data. Skipping a reset is discouraged and might lead to unexpected behavior.

:::

3. Click **Save connection**, or click **Cancel** to close the dialog. 

To refresh the source schema:
1. Click **Refresh source schema** to fetch the schema of your data source.

2. If the schema has changed, the **Refreshed source schema** dialog displays them.

## Manage schema changes

Once every 24 hours, Airbyte checks for changes in your source schema and allows you to review the changes and fix breaking changes.

:::note 

Schema changes are flagged in your connection but are not propagated to your destination.
    
:::

### Review non-breaking schema changes

To review non-breaking schema changes:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection with non-breaking changes (indicated by a **yellow exclamation mark** icon).

2. Click **Review changes**.

3. The **Refreshed source schema** dialog displays the changes. 

4. Review the changes and click **OK** to close the dialog.

5. Scroll to the bottom of the page and click **Save changes**.

:::note 
    
 By default, Airbyte ignores non-breaking changes and continues syncing. You can configure how Airbyte handles syncs when it detects non-breaking changes by [editing the stream configuration](#edit-stream-configuration).
    
:::

### Fix breaking schema changes

:::note 

Breaking changes can only occur in the **Cursor** or **Primary key** fields.
    
:::

To review and fix breaking schema changes:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection with breaking changes (indicated by a **red exclamation mark** icon).

2. Click **Review changes**.

3. The **Refreshed source schema** dialog displays the changes.

4. Review the changes and click **OK** to close the dialog.

5. In the streams table, the stream with a breaking change is highlighted.

6. Fix the breaking change by selecting a new **Cursor** or **Primary key**.

7. Scroll to the bottom of the page and click **Save changes**.

:::note 
    
If a connection’s source schema has breaking changes, it will stop syncing. You must review and fix the changes before editing the connection or resuming syncs.
    
:::

### Enable schema update notifications

To get notified when your source schema changes: 
1. Make sure you have [webhook notifications](https://docs.airbyte.com/cloud/managing-airbyte-cloud#manage-airbyte-cloud-notifications) set up.

2. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection you want to receive notifications for.

3. Click the **Settings** tab on the Connection page.

4. Toggle **Schema update notifications**.

## Display Connection State

**Connection State** provides additional information about incremental syncs. It includes the most recent values for the global or stream-level cursors, which can aid in debugging or determining which data will be included in the next syncs. 

To display **Connection State**:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Settings**.

2. Click **General Settings**.

3. Toggle **Enable advanced mode** and click **Save changes**.

4. Click **Connections** in the navigation bar and then click the connection in the list you want to display.

5. Click the **Settings** tab on the Connection page.

    The **Connection State** displays.

## Choose the data residency for a connection
You can choose the data residency for your connection in the connection settings. You can also choose data residency when creating a [new connection](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#set-up-a-connection), or you can set the [default data residency](#choose-your-default-data-residency) for your workspace.

To choose the data residency for your connection: 

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click **Connections** and then click the connection that you want to change. 

2. Click the **Settings** tab. 

3. Click the **Data residency** dropdown and choose the location for your default data residency.

4. Click **Save changes**

:::note 

Changes to data residency will not affect any sync in progress. 

:::

## Manage credits

### Enroll in the Free Connector Program

The Free Connector Program allows you to sync connections with [alpha](https://docs.airbyte.com/project-overview/product-release-stages#alpha) or [beta](https://docs.airbyte.com/project-overview/product-release-stages/#beta) connectors at no cost.

:::note 
    
You must be enrolled in the program to use alpha and beta connectors for free. If either the source or destination is in alpha or beta, the whole connection is free to sync. When both the source and destination of a connection become [generally available](https://docs.airbyte.com/project-overview/product-release-stages/#general-availability-ga) (GA), the connection will no longer be free. We will email you two weeks before both connectors in a connection move to GA.
    
:::

Before enrolling in the program, [set up](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#set-up-a-source) at least one alpha or beta connector and verify your email if you haven't already.

To enroll in the program:
1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Credits** in the navigation bar.

2. Click **Enroll now** in the **Free Connector Program** banner.

3. Click **Enroll now**.

4. Input your credit card information and click **Save card**.

:::note 
    
Credit card information is required, even if you previously bought credits on Airbyte Cloud. This ensures uninterrupted syncs when both connectors move to GA.
    
:::

Since alpha and beta connectors are still in development, support is not provided. For additional resources, check out our [Connector Catalog](https://docs.airbyte.com/integrations/), [Troubleshooting & FAQ](https://docs.airbyte.com/troubleshooting/), and our [Community Slack](https://slack.airbyte.io/).

### Buy credits

This section guides you through purchasing credits on Airbyte Cloud. An Airbyte [credit](https://airbyte.com/pricing) is a unit of measure used to pay for Airbyte resources when you run a sync. 

To buy credits:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Credits** in the navigation bar.

2. If you are unsure of how many credits you need, click **Talk to Sales** to find the right amount for your team.

3. Click **Buy credits**.

4. The Stripe payment page displays. If you want to change the amount of credits, click Qty **200**. The **Update quantity** dialog displays, and you can either type the amount or use minus (**-**) or plus (**+**) to change the quantity. Click **Update**. 

    :::note 
    
    Purchase limits:
    * Minimum: 100 credits
    * Maximum: 999 credits
    
    :::

    To buy more credits or a subscription plan, reach out to [Sales](https://airbyte.com/talk-to-sales).

5. Fill out the payment information. 
    
    After you enter your billing address, sales tax is calculated and added to the total.

6. Click **Pay**.
    
    Your payment is processed. The Credits page displays the updated quantity of credits, total credit usage, and the credit usage per connection. 

    A receipt for your purchase is sent to your email. [Email us](mailto:ar@airbyte.io) for an invoice.

    :::note 
    
    Credits expire after one year if they are not used.
    
    :::
