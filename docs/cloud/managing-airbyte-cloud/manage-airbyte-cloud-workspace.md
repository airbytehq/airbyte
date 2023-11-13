# Manage your workspace

An Airbyte Cloud workspace allows you to collaborate with other users and manage connections under a shared billing account.

:::info
Airbyte [credits](https://airbyte.com/pricing) are assigned per workspace and cannot be transferred between workspaces.
:::

## Add users to your workspace

To add a user to your workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Access Management**.

3. Click **+ New user**.

4. On the **Add new users** dialog, enter the email address of the user you want to invite to your workspace. 

5. Click **Send invitation**.

    :::info
    The user will have access to only the workspace you invited them to. They will be added as a workspace admin by default.
    :::

## Remove users from your workspace​

To remove a user from your workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Access Management**.

3. Click **Remove** next to the user’s email.

4. The **Remove user** dialog displays. Click **Remove**.

## Rename a workspace

To rename a workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **General Settings**.

3. In the **Workspace name** field, enter the new name for your workspace. 

4. Click **Save changes**.

## Delete a workspace

To delete a workspace:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **General Settings**.

3. In the **Delete your workspace** section, click **Delete**.

## Single workspace vs. multiple workspaces
 
You can use one or multiple workspaces with Airbyte Cloud, which gives you flexibility in managing user access and billing.
 
### Access
| Number of workspaces | Benefits                                                                      | Considerations                                                                                                                              |
|----------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Single               | All users in a workspace have access to the same data.                        | If you add a user to a workspace, you cannot limit their access to specific data within that workspace.                                     |
| Multiple             | You can create multiple workspaces to allow certain users to access the data. | Since you have to manage user access for each workspace individually, it can get complicated if you have many users in multiple workspaces. | 
 
### Billing
| Number of workspaces | Benefits                                                                      | Considerations                                                                                                                              |
|----------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Single               | You can use the same payment method for all purchases.                        | Credits pay for the use of resources in a workspace when you run a sync. Resource usage cannot be divided and paid for separately (for example, you cannot bill different departments in your organization for the usage of some credits in one workspace).                                     |
| Multiple             | Workspaces are independent of each other, so you can use a different payment method card for each workspace (for example, different credit cards per department in your organization). | You can use the same payment method for different workspaces, but each workspace is billed separately. Managing billing for each workspace can become complicated if you have many workspaces. |

## Switch between multiple workspaces

To switch between workspaces:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click the current workspace name under the Airbyte logo in the navigation bar.

2. Click **View all workspaces**.

3. Click the name of the workspace you want to switch to.
