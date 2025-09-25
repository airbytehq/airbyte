---
products: cloud, oss-enterprise
---

# Manage workspaces

You can create, manage, and delete workspaces, and control access to them.

## Create a new workspace

Organization admins and readers can create workspaces. Follow these steps to create a new workspace.

1. Go to your Organization home page.

2. Click **New workspace**.

3. Enter a workspace name and select a [region](/platform/cloud/managing-airbyte-cloud/manage-data-residency).

4. Click **Create workspace**. Airbyte creates a new, empty workspace.

## Rename a workspace

Workspace admins can rename workspaces. Follow these steps to rename a workspace.

1. [Switch](#switch-workspaces) to the workspace you want to rename.

2. Click **Workspace settings** > **General**.

3. Under **Workspace name**, type the new name.

4. Click **Save changes**. Airbyte renames your workspace.

## Delete a workspace

Organizations admins and editors, and workspace admins, can delete a workspace. Follow these steps to delete a workspace.

:::danger
Deleting a workspace deletes all its sources, destinations, and connections. This is irreversible. Think carefully before doing this.
:::

1. [Switch](#switch-workspaces) to the workspace you want to delete.

2. Click **Workspace settings** > **General**.

3. Click **Delete your workspace**.

4. Type your workspace name to confirm you want to delete it.

5. Click **Delete workspace**. Airbyte permanently deletes your workspace.

## Add users to your workspace

Workspace admins can add any organization member to a workspace.

1. [Switch](#switch-workspaces) to the workspace you want to add them to.

2. Click **Workspace settings** > **Members**.

3. Click **New member**.

4. Start entering the person's name or email to find them in the list.

5. Click their name to select them, then assign them an [RBAC](../access-management/rbac) role.

6. Click **Add new member**.

## Remove someone from your workspace​

Workspace admins can remove someone from a workspace, but can't remove other workspace admins. Follow these steps to remove someone from your workspace.

1. [Switch](#switch-workspaces) to the workspace you want to remove them from.

2. Click **Workspace settings** > **Members**.

3. Find the person you want to remove, click the role next to their name, and select **Remove user from workspace**.

## Switch between workspaces {#switch-workspaces}

If you have multiple workspaces in the same organization, you can switch between them. Any workspace reader, runner, editor, or admin can open a workspace.

1. In the navigation bar, under **Workspace**, click the dropdown with your current workspace name.

2. Find and click the name of the workspace you want to switch to. Airbyte switches to that workspace.

## Managing roles

See [Role based access control](../access-management/rbac) to learn more about the different roles available. If you're on the Cloud Standard plan, all users are admins.
