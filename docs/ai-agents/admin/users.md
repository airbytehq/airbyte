---
plan: team, custom
sidebar_position: 4
---

# Users

The Users page lets organization administrators invite people, assign roles, and manage who has access to the organization. User management is available on the [Team and Custom plans](./billing.md#team).

## View members

Open **Users** from the sidebar to see everyone in your organization. The table shows each member's name, email, role, and status. Use the search bar to filter by name or email.

Members can have one of two statuses:

- **Active**: The user has accepted their invitation and can sign in.
- **Invited**: The user has been invited but hasn't signed in yet.

## Invite users

Administrators can invite new members by email.

1. On the Users page, click **Invite Users**.
2. Enter one or more email addresses. You can type or paste multiple addresses separated by commas, semicolons, or spaces.
3. Click **Send invites**.

Invited users receive an email with a link to join the organization. Once they sign in for the first time, their status changes from **Invited** to **Active**.

## Roles

Each member has a role that determines what they can do in the organization.

| Capability | Admin | Member |
|---|---|---|
| Use Chats | Yes | Yes |
| Manage connectors in assigned workspaces | Yes | Yes |
| View all workspaces | Yes | No |
| Create, modify, and delete workspaces | Yes | No |
| Invite and remove users | Yes | No |
| Assign workspace membership | Yes | No |
| Change user roles | Yes | No |
| Configure SSO | Yes | No |
| Manage billing | Yes | No |

The first user in an organization is automatically an administrator. When you invite new users, they are added as members by default. Administrators can change a member's role at any time from the Users page using the role dropdown.

An organization must always have at least one administrator. You cannot remove or demote the last remaining admin.

## Remove a user

1. On the Users page, find the user you want to remove.
2. Click the delete icon next to their row.
3. Confirm the removal.

Removing a user revokes their access to the organization immediately. To cancel a pending invitation instead, click the delete icon next to the invited user's row.

## Workspace membership

On the Team and Custom plans, administrators control which workspaces each member can access.

- **Administrators** can see and manage every workspace in the organization, and always keep access to all of them.
- **Members** can be added to specific workspaces by an administrator, and see only the workspaces they belong to.

Everyone in the organization can access the `default` workspace. Administrators manage membership for other workspaces from the workspace picker in the sidebar: open a workspace's edit dialog and add or remove members there. For details on workspace structure and management, see [Workspaces](../concepts/architecture/workspaces.md).

## Related topics

- [Single sign-on](./sso.md): Let members sign in through your identity provider.
- [Workspaces](../concepts/architecture/workspaces.md): The isolation layer within an organization.
- [Billing and pricing](./billing.md): Plans that include user management.
