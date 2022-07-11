# Managing Airbyte Cloud

This page will help you manage your Airbyte Cloud workspaces and understand Airbyte Cloud limitations.

## Manage your Airbyte Cloud workspace

An Airbyte Workspace allows you to collaborate with other users and manage connections under a shared billing account.

:::info
Airbyte [credits](https://airbyte.com/pricing) are assigned per workspace and cannot be transferred between workspaces.
:::

### Add users to your workspace

To add a user to your workspace:

1. On the Airbyte Cloud dashboard, click **Settings** in the left-hand navigation bar. 
2. In the Workspace Settings sidebar, click **Access Management**.
3. In the top right-hand corner, click **+ New User**.
4. On the Add new users window, enter the email address of the user you want to invite to your workspace. Click **Send invitation**.

    :::info
    The user will have access to only the workspace you invited them to. Also note that they will be added as a workspace admin by default.
    :::

### Switch between multiple workspaces

To switch between workspaces:

1. On the Airbyte Cloud dashboard, click the current workspace name under the Airbyte logo in the left-hand navigation bar.
2. Click **View all workspaces**.
3. Click the name of the workspace you want to switch to.

### Rename a workspace

To rename a workspace:

1. On the Airbyte Cloud dashboard, click **Settings** in the left-hand navigation bar. 
2. In the Workspace Settings sidebar, click **General Settings**.
3. In the Workspace name field, enter the new name for your workspace. Click **Save**.

### Delete a workspace

To delete a workspace:

1. On the Airbyte Cloud dashboard, click **Settings** in the left-hand navigation bar. 
2. In the Workspace Settings sidebar, click **General Settings**.
3. Click **Delete your workspace**.

## Manage Airbyte Cloud notifications

To set up Slack notifications:

1. On the Airbyte Cloud dashboard, click **Settings** in the left-hand navigation bar. 
2. In the Workspace Settings sidebar, click **Notifications.**
3. [Create an Incoming Webhook for Slack](https://api.slack.com/messaging/webhooks).
4. Navigate back to the Airbyte Cloud dashboard > Settings > Notifications and enter the Webhook URL. Click **Save changes**.
5. Toggle the **Send notifications when sync fails** and **Send notifications when sync succeeds** buttons as required.

## Understand Airbyte Cloud limits

Understanding the following limitations will help you better manage Airbyte Cloud:

* Max number of workspaces per user: 100
* Max number of sources in a workspace: 100
* Max number of destinations in a workspace: 100
* Max number of connection in a workspace: 100
* Max number of streams that can be returned by a source in a discover call: 1K
* Max number of streams that can be configured to sync in a single connection: 1K
* Size of a single record: 100MB
* Shortest sync schedule: Every 60 min
* Schedule accuracy: +/- 30 min

## Buy Credits

This section guides you through purchasing credits on Airbyte Cloud. An Airbyte [credit](https://docs.airbyte.com/cloud/core-concepts/#credits) is a unit of measure used to pay for Airbyte resources when you run a sync. See [Pricing](https://airbyte.com/pricing) for more information.

 To buy credits:

1. On the [Airbyte Cloud](http://cloud.airbyte.io) dashboard, click the **star icon**.
    
    The Credits page displays.

2. If you are unsure of how many credits you need, click **Talk to sales** to find the right amount for your team.

3. Click **Buy credits**. The Stripe payment page displays.

4. If you want to change the amount of credits, click Qty **200**. **Update quantity** displays, and you can either type the amount or use minus (**-**) or plus (**+**) to change the quantity. Click **Update**. 

    :::note 
    Purchase limits:
    * Minimum: 100 credits
    * Maximum: 999 credits
    :::

    To buy more credits or a subscription plan, reach out to [Sales](https://airbyte.com/talk-to-sales).

5. Fill out the payment information.

6. Click **Pay**.
    
    Your payment is processed, and the Credits page displays the updated quantity of credits, total credit usage, and the credit usage per connection. 

    A receipt for your purchase is sent to your email. [Email us](mailto:ar@airbyte.io) for an invoice.

    :::note 
    
    Credits expire after one year if they are not used.
    
    :::
