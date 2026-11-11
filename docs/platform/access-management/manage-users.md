---
products: cloud
---

# Manage users and permissions

This page explains who can manage users in Airbyte Cloud, which roles are available on each plan, and what organization admins and workspace admins can do. For step-by-step instructions on a specific feature, follow the links in [Related pages](#related-pages).

## What's available on each plan

| Capability                               | Standard                              | Plus                                  | Pro                 | Enterprise Flex     |
| :--------------------------------------- | :------------------------------------ | :------------------------------------ | :------------------ | :------------------ |
| Invite users                             | Yes                                   | Yes                                   | Yes                 | Yes                 |
| Role a new user gets                     | Workspace admin or organization admin | Workspace admin or organization admin | Any role you choose | Any role you choose |
| Change a user's role                     | No                                    | No                                    | Yes                 | Yes                 |
| [Role-based access control (RBAC)](rbac) | No                                    | No                                    | Yes                 | Yes                 |
| [User groups](user-groups)               | No                                    | No                                    | Yes                 | Yes                 |
| [Single sign-on (SSO)](sso)              | No<sup>1</sup>                        | Yes                                   | Yes                 | Yes                 |
| [SCIM provisioning](scim)                | No                                    | No                                    | Yes                 | Yes                 |

<sup>1</sup> If your Standard organization already uses SSO, you keep it as long as you remain a paying customer.

For workspace limits and other plan differences, see [Airbyte Cloud limits](../cloud/managing-airbyte-cloud/understand-airbyte-cloud-limits) and [Airbyte's pricing page](https://airbyte.com/pricing).

## Organization admins and workspace admins

Airbyte has two levels of access. An [organization](../organizations-workspaces/) contains one or more [workspaces](../organizations-workspaces/workspaces/).

- **Organization admins** have full control of the organization and every workspace in it. They can manage organization settings and billing, create workspaces, and add, remove, and change the roles of users at the organization level.

- **Workspace admins** have full control of a single workspace. They can manage its sources, destinations, connections, and settings, and add, remove, and change the roles of users in that workspace. A workspace admin can't change organization settings or manage users at the organization level.

An organization role applies to every workspace in the organization. A workspace role can raise someone's access in one workspace, but it can't lower it below their organization role. Because of this, an organization admin is always an admin of every workspace. You can't demote or remove an organization admin from a single workspace.

## Standard and Plus plans

Standard and Plus don't include RBAC. Every user is an admin.

- When you invite someone to a workspace, they become a workspace admin of that workspace.

- When you invite someone to the organization, they become an organization admin.

- You can't change a user's role after they join.

- You can remove a workspace admin from the workspace.

- You can't demote an organization admin, and you can't remove one from a single workspace. Another organization admin must remove them from the organization. You can't remove yourself.

If you need someone to have access to one workspace only, invite them to that workspace, not to the organization. To reduce the access of an organization admin, remove them from the organization, then invite them to the workspace they need.

To assign roles with less access, such as reader or editor, upgrade to Pro or Enterprise Flex.

## Pro and Enterprise Flex plans

Pro and Enterprise Flex include RBAC. Organization admins and workspace admins can assign any [organization or workspace role](rbac) to users and [user groups](user-groups). Assign the lowest role each person needs, because once someone is an organization admin, you can't demote them.

If you use [SCIM provisioning](scim), your identity provider controls who belongs to the organization and to each user group. You still assign roles in Airbyte.

## What happens to roles when you downgrade

If your organization moves from a plan with RBAC to a plan without it, Airbyte converts every user who isn't an organization admin, and every pending invitation, to a workspace admin of your organization's default workspace. Organization admins remain organization admins.

Before you downgrade, review your organization's users and remove anyone who shouldn't keep admin access.

## Related pages

- [Manage workspaces](../using-airbyte/workspaces)
- [Role-based access control (RBAC)](rbac)
- [User groups](user-groups)
- [Single sign-on (SSO)](sso)
- [SCIM provisioning](scim)
- [Airbyte Cloud limits](../cloud/managing-airbyte-cloud/understand-airbyte-cloud-limits)
