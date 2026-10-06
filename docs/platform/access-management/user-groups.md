---
products: cloud-teams
---

# User groups

A user group is a named set of organization members. You can grant a group a permission, and every member gets that permission.

User groups are available when SCIM provisioning is enabled. To learn how SCIM manages users and groups, see [SCIM provisioning](scim).

## How user groups work with SCIM

Your identity provider owns group names and membership. Airbyte owns the permissions assigned to a group.

| Group information | Owner |
| --- | --- |
| Group name | Your identity provider |
| Group membership | Your identity provider |
| Group permissions | Airbyte |

SCIM cannot assign Airbyte permissions. An organization admin assigns permissions to groups in Airbyte.

While SCIM is enabled, you can't rename a group, change its membership, or delete it in Airbyte. Make those changes in your identity provider instead.

:::warning
Your identity provider can't adopt an existing Airbyte group with the same name. Provisioning for that group fails with a `409` response until you rename or delete the Airbyte group.

Before SCIM provisioning starts, review and delete or rename any pre-existing Airbyte groups that your IdP should provision. See [Enable SCIM in Airbyte](scim#enable-scim-in-airbyte) for the full guidance.
:::

## Open user groups

The **User Groups** page is available when SCIM provisioning is enabled and you can manage organization permissions.

1. In Airbyte, click **Organization settings** > **User Groups**.

2. Search for a group, or select a group to view its members.

The page shows each group's name and member count. It is read-only for group names and membership.

## Assign permissions to a group

An organization admin can assign permissions to a group at either of these scopes:

- The organization
- One workspace

A group permission has exactly one scope. You can't assign the same permission to both an organization and a workspace in one permission entry.

1. Open a group from **User Groups**.

2. Edit the group's organization permissions or workspace permissions.

3. Save the permission changes.

<!-- Confirm the exact Edit permissions flow once PLAT-1118 ships -->

## How permissions combine

A person's effective access is the highest permission from their individual permissions and all the groups they belong to. The person must also be an organization member for group permissions to apply.

If you remove someone from a group, they lose any access they had only through that group. Their individual permissions are not changed.

For more information about roles and permissions, see [role-based access control](rbac).
