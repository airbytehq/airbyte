---
products: cloud, oss-enterprise
---

# Manage your workspace

A workspace in Airbyte allows you to collaborate with other users and manage connections together.

## Add users to your workspace

1. To add a user to your workspace, go to the **Settings** via the side navigation in Airbyte. Navigate to **Workspace** > **General** and click **+ New member**.

2. On the **Add new member** dialog, enter the email address of the user you want to invite to your workspace. Click **Add new member**.

:::info
The user will have access to only the workspace you invited them to. They will be added with a role of `Workspace Admin`, which has the ability to add or delete other users and make changes to connections and connectors in the workspace.
:::

## Remove users from your workspace​

1. To remove a user from your workspace, to the **Settings** via the side navigation in Airbyte. Navigate to **Workspace** > **General**. In the workspace role column, click the down carat and select **Remove user**.

2. Complete removal by clicking **Remove** in the confirmation modal.

:::tip
Organization admins cannot be removed from a workspace. Reach out to Airbyte Support if you need assistance removing an organization admin.
:::

## Rename a workspace

To rename a workspace, go to the **Settings** via the side navigation in Airbyte. Navigate to **Workspace** > **General**. In the **Workspace name** field, enter the new name for your workspace. Click **Save changes**.

## Delete a workspace

To delete a workspace, go to the **Settings** via the side navigation in Airbyte. Navigate to **Workspace** > **General**. In the **Danger!** section, click **Delete your workspace**.

## Managing multiple workspaces

You can have access to one or multiple workspaces with Airbyte Cloud, which gives you flexibility in managing user access and billing. Workspaces can also be linked through an organization, which allows you to collaborate with team members and share workspaces across your team.

:::info
Organizations are only available in Airbyte Cloud through Cloud Teams. [Get in touch](https://airbyte.com/company/talk-to-sales) with us if you would like to take advantage of organization features.
:::

### Billing across multiple workspaces

Airbyte [credits](https://airbyte.com/pricing) are by default assigned per workspace and cannot be transferred between workspaces. [Get in touch](https://airbyte.com/company/talk-to-sales) with us if you would like to centralize billing across workspaces.

## Managing User Roles

Airbyte offers multiple user roles to enable teams to securely access workspaces or organizations. All roles are available to Cloud Teams and Self-Managed Enterprise users. Cloud users only have admin roles.

| Role                                                                                                                    | Cloud | Cloud Teams | Enterprise |
| ----------------------------------------------------------------------------------------------------------------------- | ----- | ----------- | ---------- |
| **Organization Admin:** Administer the whole organization, create workspaces in it, and manage organization permissions |   ✅    | ✅          | ✅         |
| **Workspace Admin:** Administer the workspace, create workspace permissions                                             | ✅    |      ✅       |    ✅        |
| **Workspace Reader:** View information within a workspace, cannot modify anything within a workspace                    |       | ✅          | ✅         |


More information about specific roles can be found in our [Role-Based Access Control documentation](../access-management/rbac.md).

## Switch between multiple workspaces

To switch between workspaces, click the current workspace name under the Airbyte logo in the navigation bar. Search for the workspace or click the name of the workspace you want to switch to.
