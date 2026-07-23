---
plan: all
sidebar_position: 4
---

# Governance

Governance is how you control what your agents, and the people who build them, can reach. As you connect more systems and add more people to an organization, you take on more risk: a broad credential, a shared workspace, or an over-permissioned teammate can expose data an agent shouldn't access. Governance is the umbrella term for the controls that mitigate that risk by narrowing access to only what each agent and person needs.

Airbyte Agents gives you multiple layers of control, and most organizations combine them: workspaces to separate credentials, roles to separate people, and entity access to fine-tune what each member can reach through a connector.

## Workspaces

A [workspace](./architecture/workspaces.md) is an isolation boundary within an organization. Each workspace holds its own connectors and credentials, and a token scoped to one workspace can't reach another. Use workspaces to separate tenants, teams, or environments so that access to one set of credentials doesn't imply access to the rest. Multiple workspaces are available on the Team and Custom plans.

## User roles and permissions

Every member of an organization has a role, either **Admin** or **Member**, that determines what they can do. Admins manage workspaces, users, billing, and organization settings; members work within the workspaces they're assigned to. Assigning the right role, and adding members only to the workspaces they need, keeps administrative and data access scoped to the people who require it. See [Users](../admin/users.md) for roles and workspace membership. User management is available on the Team and Custom plans.

## Entity access permissions

Within a single connector, [entity access permissions](../interfaces/ui/add-connector.md#entity-access) let administrators control which members can read from and write to each entity the connector exposes. This is the finest-grained layer: it applies per entity, per member, and per action, so you can share a connector while still keeping a sensitive entity, such as payroll or customer contacts, limited to the people who should reach it.

## Related controls

Other features support governance by controlling how people authenticate and where requests can originate:

- [**Single sign-on (SSO)**](../admin/sso.md): Let members sign in through your identity provider instead of individual passwords. Available on the Team and Custom plans.
- [**IP allow list**](../admin/ip-allowlist.md): Restrict the IP addresses that traffic to your organization can use.
